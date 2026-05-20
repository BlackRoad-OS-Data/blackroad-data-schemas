# RoadWork Mock API Smoke v0 Receipt

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
- final status: done
- events after smoke: 7
- receipts after smoke: 6

Status:
local_mock_api_smoke_validated

Policy:
- Local files only.
- No server started.
- No GitHub repos changed.
- No secrets touched.
- No generated runtime artifacts committed.
