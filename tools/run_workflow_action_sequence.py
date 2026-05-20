import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "canon/workflow"
REPORTS = ROOT / "reports"

schema_path = WORKFLOW / "sql/roadwork_workflow_schema_v0.sql"
sample_path = WORKFLOW / "samples/universal_172_sample_workflow.json"
rules_path = WORKFLOW / "rules/workflow_transition_rules_v0.json"

run_json_path = WORKFLOW / "runs/workflow_action_sequence_v0.json"
run_md_path = WORKFLOW / "runs/workflow_action_sequence_v0.md"
db_path = ROOT / "reports/tmp/roadwork_action_runner_v0.sqlite"
receipt_path = REPORTS / "workflow-action-runner-v0-receipt-20260520.md"

WORKFLOW.joinpath("runs").mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)
db_path.parent.mkdir(parents=True, exist_ok=True)

sample = json.loads(sample_path.read_text())
rules = json.loads(rules_path.read_text())

workflow_item = dict(sample["workflow_item"])
tasks = sample["tasks"]

sequence = [
    {
        "action": "claim",
        "actor": "alexandria",
        "note": "Operator claimed workflow item.",
        "metadata": {"claimed_by": "alexandria"},
    },
    {
        "action": "start_work",
        "actor": "alexandria",
        "note": "Operator started workflow work.",
        "metadata": {},
    },
    {
        "action": "set_awaiting",
        "actor": "alexandria",
        "note": "Workflow is awaiting operator approval for next execution phase.",
        "metadata": {
            "awaiting_type": "operator_approval",
            "awaiting_owner": "alexandria",
            "awaiting_note": "Approve next phase before generating repo/project issues.",
        },
    },
    {
        "action": "resolve_awaiting",
        "actor": "alexandria",
        "note": "Operator approval received.",
        "metadata": {},
    },
    {
        "action": "complete",
        "actor": "alexandria",
        "note": "Sample transition sequence completed.",
        "metadata": {},
    },
]

def transition(status, action):
    allowed = rules["actions"].get(status, {})
    if action not in allowed:
        raise ValueError(f"invalid transition: {status} + {action}")
    return allowed[action]

def now_utc():
    return datetime.now(timezone.utc).isoformat()

if db_path.exists():
    db_path.unlink()

db = sqlite3.connect(db_path)
db.executescript(schema_path.read_text())

created_at = now_utc()

db.execute("""
INSERT INTO workflow_items (
  id, index_id, title, description, source, source_id, status, received_at,
  read_at, read_by, claimed_by, claimed_at, is_collaborative,
  awaiting_type, awaiting_since, awaiting_owner, awaiting_note,
  due_at, sla_response_at, sla_resolution_at, escalation_at,
  created_at, updated_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    workflow_item["id"],
    workflow_item["index_id"],
    workflow_item["title"],
    workflow_item["description"],
    workflow_item["source"],
    workflow_item["source_id"],
    workflow_item["status"],
    workflow_item["received_at"],
    workflow_item["read_at"],
    workflow_item["read_by"],
    workflow_item["claimed_by"],
    workflow_item["claimed_at"],
    workflow_item["is_collaborative"],
    workflow_item["awaiting_type"],
    workflow_item["awaiting_since"],
    workflow_item["awaiting_owner"],
    workflow_item["awaiting_note"],
    workflow_item["due_at"],
    workflow_item["sla_response_at"],
    workflow_item["sla_resolution_at"],
    workflow_item["escalation_at"],
    workflow_item["created_at"],
    workflow_item["updated_at"],
))

for task in tasks:
    db.execute("""
    INSERT INTO workflow_tasks (
      id, workflow_item_id, title, description, status, owner, priority, due_at,
      claimed_by, claimed_at, completed_at, receipt_id, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task["id"],
        task["workflow_item_id"],
        task["title"],
        task["description"],
        task["status"],
        task["owner"],
        task["priority"],
        task["due_at"],
        task["claimed_by"],
        task["claimed_at"],
        task["completed_at"],
        task["receipt_id"],
        task["created_at"],
        task["updated_at"],
    ))

run_events = []
run_actions = []
run_receipts = []

current_status = workflow_item["status"]

