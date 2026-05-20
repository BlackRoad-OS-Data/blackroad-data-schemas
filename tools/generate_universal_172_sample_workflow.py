import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "canon/workflow"
SAMPLES = WORKFLOW / "samples"
REPORTS = ROOT / "reports"

process_path = WORKFLOW / "universal_172_process.json"
schema_path = WORKFLOW / "sql/roadwork_workflow_schema_v0.sql"
db_path = ROOT / "reports/tmp/roadwork_universal_172_sample.sqlite"
json_path = SAMPLES / "universal_172_sample_workflow.json"
md_path = SAMPLES / "universal_172_sample_workflow.md"
receipt_path = REPORTS / "universal-172-sample-workflow-receipt-20260520.md"

SAMPLES.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)
db_path.parent.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

process = json.loads(process_path.read_text())
steps = process["steps"]

workflow_item = {
    "id": "wf_universal_172_sample_20260520",
    "index_id": "WF-2026-0520-0001",
    "title": "Universal 172-Step Repeatable Process Sample",
    "description": "Sample RoadWork workflow generated from the Universal 172-step canon template.",
    "source": "local_canon",
    "source_id": "universal_172_process.json",
    "status": "received",
    "received_at": now,
    "read_at": None,
    "read_by": None,
    "claimed_by": None,
    "claimed_at": None,
    "is_collaborative": 1,
    "awaiting_type": None,
    "awaiting_since": None,
    "awaiting_owner": None,
    "awaiting_note": None,
    "due_at": None,
    "sla_response_at": None,
    "sla_resolution_at": None,
    "escalation_at": None,
    "created_at": now,
    "updated_at": now,
}

tasks = []
events = []

events.append({
    "id": "evt_universal_172_received",
    "workflow_item_id": workflow_item["id"],
    "event_type": "received",
    "actor": "alexandria",
    "note": "Generated sample workflow item from Universal 172-step process.",
    "before_status": None,
    "after_status": "received",
    "metadata_json": json.dumps({"source": "universal_172_process.json"}),
    "receipt_id": "rcpt_universal_172_sample_workflow_20260520",
    "created_at": now,
})

for step in steps:
    task_id = "task_" + step["step_id"].lower().replace("-", "_")
    tasks.append({
        "id": task_id,
        "workflow_item_id": workflow_item["id"],
        "title": step["title"],
        "description": f"Macro {step['macro_number']}: {step['macro_title']} | Step {step['step_number']}",
        "status": "unclaimed",
        "owner": None,
        "priority": "normal",
        "due_at": None,
        "claimed_by": None,
        "claimed_at": None,
        "completed_at": None,
        "receipt_id": None,
        "created_at": now,
        "updated_at": now,
        "step_id": step["step_id"],
        "step_number": step["step_number"],
        "macro_number": step["macro_number"],
        "macro_title": step["macro_title"],
        "macro_step_number": step["macro_step_number"],
    })

payload = {
    "generated_at_utc": now,
    "workflow_item": workflow_item,
    "task_count": len(tasks),
    "event_count": len(events),
    "tasks": tasks,
    "events": events,
}

json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

if db_path.exists():
    db_path.unlink()

db = sqlite3.connect(db_path)
db.executescript(schema_path.read_text())

db.execute("""
INSERT INTO workflow_items (
  id, index_id, title, description, source, source_id, status, received_at,
  read_at, read_by, claimed_by, claimed_at, is_collaborative,
  awaiting_type, awaiting_since, awaiting_owner, awaiting_note,
  due_at, sla_response_at, sla_resolution_at, escalation_at,
  created_at, updated_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    workflow_item["id"], workflow_item["index_id"], workflow_item["title"],
    workflow_item["description"], workflow_item["source"], workflow_item["source_id"],
    workflow_item["status"], workflow_item["received_at"], workflow_item["read_at"],
    workflow_item["read_by"], workflow_item["claimed_by"], workflow_item["claimed_at"],
    workflow_item["is_collaborative"], workflow_item["awaiting_type"],
    workflow_item["awaiting_since"], workflow_item["awaiting_owner"],
    workflow_item["awaiting_note"], workflow_item["due_at"], workflow_item["sla_response_at"],
    workflow_item["sla_resolution_at"], workflow_item["escalation_at"],
    workflow_item["created_at"], workflow_item["updated_at"],
))

for task in tasks:
    db.execute("""
    INSERT INTO workflow_tasks (
      id, workflow_item_id, title, description, status, owner, priority, due_at,
      claimed_by, claimed_at, completed_at, receipt_id, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task["id"], task["workflow_item_id"], task["title"], task["description"],
        task["status"], task["owner"], task["priority"], task["due_at"],
        task["claimed_by"], task["claimed_at"], task["completed_at"],
        task["receipt_id"], task["created_at"], task["updated_at"],
    ))

for event in events:
    db.execute("""
    INSERT INTO workflow_events (
      id, workflow_item_id, event_type, actor, note, before_status, after_status,
      metadata_json, receipt_id, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event["id"], event["workflow_item_id"], event["event_type"], event["actor"],
        event["note"], event["before_status"], event["after_status"],
        event["metadata_json"], event["receipt_id"], event["created_at"],
    ))

db.commit()

workflow_count = db.execute("select count(*) from workflow_items").fetchone()[0]
task_count = db.execute("select count(*) from workflow_tasks").fetchone()[0]
event_count = db.execute("select count(*) from workflow_events").fetchone()[0]

if workflow_count != 1:
    raise SystemExit(f"expected 1 workflow item, got {workflow_count}")
if task_count != 172:
    raise SystemExit(f"expected 172 tasks, got {task_count}")
if event_count != 1:
    raise SystemExit(f"expected 1 event, got {event_count}")

md_lines = [
    "# Universal 172 Sample Workflow",
    "",
    f"Generated at UTC: {now}",
    "",
    f"Workflow item: {workflow_item['index_id']}",
    f"Title: {workflow_item['title']}",
    f"Status: {workflow_item['status']}",
    "",
    f"Tasks: {task_count}",
    f"Events: {event_count}",
    "",
    "## First 10 tasks",
    "",
]

for task in tasks[:10]:
    md_lines.append(f"- {task['step_id']} — {task['title']}")

md_lines.extend([
    "",
    "## Last task",
    "",
    f"- {tasks[-1]['step_id']} — {tasks[-1]['title']}",
    "",
])

md_path.write_text("\n".join(md_lines))

receipt_path.write_text(f"""# Universal 172 Sample Workflow Receipt

Date:
2026-05-20

Local root:
~/blackroad/orgs

Action:
Generated a sample RoadWork workflow item and 172 linked workflow tasks from the Universal 172-Step Repeatable Process canon template.

Files:
- _canon/workflow/samples/universal_172_sample_workflow.json
- _canon/workflow/samples/universal_172_sample_workflow.md
- reports/tmp/roadwork_universal_172_sample.sqlite

Validation:
- workflow_items: {workflow_count}
- workflow_tasks: {task_count}
- workflow_events: {event_count}
- SQLite insert validation: OK

Status:
local_sample_generated

Policy:
- Local files only.
- No GitHub repos changed.
- No secrets touched.
- No generated runtime artifacts committed.
""")

print("workflow_items:", workflow_count)
print("workflow_tasks:", task_count)
print("workflow_events:", event_count)
print("wrote", json_path)
print("wrote", md_path)
print("wrote", db_path)
print("wrote", receipt_path)
