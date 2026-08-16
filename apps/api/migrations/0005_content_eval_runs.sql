-- ForgeOS migration 0005
-- Purpose: Store rubric-scored evaluation harness runs with baseline/regression snapshots.

CREATE TABLE IF NOT EXISTS contentevalrun (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  organization_id TEXT NOT NULL,
  created_by_user_id TEXT NOT NULL,
  workflow_type TEXT NOT NULL,
  artifact_key TEXT NOT NULL DEFAULT 'adhoc',
  artifact_text TEXT NOT NULL,
  prompt_version TEXT,
  skill_version TEXT,
  scores_json TEXT NOT NULL,
  overall_score REAL NOT NULL,
  gate_status TEXT NOT NULL,
  failed_dimensions_json TEXT,
  baseline_run_id INTEGER,
  deltas_json TEXT,
  regression_failed INTEGER NOT NULL DEFAULT 0,
  is_baseline INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_contentevalrun_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT ck_contentevalrun_workflow_type CHECK (workflow_type IN ('blog','launch','analyst')),
  CONSTRAINT ck_contentevalrun_gate_status CHECK (gate_status IN ('pass','fail'))
);

CREATE INDEX IF NOT EXISTS idx_contentevalrun_org_workflow_artifact_created
  ON contentevalrun(organization_id, workflow_type, artifact_key, created_at);
