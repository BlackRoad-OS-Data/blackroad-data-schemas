#!/usr/bin/env python3
from pathlib import Path
import argparse
import subprocess
import sys
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "site/roados_email_workflow_plain_proof.html"
CHECK = ROOT / "tools/roadcheck_roados_email_workflow.py"
VALIDATOR = ROOT / "tools/validate_roados_email_workflow_plain_proof.py"
SPEC = ROOT / "canon/roados/window_grammar/roados_email_workflow_plain_proof_spec_v0.json"

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"

def run(cmd):
    return subprocess.run(cmd, cwd=ROOT)

def cmd_check(_args):
    if not CHECK.exists():
        print(f"{RED}RED{RESET} missing {CHECK}")
        return 1
    return run(["python3", str(CHECK.relative_to(ROOT))]).returncode

def cmd_validate(_args):
    if not VALIDATOR.exists():
        print(f"{RED}RED{RESET} missing {VALIDATOR}")
        return 1
    return run(["python3", "-m", "py_compile", str(VALIDATOR.relative_to(ROOT))]).returncode or run(["python3", str(VALIDATOR.relative_to(ROOT))]).returncode

def cmd_open(_args):
    if not HTML.exists():
        print(f"{RED}RED{RESET} missing {HTML}")
        return 1
    webbrowser.open(HTML.resolve().as_uri())
    print(f"{GREEN}GREEN{RESET} opened {HTML}")
    return 0

def cmd_serve(args):
    if not HTML.exists():
        print(f"{RED}RED{RESET} missing {HTML}")
        return 1
    print(f"{CYAN}{BOLD}RoadOS local proof server{RESET}")
    print(f"root: {ROOT}")
    print(f"url:  http://127.0.0.1:{args.port}/site/roados_email_workflow_plain_proof.html")
    print("stop: Ctrl+C")
    return run(["python3", "-m", "http.server", str(args.port), "--bind", "127.0.0.1"]).returncode

def cmd_where(_args):
    print(f"{CYAN}{BOLD}RoadOS Email Workflow Proof Paths{RESET}")
    for label, path in [
        ("root", ROOT),
        ("html", HTML),
        ("check", CHECK),
        ("validator", VALIDATOR),
        ("spec", SPEC),
    ]:
        status = "GREEN" if path.exists() else "RED"
        color = GREEN if path.exists() else RED
        print(f"{color}{status:6}{RESET} {label}: {path}")
    return 0

def main():
    parser = argparse.ArgumentParser(description="RoadOS email workflow proof terminal control.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="Run green/yellow/red terminal health check.").set_defaults(fn=cmd_check)
    sub.add_parser("validate", help="Run validator only.").set_defaults(fn=cmd_validate)
    sub.add_parser("open", help="Open local HTML proof in browser.").set_defaults(fn=cmd_open)
    sub.add_parser("where", help="Print important proof paths.").set_defaults(fn=cmd_where)

    serve = sub.add_parser("serve", help="Serve repo locally over http://127.0.0.1.")
    serve.add_argument("--port", type=int, default=8765)
    serve.set_defaults(fn=cmd_serve)

    args = parser.parse_args()
    raise SystemExit(args.fn(args))

if __name__ == "__main__":
    main()
