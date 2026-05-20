import json
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "canon/workflow"
REPORTS = ROOT / "reports"

contract_path = WORKFLOW / "api/roadwork_api_contract_v0.json"
rules_path = WORKFLOW / "rules/workflow_transition_rules_v0.json"
button_matrix_path = WORKFLOW / "ui/roadwork_action_button_matrix_v0.json"

source_db_path = ROOT / "reports/tmp/roadwork_action_runner_v0.sqlite"
smoke_db_path = ROOT / "reports/tmp/roadwork_mock_api_smoke_v0.sqlite"

smoke_json_path = WORKFLOW / "api/roadwork_mock_api_smoke_v0.json"
smoke_md_path = WORKFLOW / "api/ROADWORK_MOCK_API_SMOKE_V0.md"
receipt_path = REPORTS / "roadwork-mock-api-smoke-v0-receipt-20260520.md"

if not source_db_path.exists():
    raise SystemExit("missing reports/tmp/roadwork_action_runner_v0.sqlite; run action runner first")

shutil.copyfile(source_db_path, smoke_db_path)

contract = json.loads(contract_path.read_text())
rules = json.loads(rules_path.read_text())
button_matrix = json.loads(button_matrix_path.read_text())

db = sqlite3.connect(smoke_db_path)
db.row_factory = sqlite3.Row

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def row_to_dict(row):
    return dict(row) if row else None

def api_status():
    return {
        "ok": True,
        "contract": contract["name"],
        "version": contract["version"],
        "base_path": contract["base_path"],
    }

def get_item(item_id):
    row = db.execute(
        "select * from workflow_items where id = ?",
        (item_id,),
    ).fetchone()

    if not row:
        raise ValueError(f"workflow item not found: {item_id}")

    return row_to_dict(row)

def get_allowed_actions(item_id):
    item = get_item(item_id)
    status = item["status"]

    buttons = button_matrix["buttons_by_status"].get(status, [])

    return {
        "workflow_item_id": item_id,
        "status": status,
        "actions": buttons,
    }

def get_events(item_id):
    rows = db.execute(
        "select * from workflow_events where workflow_item_id = ? order by created_at",
        (item_id,),
    ).fetchall()

    return [row_to_dict(row) for row in rows]

def get_receipts(item_id):
    rows = db.execute(
        "select * from workflow_receipts where workflow_item_id = ? order by created_at",
        (item_id,),
    ).fetchall()

    return [row_to_dict(row) for row in rows]

