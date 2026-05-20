# RoadWork Local UI Proof

Status:
local_proof_only

Branch:
roadwork-local-ui-proof

Purpose:
Static local RoadWork UI proof showing workflow columns, one sample workflow item, allowed action buttons, Universal 172 task count, and receipt placeholder.

This is not production RoadWork.
This is not deployed.
This does not connect email, Slack, customers, APIs, production data, or private data.

Files:
- site/roadwork_local_ui_proof.html
- tools/validate_roadwork_local_ui_proof.py

Validate:
python3 tools/validate_roadwork_local_ui_proof.py

Run locally:
python3 -m http.server 8791

Open:
http://127.0.0.1:8791/site/roadwork_local_ui_proof.html

Honesty:
This reads static local canon JSON files only.
It proves UI shape, not production readiness.
