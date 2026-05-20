import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "canon/workflow"
UI = WORKFLOW / "ui"
REPORTS = ROOT / "reports"

rules_path = WORKFLOW / "rules/workflow_transition_rules_v0.json"
ui_spec_path = UI / "roadwork_ui_state_spec_v0.json"

rules = json.loads(rules_path.read_text())
ui_spec = json.loads(ui_spec_path.read_text())

receipt_required = set(rules["receipt_required_actions"])

BUTTON_LABELS = {
    "mark_read": "Mark Read",
    "claim": "Claim",
    "close": "Close",
    "escalate": "Escalate",
    "start_work": "Start Work",
    "set_awaiting": "Set Awaiting",
    "collaborate": "Collaborate",
    "update_progress": "Update Progress",
    "complete": "Complete",
    "block": "Block",
    "resolve_awaiting": "Resolve Awaiting",
    "reassign": "Reassign",
    "cancel": "Cancel",
    "resolve_blocker": "Resolve Blocker",
    "archive": "Archive",
    "reopen": "Reopen",
    "restore": "Restore"
}

BUTTON_KIND = {
    "mark_read": "secondary",
    "claim": "primary",
    "close": "danger",
    "escalate": "warning",
    "start_work": "primary",
    "set_awaiting": "warning",
    "collaborate": "secondary",
    "update_progress": "secondary",
    "complete": "success",
    "block": "danger",
    "resolve_awaiting": "primary",
    "reassign": "secondary",
    "cancel": "danger",
    "resolve_blocker": "primary",
    "archive": "secondary",
    "reopen": "warning",
    "restore": "primary"
}

matrix = {
    "name": "RoadWork Action Button Matrix",
    "version": "0.1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "status": "planned_ui_action_matrix",
    "buttons_by_status": {}
}

errors = []

for status, column in ui_spec["status_columns"].items():
    allowed = rules["actions"].get(status, {})
    primary_actions = column["primary_actions"]

    matrix["buttons_by_status"][status] = []

    for action in primary_actions:
        if action not in allowed:
            errors.append(f"{status}: UI action {action} missing from transition rules")
            continue

        target_status = allowed[action]

        matrix["buttons_by_status"][status].append({
            "action": action,
            "label": BUTTON_LABELS.get(action, action.replace("_", " ").title()),
            "from_status": status,
            "to_status": target_status,
            "kind": BUTTON_KIND.get(action, "secondary"),
            "requires_receipt": action in receipt_required,
            "enabled_when": [
                f"workflow.status == '{status}'",
                "user_or_agent_has_permission == true"
            ]
        })

if errors:
    for error in errors:
        print("ERROR:", error)
    raise SystemExit(1)

json_path = UI / "roadwork_action_button_matrix_v0.json"
md_path = UI / "ROADWORK_ACTION_BUTTON_MATRIX_V0.md"
receipt_path = REPORTS / "roadwork-action-button-matrix-v0-receipt-20260520.md"

json_path.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n")

lines = [
    "# RoadWork Action Button Matrix v0",
    "",
    f"Generated at UTC: {matrix['generated_at_utc']}",
    "",
    "Status: planned_ui_action_matrix",
    "",
]

for status, buttons in matrix["buttons_by_status"].items():
    lines.append(f"## `{status}`")
    lines.append("")
    lines.append("| Button | Action | Next status | Kind | Receipt required |")
    lines.append("|---|---|---|---|---|")

    for button in buttons:
        lines.append(
            f"| {button['label']} | `{button['action']}` | `{button['to_status']}` | {button['kind']} | {button['requires_receipt']} |"
        )

    lines.append("")

md_path.write_text("\n".join(lines) + "\n")

button_count = sum(len(buttons) for buttons in matrix["buttons_by_status"].values())
receipt_required_count = sum(
    1
    for buttons in matrix["buttons_by_status"].values()
    for button in buttons
    if button["requires_receipt"]
)

receipt_path.write_text(f"""# RoadWork Action Button Matrix v0 Receipt

Date:
2026-05-20

Local root:
~/blackroad/orgs

Action:
Created RoadWork Action Button Matrix v0 from validated workflow transition rules and RoadWork UI State Spec v0.

Files:
- _canon/workflow/ui/roadwork_action_button_matrix_v0.json
- _canon/workflow/ui/ROADWORK_ACTION_BUTTON_MATRIX_V0.md

Validation:
- Statuses mapped: {len(matrix['buttons_by_status'])}
- Buttons mapped: {button_count}
- Receipt-required buttons: {receipt_required_count}
- Invalid UI actions: 0

Purpose:
Define allowed UI/agent action buttons per workflow status, including target status and receipt requirement.

Status:
planned_ui_action_matrix

Policy:
- Local canon/UI files only.
- No GitHub repos changed.
- No secrets touched.
- No generated runtime artifacts committed.
""")

print("wrote", json_path)
print("wrote", md_path)
print("wrote", receipt_path)
print("statuses:", len(matrix["buttons_by_status"]))
print("buttons:", button_count)
print("receipt_required_buttons:", receipt_required_count)
