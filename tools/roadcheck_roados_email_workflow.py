#!/usr/bin/env python3
from pathlib import Path
import subprocess
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "site/roados_email_workflow_plain_proof.html"
VALIDATOR = ROOT / "tools/validate_roados_email_workflow_plain_proof.py"
SPEC = ROOT / "canon/roados/window_grammar/roados_email_workflow_plain_proof_spec_v0.json"

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BLUE = "\033[36m"
RESET = "\033[0m"
BOLD = "\033[1m"

results = []

def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)

def add(level, name, detail=""):
    results.append((level, name, detail))

def exists(path, label, required=True):
    if path.exists():
        add("green", label, str(path.relative_to(ROOT)))
    else:
        add("red" if required else "yellow", label, f"missing: {path.relative_to(ROOT)}")

def marker_check(text, marker, label, required=True):
    if marker in text:
        add("green", label, marker)
    else:
        add("red" if required else "yellow", label, f"missing marker: {marker}")

def no_pattern(text, pattern, label, required=True):
    if re.search(pattern, text, flags=re.I):
        add("red" if required else "yellow", label, f"found forbidden pattern: {pattern}")
    else:
        add("green", label, f"not found: {pattern}")

print(f"{BOLD}{BLUE}RoadOS Email Workflow Proof Terminal Check{RESET}")
print(f"{BLUE}root: {ROOT}{RESET}")
print("")

exists(HTML, "HTML proof file")
exists(VALIDATOR, "validator file")
exists(SPEC, "spec JSON file", required=False)

branch = run(["git", "branch", "--show-current"])
branch_name = branch.stdout.strip()
if branch.returncode == 0 and branch_name:
    if branch_name == "roados-email-workflow-proof":
        add("green", "git branch", branch_name)
    else:
        add("yellow", "git branch", f"{branch_name} (expected roados-email-workflow-proof while developing)")
else:
    add("yellow", "git branch", "could not read branch")

status = run(["git", "status", "--short"])
if status.returncode == 0:
    if status.stdout.strip():
        add("yellow", "git working tree", "dirty / uncommitted changes present")
    else:
        add("green", "git working tree", "clean")
else:
    add("yellow", "git working tree", status.stderr.strip())

if VALIDATOR.exists():
    pyc = run(["python3", "-m", "py_compile", str(VALIDATOR.relative_to(ROOT))])
    if pyc.returncode == 0:
        add("green", "validator py_compile", "OK")
    else:
        add("red", "validator py_compile", pyc.stderr.strip())

    val = run(["python3", str(VALIDATOR.relative_to(ROOT))])
    if val.returncode == 0:
        add("green", "validator run", val.stdout.strip().splitlines()[-1] if val.stdout.strip() else "OK")
    else:
        add("red", "validator run", val.stderr.strip() or val.stdout.strip())

if HTML.exists():
    html = HTML.read_text(errors="replace")

    for i in range(1, 9):
        marker_check(html, f'id="slot-{i}"', f"slot {i}")

    for i in range(9, 21):
        marker_check(html, f'id="dock-{i}"', f"dock {i}")

    required_behaviors = [
        "localStorage",
        "receipt(",
        "draftReply",
        "claimItem",
        "setAwaiting",
        "createTask",
        "setupWindowBehavior",
        "expandSlot",
        "restoreExpanded",
        "setupRoadDragSwap",
        "swapRoadSlots",
        "setupDockStorage",
        "storeRoadSlot",
        "restoreStoredSlot",
        "recordLayoutState",
        "applyLayoutState",
        "workspacePresets",
        "exportWorkspacePackage",
        "importWorkspacePackage",
        "runLocalSearch",
        "getFilteredEmails",
    ]

    for marker in required_behaviors:
        marker_check(html, marker, f"behavior: {marker}")

    honesty_markers = [
        "LOCAL MOCK PROOF",
        "No Gmail",
        "No real send",
        "No external API",
        "No secrets",
        "No production claim",
        "MOCK",
    ]

    for marker in honesty_markers:
        marker_check(html, marker, f"honesty: {marker}")

    forbidden = [
        r"https?://",
        r"api\.gmail",
        r"slack\.com",
        r"fetch\s*\(",
        r"XMLHttpRequest",
        r"Authorization:",
        r"Bearer ",
        r"OPENAI_API_KEY",
        r"CLOUDFLARE_API_TOKEN",
        r"RAILWAY_TOKEN",
        r"GITHUB_TOKEN",
    ]

    for pattern in forbidden:
        no_pattern(html, pattern, f"forbidden: {pattern}")

greens = [r for r in results if r[0] == "green"]
yellows = [r for r in results if r[0] == "yellow"]
reds = [r for r in results if r[0] == "red"]

def color(level):
    return {"green": GREEN, "yellow": YELLOW, "red": RED}[level]

def icon(level):
    return {"green": "GREEN", "yellow": "YELLOW", "red": "RED"}[level]

for level, name, detail in results:
    print(f"{color(level)}{icon(level):6}{RESET} {name}")
    if detail:
        print(f"       {detail}")

print("")
print(f"{BOLD}SUMMARY{RESET}")
print(f"{GREEN}GREEN:{RESET} {len(greens)}")
print(f"{YELLOW}YELLOW:{RESET} {len(yellows)}")
print(f"{RED}RED:{RESET} {len(reds)}")

if reds:
    print(f"\n{RED}{BOLD}FAIL{RESET}: fix RED items before PR/merge.")
    sys.exit(1)

if yellows:
    print(f"\n{YELLOW}{BOLD}WARN{RESET}: usable, but review YELLOW items.")
    sys.exit(0)

print(f"\n{GREEN}{BOLD}PASS{RESET}: RoadOS proof looks good.")