for idx, step in enumerate(sequence, start=1):
    action = step["action"]
    actor = step["actor"]
    note = step["note"]
    metadata = step["metadata"]

    before_status = current_status
    after_status = transition(before_status, action)
    ts = now_utc()

    action_id = f"act_workflow_runner_v0_{idx:02d}"
    event_id = f"evt_workflow_runner_v0_{idx:02d}"
    receipt_id = f"rcpt_workflow_runner_v0_{idx:02d}"

    run_actions.append({
        "id": action_id,
        "workflow_item_id": workflow_item["id"],
        "action_type": action,
        "actor": actor,
        "status_before": before_status,
        "status_after": after_status,
        "result": "ok",
        "error": "",
        "metadata_json": json.dumps(metadata, sort_keys=True),
        "receipt_id": receipt_id,
        "created_at": ts,
    })

    run_events.append({
        "id": event_id,
        "workflow_item_id": workflow_item["id"],
        "event_type": action,
        "actor": actor,
        "note": note,
        "before_status": before_status,
        "after_status": after_status,
        "metadata_json": json.dumps(metadata, sort_keys=True),
        "receipt_id": receipt_id,
        "created_at": ts,
    })

    run_receipts.append({
        "id": receipt_id,
        "workflow_item_id": workflow_item["id"],
        "task_id": None,
        "receipt_type": "workflow_transition",
        "receipt_path": str(receipt_path),
        "receipt_hash": "",
        "actor": actor,
        "action": action,
        "created_at": ts,
    })

    if action == "claim":
        workflow_item["claimed_by"] = metadata.get("claimed_by", actor)
        workflow_item["claimed_at"] = ts

    if action == "set_awaiting":
        workflow_item["awaiting_type"] = metadata.get("awaiting_type")
        workflow_item["awaiting_since"] = ts
        workflow_item["awaiting_owner"] = metadata.get("awaiting_owner")
        workflow_item["awaiting_note"] = metadata.get("awaiting_note", "")

        db.execute("""
        INSERT INTO workflow_awaiting_log (
          id, workflow_item_id, awaiting_type, awaiting_owner, awaiting_since,
          resolved_at, resolved_by, resolution_note, receipt_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "awaiting_workflow_runner_v0_01",
            workflow_item["id"],
            workflow_item["awaiting_type"],
            workflow_item["awaiting_owner"],
            workflow_item["awaiting_since"],
            None,
            None,
            "",
            receipt_id,
        ))

    if action == "resolve_awaiting":
        db.execute("""
        UPDATE workflow_awaiting_log
        SET resolved_at = ?, resolved_by = ?, resolution_note = ?, receipt_id = ?
        WHERE workflow_item_id = ? AND resolved_at IS NULL
        """, (
            ts,
            actor,
            "Awaiting condition resolved by action runner.",
            receipt_id,
            workflow_item["id"],
        ))

        workflow_item["awaiting_type"] = None
        workflow_item["awaiting_since"] = None
        workflow_item["awaiting_owner"] = None
        workflow_item["awaiting_note"] = None

    current_status = after_status
    workflow_item["status"] = current_status
    workflow_item["updated_at"] = ts

    db.execute("""
    INSERT INTO workflow_actions (
      id, workflow_item_id, action_type, actor, status_before, status_after,
      result, error, metadata_json, receipt_id, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        action_id,
        workflow_item["id"],
        action,
        actor,
        before_status,
        after_status,
        "ok",
        "",
        json.dumps(metadata, sort_keys=True),
        receipt_id,
        ts,
    ))

    db.execute("""
    INSERT INTO workflow_events (
      id, workflow_item_id, event_type, actor, note, before_status, after_status,
      metadata_json, receipt_id, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        workflow_item["id"],
        action,
        actor,
        note,
        before_status,
        after_status,
        json.dumps(metadata, sort_keys=True),
        receipt_id,
        ts,
    ))

    db.execute("""
    INSERT INTO workflow_receipts (
      id, workflow_item_id, task_id, receipt_type, receipt_path, receipt_hash,
      actor, action, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        receipt_id,
        workflow_item["id"],
        None,
        "workflow_transition",
        str(receipt_path),
        "",
        actor,
        action,
        ts,
    ))

