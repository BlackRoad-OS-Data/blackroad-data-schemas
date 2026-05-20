import json
from pathlib import Path

rules_path = Path("canon/workflow/rules/workflow_transition_rules_v0.json")
rules = json.loads(rules_path.read_text())

statuses = set(rules["statuses"])
actions = rules["actions"]

errors = []

for source_status, action_map in actions.items():
    if source_status not in statuses:
        errors.append(f"unknown source status: {source_status}")

    for action, target_status in action_map.items():
        if target_status not in statuses:
            errors.append(f"{source_status}.{action} points to unknown target: {target_status}")

required_tests = [
    ("received", "claim", "triaged"),
    ("triaged", "start_work", "in_progress"),
    ("in_progress", "set_awaiting", "awaiting"),
    ("awaiting", "resolve_awaiting", "in_progress"),
    ("in_progress", "complete", "done"),
    ("done", "archive", "archived"),
    ("archived", "restore", "done")
]

def transition(status, action):
    if status not in actions:
        raise ValueError(f"no actions defined for status: {status}")

    if action not in actions[status]:
        raise ValueError(f"invalid action {action} for status {status}")

    return actions[status][action]

for status, action, expected in required_tests:
    actual = transition(status, action)
    if actual != expected:
        errors.append(f"{status} + {action}: expected {expected}, got {actual}")

invalid_tests = [
    ("received", "archive"),
    ("archived", "complete"),
    ("done", "set_awaiting")
]

for status, action in invalid_tests:
    try:
        transition(status, action)
        errors.append(f"invalid transition incorrectly allowed: {status} + {action}")
    except ValueError:
        pass

if errors:
    for error in errors:
        print("ERROR:", error)
    raise SystemExit(1)

print("workflow transition rules validation OK")
print("statuses:", len(statuses))
print("source states with actions:", len(actions))
print("receipt-required actions:", len(rules["receipt_required_actions"]))
