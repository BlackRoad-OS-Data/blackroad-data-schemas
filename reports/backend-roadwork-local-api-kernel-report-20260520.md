# RoadWork Local API Kernel — Report (2026-05-20)

Status: **GREEN — proof_only / local_only / production: false**

## What this is

A stdlib-only HTTP kernel (Python 3 `http.server`) that reads canonical workflow
files from this repo and serves them over GET endpoints on `127.0.0.1:8790`.

It is the smallest backend that can answer "do the canon files load, parse, and
expose through a contract surface?" with a terminal-verifiable yes/no.

## What this is NOT

- not deployed anywhere
- not connected to Gmail, Slack, any provider, any external API
- not bound to any non-loopback address
- not a database server (no driver imported, no connection opened)
- not authenticated (loopback only)
- no secrets read or written
- no mutating endpoints

## Files added on branch `backend-roadwork-local-api-kernel`

- `backend/roadwork_api_kernel.py` — the kernel (Python stdlib only)
- `backend/README.md` — operator-facing notes
- `tools/roadcheck_backend_roadwork.py` — terminal smoke + check
- `reports/backend-roadwork-local-api-kernel-report-20260520.md` — this file
- `reports/backend-orgs-session-start-audit-20260520.md` — pre-work audit
- `receipts/backend-roadwork-local-api-kernel-receipt-20260520.md` — receipt

## Endpoints

| Path | Method | Canon source |
|---|---|---|
| `/api/health` | GET | self-reported |
| `/api/workflow/status` | GET | `canon/workflow/workflow_state_model.json` |
| `/api/workflow/schema` | GET | `canon/workflow/sql/roadwork_workflow_schema_v0.sql` |
| `/api/workflow/rules` | GET | `canon/workflow/rules/workflow_transition_rules_v0.json` |
| `/api/workflow/templates/universal-172` | GET | `canon/workflow/universal_172_process.json` |
| `/api/workflow/sample` | GET | `canon/workflow/samples/universal_172_sample_workflow.json` |
| `/api/workflow/actions` | GET | `canon/workflow/runs/workflow_action_sequence_v0.json` |
| `/api/workflow/receipts/recent` | GET | `receipts/*.md` (name + mtime listing only) |

Every response carries:

```
production: false
mode:       local_only
implemented: proof_only
```

`POST` returns `405`.

## Terminal checks (all GREEN)

```
python3 -m py_compile backend/roadwork_api_kernel.py    # OK
python3 backend/roadwork_api_kernel.py --smoke          # GREEN, 8/8 endpoints
python3 tools/roadcheck_backend_roadwork.py             # GREEN, 21/21 checks
```

Checks performed:
- backend file exists
- kernel py_compile clean
- kernel module imports
- all 7 required canon files present
- no forbidden external strings (Gmail / Slack / AWS / OpenAI / Anthropic / private-key markers)
- each of 8 documented endpoints dispatches `200` with proof envelope
- `/api/health` lists every endpoint
- no mutating routes registered

## `./roados` integration

Skipped on this branch. `./roados` is not present on `blackroad-lab`; it only
exists on the still-open `roados-email-workflow-proof` branch (PR #7). When that
PR merges, the planned subcommands are:

```
./roados backend-check   -> python3 tools/roadcheck_backend_roadwork.py
./roados backend-smoke   -> python3 backend/roadwork_api_kernel.py --smoke
./roados backend-serve   -> python3 backend/roadwork_api_kernel.py
```

They can be added without touching existing `check/doctor/report`. Not done in
this branch to keep the diff strictly additive and lab-rooted.

## What is still mock / local / planned

- everything in this branch is local proof only
- the SQL schema is served as text; no DB is created or migrated
- receipts list is filename + mtime only; no receipt content is exposed
- no auth, no rate limit, no audit log
- not yet integrated with the RoadOS HTML browser proof or with `./roados`

## Next safe backend step

1. Operator review of this PR.
2. After PR #7 merges, add the `./roados backend-*` wrappers on a follow-up.
3. Add a contract test comparing `/api/workflow/rules` payload against
   `canon/workflow/api/roadwork_api_contract_v0.json`.
