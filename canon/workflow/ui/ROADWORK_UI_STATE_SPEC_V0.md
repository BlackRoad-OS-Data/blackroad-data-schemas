# RoadWork UI State Spec v0

Generated at UTC: 2026-05-20T17:10:48.756299+00:00

Status: planned_ui_spec

## Views

### Inbox

Everything received from RoadWire, OneWay, forms, APIs, agents, or manual entry.

### Workflow Board

Kanban-style view grouped by workflow status.

### Timeline

SLA, due date, escalation, awaiting, and receipt timeline.

### 172-Step Process

Universal 172-step repeatable process as linked tasks.

## Status Columns

### New / Received `received`

- Badge: NEW
- Meaning: Item entered the system but is not owned yet.
- Actions: mark_read, claim, close, escalate

### Triaged `triaged`

- Badge: TRIAGED
- Meaning: Item has been read/claimed and is ready to start.
- Actions: start_work, set_awaiting, collaborate, close, escalate

### In Progress `in_progress`

- Badge: ACTIVE
- Meaning: Work is actively moving.
- Actions: update_progress, set_awaiting, collaborate, complete, block

### Awaiting `awaiting`

- Badge: AWAITING
- Meaning: Work is paused for a typed reason.
- Actions: resolve_awaiting, escalate, reassign, cancel

### Collaborating `collaborating`

- Badge: COLLAB
- Meaning: Multiple humans or agents are involved.
- Actions: update_progress, set_awaiting, complete, block

### Blocked `blocked`

- Badge: BLOCKED
- Meaning: Work cannot proceed without a blocker being resolved.
- Actions: resolve_blocker, set_awaiting, close

### Done `done`

- Badge: DONE
- Meaning: Work completed or closed.
- Actions: reopen, archive

### Archived `archived`

- Badge: ARCHIVED
- Meaning: Removed from active work but recoverable.
- Actions: restore

## Detail Panels

- summary
- actions
- 172_tasks
- subtasks
- awaiting
- timeline
- collaborators
- events
- receipts
- source_payload

## Honesty Rules

- Do not show implemented status unless receipts/tests prove it.
- Show initialized-shell when the repo or workflow only has structure.
- Show partial when work exists but is not verified.
- Show blocked when access, disk, permissions, or decisions stop progress.
- Every major action should create an event or receipt.
