# RoadWork Workflow Schema v0 Receipt

Date:
2026-05-20

Local root:
~/blackroad/orgs

Action:
Created and validated local SQL schema for the BlackRoad RoadWork Workflow Kernel.

Files:
- _canon/workflow/sql/roadwork_workflow_schema_v0.sql
- scripts/validate_workflow_schema.py

Validation:
SQLite in-memory schema parse and table check.

Tables:
- workflow_items
- workflow_tasks
- workflow_subtasks
- workflow_collaborators
- workflow_events
- workflow_actions
- workflow_awaiting_log
- workflow_timeline_events
- workflow_receipts

Purpose:
Turn the workflow state model and Universal 172-step process into a database-ready structure for RoadWork, RoadMap, RoadTrip, OneWay, RoadWire, CarKeys, and RoadChain.

Status:
planned_schema_validated_locally

Policy:
- Local canon/schema files only.
- No GitHub repos changed.
- No secrets touched.
- No generated runtime artifacts committed.
