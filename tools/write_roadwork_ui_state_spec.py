import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_canon/workflow/ui"
REPORTS = ROOT / "reports"

OUT.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

spec = {
    "name": "RoadWork UI State Spec",
    "version": "0.1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "status": "planned_ui_spec",
    "purpose": "Define RoadWork inbox, workflow board, actions, badges, detail panels, and receipt visibility.",
    "views": [
        {
            "id": "inbox",
            "name": "Inbox",
            "description": "Everything received from RoadWire, OneWay, forms, APIs, agents, or manual entry.",
            "default_filters": ["status:received", "status:triaged", "status:awaiting", "status:blocked"]
        },
        {
            "id": "board",
            "name": "Workflow Board",
            "description": "Kanban-style view grouped by workflow status.",
            "columns": ["received", "triaged", "in_progress", "awaiting", "collaborating", "blocked", "done", "archived"]
        },
        {
            "id": "timeline",
            "name": "Timeline",
            "description": "SLA, due date, escalation, awaiting, and receipt timeline."
        },
        {
            "id": "process",
            "name": "172-Step Process",
            "description": "Universal 172-step repeatable process as linked tasks."
        }
    ],
    "status_columns": {
        "received": {
            "label": "New / Received",
            "badge": "NEW",
            "meaning": "Item entered the system but is not owned yet.",
            "primary_actions": ["mark_read", "claim", "close", "escalate"]
        },
        "triaged": {
            "label": "Triaged",
            "badge": "TRIAGED",
            "meaning": "Item has been read/claimed and is ready to start.",
            "primary_actions": ["start_work", "set_awaiting", "collaborate", "close", "escalate"]
        },
        "in_progress": {
            "label": "In Progress",
            "badge": "ACTIVE",
            "meaning": "Work is actively moving.",
            "primary_actions": ["update_progress", "set_awaiting", "collaborate", "complete", "block"]
        },
        "awaiting": {
            "label": "Awaiting",
            "badge": "AWAITING",
            "meaning": "Work is paused for a typed reason.",
            "primary_actions": ["resolve_awaiting", "escalate", "reassign", "cancel"]
        },
        "collaborating": {
            "label": "Collaborating",
            "badge": "COLLAB",
            "meaning": "Multiple humans or agents are involved.",
            "primary_actions": ["update_progress", "set_awaiting", "complete", "block"]
        },
        "blocked": {
            "label": "Blocked",
            "badge": "BLOCKED",
            "meaning": "Work cannot proceed without a blocker being resolved.",
            "primary_actions": ["resolve_blocker", "set_awaiting", "close"]
        },
        "done": {
            "label": "Done",
            "badge": "DONE",
            "meaning": "Work completed or closed.",
            "primary_actions": ["reopen", "archive"]
        },
        "archived": {
            "label": "Archived",
            "badge": "ARCHIVED",
            "meaning": "Removed from active work but recoverable.",
            "primary_actions": ["restore"]
        }
    },
    "card_fields": [
        "index_id",
        "title",
        "source",
        "status",
        "claimed_by",
        "awaiting_type",
        "due_at",
        "receipt_count",
        "task_progress"
    ],
    "detail_panels": [
        "summary",
        "actions",
        "172_tasks",
        "subtasks",
        "awaiting",
        "timeline",
        "collaborators",
        "events",
        "receipts",
        "source_payload"
    ],
    "awaiting_badges": {
        "customer_response": "Awaiting customer",
        "internal_approval": "Awaiting approval",
        "external_vendor": "Awaiting vendor",
        "legal_review": "Legal review",
        "security_review": "Security review",
        "data_access": "Data access",
        "credentials": "Credentials",
        "parts_or_assets": "Assets needed",
        "agent_output": "Agent output",
        "deployment_window": "Deploy window",
        "payment_or_billing": "Billing"
    },
    "receipt_panel": {
        "required_for_actions": [
            "claim",
            "start_work",
            "set_awaiting",
            "resolve_awaiting",
            "complete",
            "archive",
            "reopen",
            "resolve_blocker"
        ],
        "fields": [
            "receipt_id",
            "receipt_type",
            "actor",
            "action",
            "created_at",
            "receipt_path",
            "receipt_hash"
        ]
    },
    "honesty_rules": [
        "Do not show implemented status unless receipts/tests prove it.",
        "Show initialized-shell when the repo or workflow only has structure.",
        "Show partial when work exists but is not verified.",
        "Show blocked when access, disk, permissions, or decisions stop progress.",
        "Every major action should create an event or receipt."
    ]
}

json_path = OUT / "roadwork_ui_state_spec_v0.json"
md_path = OUT / "ROADWORK_UI_STATE_SPEC_V0.md"
receipt_path = REPORTS / "roadwork-ui-state-spec-v0-receipt-20260520.md"

json_path.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")

lines = [
    "# RoadWork UI State Spec v0",
    "",
    f"Generated at UTC: {spec['generated_at_utc']}",
    "",
    "Status: planned_ui_spec",
    "",
    "## Views",
    "",
]

for view in spec["views"]:
    lines.append(f"### {view['name']}")
    lines.append("")
    lines.append(view["description"])
    lines.append("")

lines.append("## Status Columns")
lines.append("")

for status, column in spec["status_columns"].items():
    lines.append(f"### {column['label']} `{status}`")
    lines.append("")
    lines.append(f"- Badge: {column['badge']}")
    lines.append(f"- Meaning: {column['meaning']}")
    lines.append(f"- Actions: {', '.join(column['primary_actions'])}")
    lines.append("")

lines.append("## Detail Panels")
lines.append("")
for panel in spec["detail_panels"]:
    lines.append(f"- {panel}")

lines.append("")
lines.append("## Honesty Rules")
lines.append("")
for rule in spec["honesty_rules"]:
    lines.append(f"- {rule}")

md_path.write_text("\n".join(lines) + "\n")

receipt_path.write_text(f"""# RoadWork UI State Spec v0 Receipt

Date:
2026-05-20

Local root:
~/blackroad/orgs

Action:
Created RoadWork UI State Spec v0 for workflow views, status columns, action buttons, awaiting badges, detail panels, and receipt visibility.

Files:
- _canon/workflow/ui/roadwork_ui_state_spec_v0.json
- _canon/workflow/ui/ROADWORK_UI_STATE_SPEC_V0.md

Validation:
- Views: {len(spec['views'])}
- Status columns: {len(spec['status_columns'])}
- Detail panels: {len(spec['detail_panels'])}
- Receipt-required actions: {len(spec['receipt_panel']['required_for_actions'])}

Status:
planned_ui_spec

Policy:
- Local canon/UI spec files only.
- No GitHub repos changed.
- No secrets touched.
- No generated runtime artifacts committed.
""")

print("wrote", json_path)
print("wrote", md_path)
print("wrote", receipt_path)
print("views:", len(spec["views"]))
print("status_columns:", len(spec["status_columns"]))
print("detail_panels:", len(spec["detail_panels"]))
