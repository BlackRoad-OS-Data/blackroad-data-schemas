#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import subprocess
import json

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

HTML = ROOT / "site/roados_email_workflow_plain_proof.html"
CHECK = ROOT / "tools/roadcheck_roados_email_workflow.py"
SPEC = ROOT / "canon/roados/window_grammar/roados_email_workflow_plain_proof_spec_v0.json"

def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)

def sh(cmd):
    p = run(cmd)
    return p.stdout.strip() if p.returncode == 0 else ""

now = datetime.now(timezone.utc).isoformat()
branch = sh(["git", "branch", "--show-current"])
commit = sh(["git", "rev-parse", "--short", "HEAD"])
status = sh(["git", "status", "--short"])
dirty = bool(status)

check = run(["python3", str(CHECK.relative_to(ROOT))]) if CHECK.exists() else None
check_ok = check is not None and check.returncode == 0

pr_json = sh([
    "gh", "pr", "list",
    "--repo", "BlackRoad-OS-Data/blackroad-data-schemas",
    "--head", branch,
    "--state", "open",
    "--json", "number,title,isDraft,baseRefName,headRefName,url",
])
try:
    prs = json.loads(pr_json) if pr_json else []
except Exception:
    prs = []

features = [
    "8 RoadOS work slots",
    "dock slots 9–20",
    "email/thread/compose/workflow panels",
    "mock receipts/event history",
    "claim/start/awaiting/done transitions",
    "draft reply/create task/mock AI actions",
    "localStorage persistence",
    "window focus/expand/restore",
    "drag/drop swap road spots",
    "dock store/restore",
    "persistent layout state",
    "workspace presets",
    "workspace package import/export",
    "local search",
    "inbox filter/sort",
    "terminal check/doctor/control commands",
]

honesty = [
    "No Gmail connected",
    "No real send",
    "No external API",
    "No backend",
    "No secrets",
    "No production RoadOS/RoadWork claim",
    "Local browser-state proof only",
]

payload = {
    "generated_at_utc": now,
    "repo": "BlackRoad-OS-Data/blackroad-data-schemas",
    "branch": branch,
    "commit": commit,
    "dirty": dirty,
    "check_ok": check_ok,
    "pr": prs[0] if prs else None,
    "features": features,
    "honesty": honesty,
}

json_path = REPORT_DIR / "ROADOS_EMAIL_WORKFLOW_PROOF_STATUS.json"
md_path = REPORT_DIR / "ROADOS_EMAIL_WORKFLOW_PROOF_STATUS.md"

json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

lines = [
    "# RoadOS Email Workflow Proof Status",
    "",
    f"Generated at UTC: {now}",
    "",
    "## Repo",
    "",
    f"- Repo: BlackRoad-OS-Data/blackroad-data-schemas",
    f"- Branch: {branch}",
    f"- Commit: {commit}",
    f"- Working tree dirty: {dirty}",
    f"- Terminal check OK: {check_ok}",
    "",
]

if prs:
    pr = prs[0]
    lines += [
        "## Open PR",
        "",
        f"- PR: {pr.get('url')}",
        f"- Title: {pr.get('title')}",
        f"- Draft: {pr.get('isDraft')}",
        f"- Base: {pr.get('baseRefName')}",
        f"- Head: {pr.get('headRefName')}",
        "",
    ]
else:
    lines += ["## Open PR", "", "- No open PR detected for current branch.", ""]

lines += ["## What works", ""]
for item in features:
    lines.append(f"- {item}")

lines += ["", "## Honesty / still not real", ""]
for item in honesty:
    lines.append(f"- {item}")

lines += ["", "## Files", ""]
for path in [HTML, CHECK, SPEC]:
    exists = path.exists()
    rel = path.relative_to(ROOT)
    lines.append(f"- {'OK' if exists else 'MISSING'} {rel}")

lines += ["", "## Next safest action", ""]
if dirty:
    lines.append("Commit or intentionally discard uncommitted files, then rerun `./roados doctor`.")
elif not check_ok:
    lines.append("Fix terminal check RED items before review.")
else:
    lines.append("Review the draft PR, then decide whether to mark ready for review or keep iterating on local proof.")

md_path.write_text("\n".join(lines) + "\n")

print("wrote", md_path)
print("wrote", json_path)
print("check_ok:", check_ok)
print("dirty:", dirty)
