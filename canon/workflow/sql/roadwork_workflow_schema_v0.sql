-- RoadWork Workflow Kernel Schema v0
-- Status: planned schema only
-- Purpose: platform-agnostic workflow/task engine for RoadWork, RoadWire, OneWay, RoadTrip, CarKeys, and RoadChain.

CREATE TABLE workflow_items (
  id TEXT PRIMARY KEY,
  index_id TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  source TEXT NOT NULL,
  source_id TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'received',
  received_at TEXT NOT NULL,
  read_at TEXT,
  read_by TEXT,
  claimed_by TEXT,
  claimed_at TEXT,
  is_collaborative INTEGER NOT NULL DEFAULT 0,
  awaiting_type TEXT,
  awaiting_since TEXT,
  awaiting_owner TEXT,
  awaiting_note TEXT,
  due_at TEXT,
  sla_response_at TEXT,
  sla_resolution_at TEXT,
  escalation_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE workflow_tasks (
  id TEXT PRIMARY KEY,
  workflow_item_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'unclaimed',
  owner TEXT,
  priority TEXT DEFAULT 'normal',
  due_at TEXT,
  claimed_by TEXT,
  claimed_at TEXT,
  completed_at TEXT,
  receipt_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (workflow_item_id) REFERENCES workflow_items(id)
);

CREATE TABLE workflow_subtasks (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'unclaimed',
  owner TEXT,
  due_at TEXT,
  completed_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (task_id) REFERENCES workflow_tasks(id)
);

CREATE TABLE workflow_collaborators (
  id TEXT PRIMARY KEY,
  workflow_item_id TEXT NOT NULL,
  collaborator_id TEXT NOT NULL,
  role TEXT DEFAULT 'collaborator',
  added_at TEXT NOT NULL,
  added_by TEXT,
  FOREIGN KEY (workflow_item_id) REFERENCES workflow_items(id)
);

CREATE TABLE workflow_events (
  id TEXT PRIMARY KEY,
  workflow_item_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  actor TEXT NOT NULL,
  note TEXT DEFAULT '',
  before_status TEXT,
  after_status TEXT,
  metadata_json TEXT DEFAULT '{}',
  receipt_id TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (workflow_item_id) REFERENCES workflow_items(id)
);

CREATE TABLE workflow_actions (
  id TEXT PRIMARY KEY,
  workflow_item_id TEXT NOT NULL,
  action_type TEXT NOT NULL,
  actor TEXT NOT NULL,
  status_before TEXT,
  status_after TEXT,
  result TEXT NOT NULL DEFAULT 'unknown',
  error TEXT DEFAULT '',
  metadata_json TEXT DEFAULT '{}',
  receipt_id TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (workflow_item_id) REFERENCES workflow_items(id)
);

CREATE TABLE workflow_awaiting_log (
  id TEXT PRIMARY KEY,
  workflow_item_id TEXT NOT NULL,
  awaiting_type TEXT NOT NULL,
  awaiting_owner TEXT,
  awaiting_since TEXT NOT NULL,
  resolved_at TEXT,
  resolved_by TEXT,
  resolution_note TEXT DEFAULT '',
  receipt_id TEXT,
  FOREIGN KEY (workflow_item_id) REFERENCES workflow_items(id)
);

CREATE TABLE workflow_timeline_events (
  id TEXT PRIMARY KEY,
  workflow_item_id TEXT NOT NULL,
  timeline_type TEXT NOT NULL,
  scheduled_at TEXT NOT NULL,
  fired_at TEXT,
  status TEXT NOT NULL DEFAULT 'scheduled',
  note TEXT DEFAULT '',
  receipt_id TEXT,
  FOREIGN KEY (workflow_item_id) REFERENCES workflow_items(id)
);

CREATE TABLE workflow_receipts (
  id TEXT PRIMARY KEY,
  workflow_item_id TEXT,
  task_id TEXT,
  receipt_type TEXT NOT NULL,
  receipt_path TEXT,
  receipt_hash TEXT,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX idx_workflow_items_status ON workflow_items(status);
CREATE INDEX idx_workflow_items_claimed_by ON workflow_items(claimed_by);
CREATE INDEX idx_workflow_items_awaiting_type ON workflow_items(awaiting_type);
CREATE INDEX idx_workflow_tasks_status ON workflow_tasks(status);
CREATE INDEX idx_workflow_events_item ON workflow_events(workflow_item_id);
CREATE INDEX idx_workflow_actions_item ON workflow_actions(workflow_item_id);
