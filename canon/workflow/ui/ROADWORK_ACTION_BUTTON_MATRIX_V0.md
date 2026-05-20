# RoadWork Action Button Matrix v0

Generated at UTC: 2026-05-20T17:11:57.744594+00:00

Status: planned_ui_action_matrix

## `archived`

| Button | Action | Next status | Kind | Receipt required |
|---|---|---|---|---|
| Restore | `restore` | `done` | primary | False |

## `awaiting`

| Button | Action | Next status | Kind | Receipt required |
|---|---|---|---|---|
| Resolve Awaiting | `resolve_awaiting` | `in_progress` | primary | True |
| Escalate | `escalate` | `blocked` | warning | False |
| Reassign | `reassign` | `awaiting` | secondary | False |
| Cancel | `cancel` | `done` | danger | False |

## `blocked`

| Button | Action | Next status | Kind | Receipt required |
|---|---|---|---|---|
| Resolve Blocker | `resolve_blocker` | `in_progress` | primary | True |
| Set Awaiting | `set_awaiting` | `awaiting` | warning | True |
| Close | `close` | `done` | danger | False |

## `collaborating`

| Button | Action | Next status | Kind | Receipt required |
|---|---|---|---|---|
| Update Progress | `update_progress` | `collaborating` | secondary | False |
| Set Awaiting | `set_awaiting` | `awaiting` | warning | True |
| Complete | `complete` | `done` | success | True |
| Block | `block` | `blocked` | danger | False |

## `done`

| Button | Action | Next status | Kind | Receipt required |
|---|---|---|---|---|
| Reopen | `reopen` | `in_progress` | warning | True |
| Archive | `archive` | `archived` | secondary | True |

## `in_progress`

| Button | Action | Next status | Kind | Receipt required |
|---|---|---|---|---|
| Update Progress | `update_progress` | `in_progress` | secondary | False |
| Set Awaiting | `set_awaiting` | `awaiting` | warning | True |
| Collaborate | `collaborate` | `collaborating` | secondary | False |
| Complete | `complete` | `done` | success | True |
| Block | `block` | `blocked` | danger | False |

## `received`

| Button | Action | Next status | Kind | Receipt required |
|---|---|---|---|---|
| Mark Read | `mark_read` | `triaged` | secondary | False |
| Claim | `claim` | `triaged` | primary | True |
| Close | `close` | `done` | danger | False |
| Escalate | `escalate` | `blocked` | warning | False |

## `triaged`

| Button | Action | Next status | Kind | Receipt required |
|---|---|---|---|---|
| Start Work | `start_work` | `in_progress` | primary | True |
| Set Awaiting | `set_awaiting` | `awaiting` | warning | True |
| Collaborate | `collaborate` | `collaborating` | secondary | False |
| Close | `close` | `done` | danger | False |
| Escalate | `escalate` | `blocked` | warning | False |