def post_action(item_id, action, actor, note="", metadata=None):
    metadata = metadata or {}
    item = get_item(item_id)
    before_status = item["status"]

    allowed = rules["actions"].get(before_status, {})
    if action not in allowed:
        raise ValueError(f"invalid action {action} for status {before_status}")

    after_status = allowed[action]
    ts = now_utc()

    action_id = f"act_mock_api_{action}_{ts.replace(':', '').replace('.', '')}"
    event_id = f"evt_mock_api_{action}_{ts.replace(':', '').replace('.', '')}"

    receipt_required = action in set(rules["receipt_required_actions"])
    receipt_id = None

    if receipt_required:
        receipt_id = f"rcpt_mock_api_{action}_{ts.replace(':', '').replace('.', '')}"

    db.execute(
        """
        INSERT INTO workflow_actions (
          id, workflow_item_id, action_type, actor, status_before, status_after,
          result, error, metadata_json, receipt_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            action_id,
            item_id,
            action,
            actor,
            before_status,
            after_status,
            "ok",
            "",
            json.dumps(metadata, sort_keys=True),
            receipt_id,
            ts,
        ),
    )

    db.execute(
        """
        INSERT INTO workflow_events (
          id, workflow_item_id, event_type, actor, note, before_status, after_status,
          metadata_json, receipt_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            item_id,
            action,
            actor,
            note,
            before_status,
            after_status,
            json.dumps(metadata, sort_keys=True),
            receipt_id,
            ts,
        ),
    )

    if receipt_required:
        db.execute(
            """
            INSERT INTO workflow_receipts (
              id, workflow_item_id, task_id, receipt_type, receipt_path, receipt_hash,
              actor, action, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                receipt_id,
                item_id,
                None,
                "mock_api_transition",
                str(receipt_path),
                "",
                actor,
                action,
                ts,
            ),
        )

    db.execute(
        """
        UPDATE workflow_items
        SET status = ?, updated_at = ?
        WHERE id = ?
        """,
        (after_status, ts, item_id),
    )

    db.commit()

    return {
        "ok": True,
        "workflow_item_id": item_id,
        "action": action,
        "before_status": before_status,
        "after_status": after_status,
        "receipt_required": receipt_required,
        "receipt_id": receipt_id,
    }

item_id = "wf_universal_172_sample_20260520"

results = {
    "generated_at_utc": now_utc(),
    "status": api_status(),
    "initial_item": get_item(item_id),
    "allowed_before": get_allowed_actions(item_id),
    "post_archive": post_action(
        item_id=item_id,
        action="archive",
        actor="alexandria",
        note="Mock API archived completed sample workflow.",
    ),
    "item_after_archive": get_item(item_id),
    "allowed_after_archive": get_allowed_actions(item_id),
    "post_restore": post_action(
        item_id=item_id,
        action="restore",
        actor="alexandria",
        note="Mock API restored archived sample workflow.",
    ),
    "item_after_restore": get_item(item_id),
    "events": get_events(item_id),
    "receipts": get_receipts(item_id),
}

if results["status"]["ok"] is not True:
    raise SystemExit("status endpoint failed")

if results["post_archive"]["after_status"] != "archived":
    raise SystemExit("archive action failed")

if results["post_restore"]["after_status"] != "done":
    raise SystemExit("restore action failed")

if results["item_after_restore"]["status"] != "done":
    raise SystemExit("final status should be done after restore")

if len(results["events"]) < 7:
    raise SystemExit("expected at least 7 events after action runner + mock API actions")

if len(results["receipts"]) < 6:
    raise SystemExit("expected at least 6 receipts after archive receipt")

smoke_json_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

lines = [
    "# RoadWork Mock API Smoke v0",
    "",
    f"Generated at UTC: {results['generated_at_utc']}",
    "",
    f"Status endpoint OK: {results['status']['ok']}",
    f"Initial status: {results['initial_item']['status']}",
    f"Archive result: {results['post_archive']['before_status']} -> {results['post_archive']['after_status']}",
    f"Restore result: {results['post_restore']['before_status']} -> {results['post_restore']['after_status']}",
    f"Final status: {results['item_after_restore']['status']}",
    f"Events: {len(results['events'])}",
    f"Receipts: {len(results['receipts'])}",
    "",
    "## Allowed actions after restore",
    "",
]

for button in results["allowed_after_archive"]["actions"]:
    lines.append(f"- {button['label']} `{button['action']}` -> `{button['to_status']}`")

smoke_md_path.write_text("\n".join(lines) + "\n")

receipt_path.write_text(f"""# RoadWork Mock API Smoke v0 Receipt

Date:
2026-05-20

Local root:
~/blackroad/orgs

Action:
Ran local mock API smoke test against the RoadWork workflow SQLite sample.

Mocked endpoints:
- GET /api/workflow/status
- GET /api/workflow/items/:id
- GET /api/workflow/items/:id/allowed-actions
- POST /api/workflow/items/:id/actions
- GET /api/workflow/items/:id/events
- GET /api/workflow/items/:id/receipts

Files:
- _canon/workflow/api/roadwork_mock_api_smoke_v0.json
- _canon/workflow/api/ROADWORK_MOCK_API_SMOKE_V0.md
- reports/tmp/roadwork_mock_api_smoke_v0.sqlite

Validation:
- status endpoint: OK
- archive transition: done -> archived
- restore transition: archived -> done
- final status: {results['item_after_restore']['status']}
- events after smoke: {len(results['events'])}
- receipts after smoke: {len(results['receipts'])}

Status:
local_mock_api_smoke_validated

Policy:
- Local files only.
- No server started.
- No GitHub repos changed.
- No secrets touched.
- No generated runtime artifacts committed.
""")

print("status_ok:", results["status"]["ok"])
print("archive:", results["post_archive"]["before_status"], "->", results["post_archive"]["after_status"])
print("restore:", results["post_restore"]["before_status"], "->", results["post_restore"]["after_status"])
print("final_status:", results["item_after_restore"]["status"])
print("events:", len(results["events"]))
print("receipts:", len(results["receipts"]))
print("wrote", smoke_json_path)
print("wrote", smoke_md_path)
print("wrote", smoke_db_path)
print("wrote", receipt_path)
