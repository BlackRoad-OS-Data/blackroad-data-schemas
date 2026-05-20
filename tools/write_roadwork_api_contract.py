import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "_canon/workflow/api"
REPORTS = ROOT / "reports"

API.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

contract = {
    "name": "RoadWork Workflow API Contract",
    "version": "0.1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "status": "planned_api_contract",
    "purpose": "Define API routes for workflow items, actions, events, receipts, allowed actions, and Universal 172 templates.",
    "base_path": "/api/workflow",
    "auth_policy": {
        "identity_layer": "CarKeys",
        "default": "operator_or_granted_agent_required",
        "dangerous_actions_require_receipt": True
    },
    "endpoints": [
        {
            "method": "GET",
            "path": "/api/workflow/status",
            "purpose": "Return API health and contract version.",
            "request": {},
            "response": {"ok": True, "version": "0.1"}
        },
        {
            "method": "GET",
            "path": "/api/workflow/items",
            "purpose": "List workflow items with filters.",
            "request": {
                "query": {
                    "status": "optional status filter",
                    "claimed_by": "optional owner filter",
                    "awaiting_type": "optional awaiting filter",
                    "limit": "default 50"
                }
            },
            "response": {"items": [], "count": 0}
        },
        {
            "method": "POST",
            "path": "/api/workflow/items",
            "purpose": "Create a new workflow item from RoadWire, OneWay, manual input, API, or agent.",
            "request": {
                "body": {
                    "title": "required",
                    "description": "optional",
                    "source": "required",
                    "source_id": "optional"
                }
            },
            "response": {"item": "workflow_item"}
        },
        {
            "method": "GET",
            "path": "/api/workflow/items/:id",
            "purpose": "Read one workflow item with task counts and current state.",
            "request": {"path": {"id": "workflow item id"}},
            "response": {"item": "workflow_item"}
        },
        {
            "method": "GET",
            "path": "/api/workflow/items/:id/tasks",
            "purpose": "List tasks and subtasks attached to a workflow item.",
            "request": {"path": {"id": "workflow item id"}},
            "response": {"tasks": [], "count": 0}
        },
        {
            "method": "GET",
            "path": "/api/workflow/items/:id/allowed-actions",
            "purpose": "Return valid action buttons for the item current status.",
            "request": {"path": {"id": "workflow item id"}},
            "response": {"status": "received", "actions": []}
        },
        {
            "method": "POST",
            "path": "/api/workflow/items/:id/actions",
            "purpose": "Run a validated workflow action such as claim, start_work, set_awaiting, complete, archive, or reopen.",
            "request": {
                "path": {"id": "workflow item id"},
                "body": {
                    "action": "required",
                    "actor": "required",
                    "note": "optional",
                    "metadata": "optional object"
                }
            },
            "response": {
                "ok": True,
                "before_status": "received",
                "after_status": "triaged",
                "receipt_id": "required for receipt-required actions"
            }
        },
        {
            "method": "GET",
            "path": "/api/workflow/items/:id/events",
            "purpose": "List event history for one workflow item.",
            "request": {"path": {"id": "workflow item id"}},
            "response": {"events": [], "count": 0}
        },
        {
            "method": "GET",
            "path": "/api/workflow/items/:id/actions",
            "purpose": "List action history for one workflow item.",
            "request": {"path": {"id": "workflow item id"}},
            "response": {"actions": [], "count": 0}
        },
        {
            "method": "GET",
            "path": "/api/workflow/items/:id/receipts",
            "purpose": "List receipts linked to one workflow item.",
            "request": {"path": {"id": "workflow item id"}},
            "response": {"receipts": [], "count": 0}
        },
        {
            "method": "GET",
            "path": "/api/workflow/items/:id/timeline",
            "purpose": "List due dates, SLA deadlines, escalations, and awaiting timeline events.",
            "request": {"path": {"id": "workflow item id"}},
            "response": {"timeline": [], "count": 0}
        },
        {
            "method": "GET",
            "path": "/api/workflow/rules/transitions",
            "purpose": "Return transition rules for statuses and actions.",
            "request": {},
            "response": {"rules": "workflow_transition_rules_v0"}
        },
        {
            "method": "GET",
            "path": "/api/workflow/ui/action-button-matrix",
            "purpose": "Return UI button matrix for all statuses.",
            "request": {},
            "response": {"matrix": "roadwork_action_button_matrix_v0"}
        },
        {
            "method": "GET",
            "path": "/api/workflow/templates/universal-172",
            "purpose": "Return the Universal 172-Step Repeatable Process template.",
            "request": {},
            "response": {"template": "universal_172_process"}
        },
        {
            "method": "POST",
            "path": "/api/workflow/templates/universal-172/instantiate",
            "purpose": "Create a workflow item with 172 linked tasks from the Universal 172 template.",
            "request": {
                "body": {
                    "title": "required",
                    "source": "manual_or_agent_or_api",
                    "owner": "optional",
                    "start_status": "default received"
                }
            },
            "response": {
                "workflow_item": "workflow_item",
                "tasks_created": 172
            }
        }
    ],
    "honesty_rules": [
        "This is a planned API contract, not an implemented server.",
        "Every state-changing POST must validate transition rules.",
        "Receipt-required actions must produce receipt rows.",
        "Do not expose secrets, tokens, source payloads, or private data by default.",
        "All statuses must remain compatible with workflow_transition_rules_v0."
    ]
}

json_path = API / "roadwork_api_contract_v0.json"
md_path = API / "ROADWORK_API_CONTRACT_V0.md"
receipt_path = REPORTS / "roadwork-api-contract-v0-receipt-20260520.md"

json_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")

lines = [
    "# RoadWork API Contract v0",
    "",
    f"Generated at UTC: {contract['generated_at_utc']}",
    "",
    "Status: planned_api_contract",
    "",
    f"Base path: `{contract['base_path']}`",
    "",
    "## Endpoints",
    "",
    "| Method | Path | Purpose |",
    "|---|---|---|",
]

for endpoint in contract["endpoints"]:
    lines.append(f"| {endpoint['method']} | `{endpoint['path']}` | {endpoint['purpose']} |")

lines.extend([
    "",
    "## Honesty Rules",
    ""
])

for rule in contract["honesty_rules"]:
    lines.append(f"- {rule}")

md_path.write_text("\n".join(lines) + "\n")

receipt_path.write_text(f"""# RoadWork API Contract v0 Receipt

Date:
2026-05-20

Local root:
~/blackroad/orgs

Action:
Created RoadWork Workflow API Contract v0.

Files:
- _canon/workflow/api/roadwork_api_contract_v0.json
- _canon/workflow/api/ROADWORK_API_CONTRACT_V0.md

Validation:
- Endpoints: {len(contract['endpoints'])}
- Base path: {contract['base_path']}
- Status: planned_api_contract

Purpose:
Define API routes for workflow items, tasks, allowed actions, state transitions, events, receipts, timeline, UI action matrix, and Universal 172 template instantiation.

Policy:
- Local canon/API files only.
- No server implemented yet.
- No GitHub repos changed.
- No secrets touched.
- No generated runtime artifacts committed.
""")

print("wrote", json_path)
print("wrote", md_path)
print("wrote", receipt_path)
print("endpoints:", len(contract["endpoints"]))
