# RoadWork Local API Proof

Status:
local_proof_only

Branch:
roadwork-local-api-proof

Purpose:
Tiny local-only RoadWork API proof using Python standard library.

This is not production RoadWork.
This is not a deployed server.
This does not connect email, Slack, APIs, customers, or private data.

Endpoints:
- GET /api/workflow/status
- GET /api/workflow/templates/universal-172
- GET /api/workflow/rules/transitions
- GET /api/workflow/ui/action-button-matrix
- GET /api/workflow/items/sample
- GET /api/workflow/items/sample/allowed-actions

Smoke test:
python3 tools/roadwork_local_api_proof.py --smoke

Run local server:
python3 tools/roadwork_local_api_proof.py --port 8789

Honesty:
This reads local canon files only.
It proves API shape, not production readiness.
