from pathlib import Path
import re
import json

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "site/roados_email_workflow_plain_proof.html"
SPEC = ROOT / "canon/roados/window_grammar/roados_email_workflow_plain_proof_spec_v0.json"

html = HTML.read_text()

required_slots = [f'id="slot-{i}"' for i in range(1, 9)]
required_dock = [f'id="dock-{i}"' for i in range(9, 21)]
required_terms = [
    "LOCAL MOCK PROOF",
    "No Gmail",
    "No real send",
    "No external API",
    "No secrets",
    "No production claim",
    "received",
    "read",
    "triaged",
    "in_progress",
    "awaiting",
    "done",
    "awaiting_type",
    "receipt",
    "MOCK",
    "Double-click any slot to expand",
    "Escape",
    "setupWindowBehavior",
    "expandSlot",
    "restoreExpanded",
    "expanded-window",
]

missing = []

for marker in required_slots:
    if marker not in html:
        missing.append(marker)

for marker in required_dock:
    if marker not in html:
        missing.append(marker)

for term in required_terms:
    if term not in html:
        missing.append(term)

external_patterns = [
    r"https?://",
    r"api\.gmail",
    r"slack\.com",
    r"fetch\(",
    r"XMLHttpRequest",
]

external_hits = []
for pattern in external_patterns:
    if re.search(pattern, html, flags=re.I):
        external_hits.append(pattern)

spec = {
    "version": "0.1",
    "status": "local_mock_proof",
    "implementation_status": "mock_local_browser_state_only",
    "html_file": str(HTML.relative_to(ROOT)),
    "desktop_slots": list(range(1, 9)),
    "dock_slots": list(range(9, 21)),
    "workflow_statuses": [
        "received",
        "read",
        "claimed",
        "triaged",
        "in_progress",
        "awaiting",
        "done",
        "archived"
    ],
    "surface_types": [
        "inbox_list",
        "email_thread",
        "email_compose",
        "workflow_item",
        "ai_actions",
        "attachment_preview",
        "receipt_history",
        "agent_context"
    ],
    "rules": {
        "no_real_send": True,
        "no_external_api": True,
        "no_gmail": True,
        "no_secrets": True,
        "no_production_claim": True,
        "mock_labels_required": True,
        "receipt_panel_required": True
    }
}

SPEC.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")

if missing:
    raise SystemExit("missing required markers: " + ", ".join(missing))

if external_hits:
    raise SystemExit("external/API patterns found: " + ", ".join(external_hits))

print("RoadOS email workflow plain proof validation OK")
print("html:", HTML)
print("spec:", SPEC)
print("slots:", 8)
print("dock_slots:", 12)
print("status:", spec["status"])
