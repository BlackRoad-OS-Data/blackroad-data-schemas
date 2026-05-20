import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]

html = (root / "site/roadwork_local_ui_proof.html").read_text()
sample = json.loads((root / "canon/workflow/samples/universal_172_sample_workflow.json").read_text())
matrix = json.loads((root / "canon/workflow/ui/roadwork_action_button_matrix_v0.json").read_text())
template = json.loads((root / "canon/workflow/universal_172_process.json").read_text())

required_html = [
    "RoadWork Local UI Proof",
    "LOCAL PROOF ONLY",
    "../canon/workflow/samples/universal_172_sample_workflow.json",
    "../canon/workflow/ui/roadwork_action_button_matrix_v0.json",
    "../canon/workflow/universal_172_process.json",
    "Receipt placeholder",
]

missing = [item for item in required_html if item not in html]
if missing:
    raise SystemExit(f"missing html markers: {missing}")

if sample["workflow_item"]["index_id"] != "WF-2026-0520-0001":
    raise SystemExit("sample workflow index mismatch")

if sample["task_count"] != 172:
    raise SystemExit("sample task count mismatch")

if template["step_count"] != 172:
    raise SystemExit("template step count mismatch")

status = sample["workflow_item"]["status"]
actions = matrix["buttons_by_status"].get(status, [])

if status != "received":
    raise SystemExit(f"expected sample status received, got {status}")

if len(actions) != 4:
    raise SystemExit(f"expected 4 received actions, got {len(actions)}")

print("roadwork local UI proof validation OK")
print("sample:", sample["workflow_item"]["index_id"])
print("status:", status)
print("template_steps:", template["step_count"])
print("allowed_actions:", len(actions))
