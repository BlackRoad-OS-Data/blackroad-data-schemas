# Workflow Transition Rules v0 Receipt

Date:
2026-05-20

Local root:
~/blackroad/orgs

Action:
Created and validated BlackRoad Workflow Transition Rules v0.

Files:
- _canon/workflow/rules/workflow_transition_rules_v0.json
- scripts/validate_workflow_transitions.py

Validation:
- Statuses validated
- Source states validated
- Target states validated
- Required valid transitions tested
- Invalid transitions rejected

Purpose:
Prevent arbitrary workflow state jumps and define allowed actions for RoadWork, RoadMap, RoadTrip, RoadWire, OneWay, CarKeys, and RoadChain.

Receipt-required actions:
- claim
- start_work
- set_awaiting
- resolve_awaiting
- complete
- archive
- reopen
- resolve_blocker

Status:
planned_rules_validated_locally

Policy:
- Local canon/rules files only.
- No GitHub repos changed.
- No secrets touched.
- No generated runtime artifacts committed.
