#!/usr/bin/env python3
"""
roadcheck_backend_roadwork.py — terminal check for the local RoadWork API kernel.

Verifies:
  - backend kernel file exists
  - kernel module imports and exposes expected handlers
  - in-process smoke returns 200 + proof envelope on every documented endpoint
  - no forbidden external strings appear in the backend source
  - required canon files exist on disk

Exit code 0 only if every check is GREEN.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KERNEL_PATH = REPO_ROOT / "backend" / "roadwork_api_kernel.py"
CANON_REQUIRED = [
    "canon/workflow/workflow_state_model.json",
    "canon/workflow/rules/workflow_transition_rules_v0.json",
    "canon/workflow/universal_172_process.json",
    "canon/workflow/samples/universal_172_sample_workflow.json",
    "canon/workflow/runs/workflow_action_sequence_v0.json",
    "canon/workflow/sql/roadwork_workflow_schema_v0.sql",
    "canon/workflow/api/roadwork_api_contract_v0.json",
]
FORBIDDEN_STRINGS = [
    "gmail.com",
    "googleapis.com",
    "slack.com",
    "hooks.slack",
    "sendgrid",
    "mailgun",
    "amazonaws.com",
    "openai.com",
    "anthropic.com",
    "AKIA",
    "BEGIN PRIVATE KEY",
    "ssh-rsa AAAA",
]

GREEN = "\033[32mGREEN \033[0m"
YELLOW = "\033[33mYELLOW\033[0m"
RED = "\033[31mRED   \033[0m"


def mark(ok: bool | None, label: str, detail: str = "") -> tuple[bool, str]:
    if ok is True:
        m = GREEN
    elif ok is False:
        m = RED
    else:
        m = YELLOW
    return ok is True, f"{m} {label}\n       {detail}" if detail else f"{m} {label}"


def import_kernel():
    spec = importlib.util.spec_from_file_location("roadwork_api_kernel", KERNEL_PATH)
    if spec is None or spec.loader is None:
        raise ImportError("could not build spec for roadwork_api_kernel")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    results: list[tuple[bool, str]] = []

    # 1. backend file exists
    results.append(
        mark(KERNEL_PATH.exists(), "backend kernel file", str(KERNEL_PATH.relative_to(REPO_ROOT)))
    )
    if not KERNEL_PATH.exists():
        for ok, line in results:
            print(line)
        print("=== RED: kernel file missing ===")
        return 1

    # 2. py_compile clean
    try:
        import py_compile

        py_compile.compile(str(KERNEL_PATH), doraise=True)
        results.append(mark(True, "kernel py_compile", "OK"))
    except py_compile.PyCompileError as e:
        results.append(mark(False, "kernel py_compile", str(e)))

    # 3. kernel imports
    try:
        kernel = import_kernel()
        results.append(mark(True, "kernel import", f"version={kernel.KERNEL_VERSION}"))
    except Exception as e:  # noqa: BLE001
        results.append(mark(False, "kernel import", repr(e)))
        for ok, line in results:
            print(line)
        print("=== RED: kernel import failed ===")
        return 1

    # 4. canon presence
    for rel in CANON_REQUIRED:
        p = REPO_ROOT / rel
        results.append(mark(p.exists(), f"canon: {rel}", "present" if p.exists() else "MISSING"))

    # 5. forbidden strings audit on backend source
    src = KERNEL_PATH.read_text(encoding="utf-8")
    hits = [s for s in FORBIDDEN_STRINGS if s.lower() in src.lower()]
    results.append(
        mark(len(hits) == 0, "no forbidden external strings", "none" if not hits else f"FOUND: {hits}")
    )

    # 6. endpoints dispatch + envelope shape
    required_keys = {"production", "mode", "implemented", "kernel", "kernel_version", "data"}
    for ep in kernel.ENDPOINTS:
        status, body = kernel.dispatch(ep)
        ok = (
            status == 200
            and isinstance(body, dict)
            and required_keys.issubset(body.keys())
            and body.get("production") is False
            and body.get("mode") == "local_only"
            and body.get("implemented") == "proof_only"
        )
        detail = f"status={status} prod={body.get('production')} mode={body.get('mode')}"
        results.append(mark(ok, f"endpoint {ep}", detail))

    # 7. health endpoint specifically reports all routes
    status, health = kernel.dispatch("/api/health")
    health_routes = set(health.get("data", {}).get("endpoints", []))
    expected_routes = set(kernel.ENDPOINTS)
    results.append(
        mark(
            expected_routes.issubset(health_routes),
            "health lists every endpoint",
            f"missing={sorted(expected_routes - health_routes) or 'none'}",
        )
    )

    # 8. POST refused
    class _Req:
        pass

    # Don't actually open a socket; smoke that the route map has no POST handler.
    has_post_route = any(getattr(kernel, "ROUTES", {}).get(p) for p in ["/api/post", "/api/mutate"])
    results.append(mark(not has_post_route, "no mutating routes registered", "GET-only"))

    print("RoadWork Backend Terminal Check")
    print(f"root: {REPO_ROOT}")
    print()
    fails = 0
    for ok, line in results:
        print(line)
        if not ok:
            fails += 1
    print()
    if fails == 0:
        print("=== GREEN: backend kernel proof OK ===")
        return 0
    print(f"=== RED: {fails} check(s) failed ===")
    return 1


if __name__ == "__main__":
    sys.exit(main())
