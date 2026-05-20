import sqlite3
from pathlib import Path

sql_path = Path("canon/workflow/sql/roadwork_workflow_schema_v0.sql")
sql = sql_path.read_text()

db = sqlite3.connect(":memory:")
db.executescript(sql)

tables = [
    row[0]
    for row in db.execute("select name from sqlite_master where type='table' order by name")
]

print("tables:", len(tables))
for table in tables:
    print(table)

expected = {
    "workflow_items",
    "workflow_tasks",
    "workflow_subtasks",
    "workflow_collaborators",
    "workflow_events",
    "workflow_actions",
    "workflow_awaiting_log",
    "workflow_timeline_events",
    "workflow_receipts",
}

missing = expected - set(tables)
if missing:
    raise SystemExit(f"missing tables: {sorted(missing)}")

print("workflow schema validation OK")
