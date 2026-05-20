# Workflow Action Sequence v0

Workflow: WF-2026-0520-0001

Initial status: received
Final status: done

## Counts

- workflow_items: 1
- workflow_tasks: 172
- workflow_actions: 5
- workflow_events: 5
- workflow_awaiting_log: 1
- workflow_receipts: 5

## Sequence

- received --claim--> triaged receipt=rcpt_workflow_runner_v0_01
- triaged --start_work--> in_progress receipt=rcpt_workflow_runner_v0_02
- in_progress --set_awaiting--> awaiting receipt=rcpt_workflow_runner_v0_03
- awaiting --resolve_awaiting--> in_progress receipt=rcpt_workflow_runner_v0_04
- in_progress --complete--> done receipt=rcpt_workflow_runner_v0_05
