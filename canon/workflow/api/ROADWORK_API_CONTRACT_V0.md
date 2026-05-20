# RoadWork API Contract v0

Generated at UTC: 2026-05-20T17:14:04.059930+00:00

Status: planned_api_contract

Base path: `/api/workflow`

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/workflow/status` | Return API health and contract version. |
| GET | `/api/workflow/items` | List workflow items with filters. |
| POST | `/api/workflow/items` | Create a new workflow item from RoadWire, OneWay, manual input, API, or agent. |
| GET | `/api/workflow/items/:id` | Read one workflow item with task counts and current state. |
| GET | `/api/workflow/items/:id/tasks` | List tasks and subtasks attached to a workflow item. |
| GET | `/api/workflow/items/:id/allowed-actions` | Return valid action buttons for the item current status. |
| POST | `/api/workflow/items/:id/actions` | Run a validated workflow action such as claim, start_work, set_awaiting, complete, archive, or reopen. |
| GET | `/api/workflow/items/:id/events` | List event history for one workflow item. |
| GET | `/api/workflow/items/:id/actions` | List action history for one workflow item. |
| GET | `/api/workflow/items/:id/receipts` | List receipts linked to one workflow item. |
| GET | `/api/workflow/items/:id/timeline` | List due dates, SLA deadlines, escalations, and awaiting timeline events. |
| GET | `/api/workflow/rules/transitions` | Return transition rules for statuses and actions. |
| GET | `/api/workflow/ui/action-button-matrix` | Return UI button matrix for all statuses. |
| GET | `/api/workflow/templates/universal-172` | Return the Universal 172-Step Repeatable Process template. |
| POST | `/api/workflow/templates/universal-172/instantiate` | Create a workflow item with 172 linked tasks from the Universal 172 template. |

## Honesty Rules

- This is a planned API contract, not an implemented server.
- Every state-changing POST must validate transition rules.
- Receipt-required actions must produce receipt rows.
- Do not expose secrets, tokens, source payloads, or private data by default.
- All statuses must remain compatible with workflow_transition_rules_v0.
