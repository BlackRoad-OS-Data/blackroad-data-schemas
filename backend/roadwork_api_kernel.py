#!/usr/bin/env python3
"""
RoadWork Local API Kernel v0 (proof_only)

Mode: local_only, 127.0.0.1 only, no external API, no secrets, no database server.
Reads canon JSON / SQL / sample files from the repo working tree and serves
them over a stdlib http.server. Intended for terminal-verifiable smoke checks
of the workflow canon, not production traffic.

Hard rules embedded in the proof contract:
  production: false
  mode: local_only
  implemented: proof_only

Run:
  python3 backend/roadwork_api_kernel.py            # serve on 127.0.0.1:8790
  python3 backend/roadwork_api_kernel.py --smoke    # in-process endpoint check
  python3 backend/roadwork_api_kernel.py --port N   # alternate port
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
CANON = REPO_ROOT / "canon"
RECEIPTS = REPO_ROOT / "receipts"

KERNEL_NAME = "roadwork_api_kernel"
KERNEL_VERSION = "0.1.0"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8790

CANON_FILES = {
    "state_model": CANON / "workflow" / "workflow_state_model.json",
    "rules": CANON / "workflow" / "rules" / "workflow_transition_rules_v0.json",
    "universal_172": CANON / "workflow" / "universal_172_process.json",
    "sample": CANON / "workflow" / "samples" / "universal_172_sample_workflow.json",
    "actions": CANON / "workflow" / "runs" / "workflow_action_sequence_v0.json",
    "schema_sql": CANON / "workflow" / "sql" / "roadwork_workflow_schema_v0.sql",
    "api_contract": CANON / "workflow" / "api" / "roadwork_api_contract_v0.json",
}

ENDPOINTS = [
    "/api/health",
    "/api/workflow/status",
    "/api/workflow/schema",
    "/api/workflow/rules",
    "/api/workflow/templates/universal-172",
    "/api/workflow/sample",
    "/api/workflow/actions",
    "/api/workflow/receipts/recent",
]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def envelope(payload, *, source: str | None = None, extra: dict | None = None) -> dict:
    body = {
        "production": False,
        "mode": "local_only",
        "implemented": "proof_only",
        "kernel": KERNEL_NAME,
        "kernel_version": KERNEL_VERSION,
        "served_at_utc": utcnow(),
        "data": payload,
    }
    if source is not None:
        body["source"] = source
    if extra:
        body.update(extra)
    return body


def handler_health() -> dict:
    canon_present = {k: v.exists() for k, v in CANON_FILES.items()}
    return envelope(
        {
            "status": "ok",
            "endpoints": ENDPOINTS,
            "canon_present": canon_present,
            "repo_root": str(REPO_ROOT),
        }
    )


def handler_workflow_status() -> dict:
    data = load_json(CANON_FILES["state_model"])
    return envelope(
        {
            "statuses": data.get("statuses", []),
            "state_model_name": data.get("name"),
            "state_model_version": data.get("version"),
        },
        source=str(CANON_FILES["state_model"].relative_to(REPO_ROOT)),
    )


def handler_workflow_schema() -> dict:
    sql_text = load_text(CANON_FILES["schema_sql"])
    return envelope(
        {
            "schema_sql": sql_text,
            "schema_sql_lines": sql_text.count("\n") + 1,
            "schema_sql_bytes": len(sql_text.encode("utf-8")),
        },
        source=str(CANON_FILES["schema_sql"].relative_to(REPO_ROOT)),
    )


def handler_workflow_rules() -> dict:
    data = load_json(CANON_FILES["rules"])
    return envelope(data, source=str(CANON_FILES["rules"].relative_to(REPO_ROOT)))


def handler_workflow_universal_172() -> dict:
    data = load_json(CANON_FILES["universal_172"])
    return envelope(data, source=str(CANON_FILES["universal_172"].relative_to(REPO_ROOT)))


def handler_workflow_sample() -> dict:
    data = load_json(CANON_FILES["sample"])
    return envelope(
        {
            "event_count": data.get("event_count"),
            "task_count": data.get("task_count"),
            "generated_at_utc": data.get("generated_at_utc"),
            "first_task": (data.get("tasks") or [None])[0],
            "first_event": (data.get("events") or [None])[0],
        },
        source=str(CANON_FILES["sample"].relative_to(REPO_ROOT)),
        extra={"note": "summary view; full sample available in canon file"},
    )


def handler_workflow_actions() -> dict:
    data = load_json(CANON_FILES["actions"])
    return envelope(data, source=str(CANON_FILES["actions"].relative_to(REPO_ROOT)))


def handler_workflow_receipts_recent() -> dict:
    if not RECEIPTS.exists():
        return envelope({"receipts": [], "count": 0}, source="receipts/")
    items = []
    for p in sorted(RECEIPTS.glob("*.md")):
        st = p.stat()
        items.append(
            {
                "name": p.name,
                "size_bytes": st.st_size,
                "mtime_utc": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
            }
        )
    items.sort(key=lambda x: x["mtime_utc"], reverse=True)
    return envelope(
        {"receipts": items[:10], "count": len(items)},
        source="receipts/",
        extra={"note": "directory listing only; no receipt content served"},
    )


ROUTES = {
    "/api/health": handler_health,
    "/api/workflow/status": handler_workflow_status,
    "/api/workflow/schema": handler_workflow_schema,
    "/api/workflow/rules": handler_workflow_rules,
    "/api/workflow/templates/universal-172": handler_workflow_universal_172,
    "/api/workflow/sample": handler_workflow_sample,
    "/api/workflow/actions": handler_workflow_actions,
    "/api/workflow/receipts/recent": handler_workflow_receipts_recent,
}


def dispatch(path: str) -> tuple[int, dict]:
    parsed = urlparse(path)
    route = parsed.path.rstrip("/") or "/"
    handler = ROUTES.get(route)
    if handler is None:
        return 404, envelope(
            {"error": "not_found", "path": route, "known_routes": sorted(ROUTES.keys())}
        )
    try:
        return 200, handler()
    except FileNotFoundError as e:
        return 500, envelope({"error": "canon_file_missing", "detail": str(e)})
    except json.JSONDecodeError as e:
        return 500, envelope({"error": "canon_file_invalid_json", "detail": str(e)})


class KernelHandler(BaseHTTPRequestHandler):
    server_version = f"{KERNEL_NAME}/{KERNEL_VERSION}"

    def do_GET(self) -> None:  # noqa: N802
        status, body = dispatch(self.path)
        payload = json.dumps(body, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Kernel-Mode", "local_only")
        self.send_header("X-Kernel-Production", "false")
        self.wfile.write(payload)

    def do_POST(self) -> None:  # noqa: N802
        # Proof kernel is read-only; no mutating endpoints exist.
        status, body = 405, envelope({"error": "method_not_allowed", "method": "POST"})
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        sys.stderr.write(
            "[%s] %s - %s\n" % (utcnow(), self.address_string(), format % args)
        )


def smoke() -> int:
    """In-process dispatch over every documented endpoint. Returns shell exit code."""
    print(f"=== {KERNEL_NAME} smoke (in-process, no socket) ===")
    failed = 0
    for path in ENDPOINTS:
        status, body = dispatch(path)
        ok = status == 200 and body.get("production") is False and body.get("mode") == "local_only"
        marker = "GREEN" if ok else "RED  "
        print(f"  {marker} {status:>3} {path}")
        if not ok:
            failed += 1
            print(f"        body={json.dumps(body)[:200]}")
    print(f"=== smoke result: {'GREEN' if failed == 0 else f'RED ({failed} failed)'} ===")
    return 0 if failed == 0 else 1


def serve(host: str, port: int) -> None:
    if host not in {"127.0.0.1", "localhost"}:
        raise SystemExit(
            f"refusing to bind {host}: kernel is local_only and must use 127.0.0.1"
        )
    httpd = ThreadingHTTPServer((host, port), KernelHandler)
    print(f"=== {KERNEL_NAME} v{KERNEL_VERSION} ===")
    print(f"mode: local_only  production: false  implemented: proof_only")
    print(f"listening: http://{host}:{port}")
    print("endpoints:")
    for ep in ENDPOINTS:
        print(f"  GET {ep}")
    print("ctrl-c to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        httpd.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(description="RoadWork local API kernel v0 (proof only)")
    parser.add_argument("--smoke", action="store_true", help="run in-process smoke and exit")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    if args.smoke:
        return smoke()
    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