db.execute("""
UPDATE workflow_items
SET status = ?,
    claimed_by = ?,
    claimed_at = ?,
    awaiting_type = ?,
    awaiting_since = ?,
    awaiting_owner = ?,
    awaiting_note = ?,
    updated_at = ?
WHERE id = ?
""", (
    workflow_item["status"],
    workflow_item["claimed_by"],
    workflow_item["claimed_at"],
    workflow_item["awaiting_type"],
    workflow_item["awaiting_since"],
    workflow_item["awaiting_owner"],
    workflow_item["awaiting_note"],
    workflow_item["updated_at"],
    workflow_item["id"],
))

db.commit()

counts = {
    "workflow_items": db.execute("select count(*) from workflow_items").fetchone()[0],
    "workflow_tasks": db.execute("select count(*) from workflow_tasks").fetchone()[0],
    "workflow_actions": db.execute("select count(*) from workflow_actions").fetchone()[0],
    "workflow_events": db.execute("select count(*) from workflow_events").fetchone()[0],
    "workflow_awaiting_log": db.execute("select count(*) from workflow_awaiting_log").fetchone()[0],
    "workflow_receipts": db.execute("select count(*) from workflow_receipts").fetchone()[0],
}

final_status = db.execute(
    "select status from workflow_items where id = ?",
    (workflow_item["id"],),
).fetchone()[0]

if counts["workflow_items"] != 1:
    raise SystemExit("expected 1 workflow item")
if counts["workflow_tasks"] != 172:
    raise SystemExit("expected 172 workflow tasks")
if counts["workflow_actions"] != len(sequence):
    raise SystemExit("expected action count to match sequence")
if counts["workflow_events"] != len(sequence):
    raise SystemExit("expected event count to match sequence")
if counts["workflow_receipts"] != len(sequence):
    raise SystemExit("expected receipt count to match sequence")
if final_status != "done":
    raise SystemExit(f"expected final status done, got {final_status}")

payload = {
    "generated_at_utc": now_utc(),
    "workflow_item_id": workflow_item["id"],
    "index_id": workflow_item["index_id"],
    "initial_status": "received",
    "final_status": final_status,
    "sequence": sequence,
    "actions": run_actions,
    "events": run_events,
    "receipts": run_receipts,
    "counts": counts,
    "db_path": str(db_path),
}

run_json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

md = [
    "# Workflow Action Sequence v0",
    "",
    f"Workflow: {workflow_item['index_id']}",
    "",
    "Initial status: received",
    f"Final status: {final_status}",
    "",
    "## Counts",
    "",
]

for key, value in counts.items():
    md.append(f"- {key}: {value}")

md.extend(["", "## Sequence", ""])

for action in run_actions:
    md.append(
        f"- {action['status_before']} --{action['action_type']}--> {action['status_after']} "
        f"receipt={action['receipt_id']}"
    )

run_md_path.write_text("\n".join(md) + "\n")

receipt_path.write_text(f"""# Workflow Action Runner v0 Receipt

Date:
2026-05-20

Local root:
~/blackroad/orgs

Action:
Ran a local workflow action sequence against the Universal 172 sample workflow using validated transition rules.

Files:
- _canon/workflow/runs/workflow_action_sequence_v0.json
- _canon/workflow/runs/workflow_action_sequence_v0.md
- reports/tmp/roadwork_action_runner_v0.sqlite

Sequence:
- received --claim--> triaged
- triaged --start_work--> in_progress
- in_progress --set_awaiting--> awaiting
- awaiting --resolve_awaiting--> in_progress
- in_progress --complete--> done

Validation:
- workflow_items: {counts['workflow_items']}
- workflow_tasks: {counts['workflow_tasks']}
- workflow_actions: {counts['workflow_actions']}
- workflow_events: {counts['workflow_events']}
- workflow_awaiting_log: {counts['workflow_awaiting_log']}
- workflow_receipts: {counts['workflow_receipts']}
- final_status: {final_status}

Status:
local_action_runner_validated

Policy:
- Local files only.
- No GitHub repos changed.
- No secrets touched.
- No generated runtime artifacts committed.
""")

print("final_status:", final_status)
for key, value in counts.items():
    print(f"{key}:", value)
print("wrote", run_json_path)
print("wrote", run_md_path)
print("wrote", db_path)
print("wrote", receipt_path)
