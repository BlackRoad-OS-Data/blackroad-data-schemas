# backend/ — RoadWork local API kernel (proof only)

Status: **local_only / proof_only / production: false**

This directory holds a stdlib-only HTTP kernel that serves the workflow canon
files in this repo to local terminal smoke checks. It is not a product. It does
not connect to Gmail, Slack, any provider, any database server, or any external
API. It binds only to `127.0.0.1`. It does not read or write secrets.

## Files

- `roadwork_api_kernel.py` — the kernel. Read-only GET endpoints over canon.

## Run

```
python3 backend/roadwork_api_kernel.py            # serve on 127.0.0.1:8790
python3 backend/roadwork_api_kernel.py --smoke    # in-process smoke (no socket)
python3 backend/roadwork_api_kernel.py --port N   # alternate port
```

## Endpoints (GET only)

| Path | Source canon file |
|---|---|
| `/api/health` | self-reported; lists routes and canon presence |
| `/api/workflow/status` | `canon/workflow/workflow_state_model.json` |
| `/api/workflow/schema` | `canon/workflow/sql/roadwork_workflow_schema_v0.sql` |
| `/api/workflow/rules` | `canon/workflow/rules/workflow_transition_rules_v0.json` |
| `/api/workflow/templates/universal-172` | `canon/workflow/universal_172_process.json` |
| `/api/workflow/sample` | `canon/workflow/samples/universal_172_sample_workflow.json` |
| `/api/workflow/actions` | `canon/workflow/runs/workflow_action_sequence_v0.json` |
| `/api/workflow/receipts/recent` | `receipts/*.md` listing (names + mtime only) |

Every response body includes:

```json
{
  "production": false,
  "mode": "local_only",
  "implemented": "proof_only",
  "kernel": "roadwork_api_kernel",
  "kernel_version": "0.1.0",
  "served_at_utc": "...",
  "data": { ... }
}
```

`POST` returns `405`. There are no mutating endpoints.

## Terminal check

```
python3 tools/roadcheck_backend_roadwork.py
```

Reports GREEN / YELLOW / RED.

## What this is not

- not deployed
- not a product surface
- not connected to Gmail, Slack, or any provider
- not bound to anything except `127.0.0.1`
- not a database server
- not authenticated
- not safe for any non-local network
