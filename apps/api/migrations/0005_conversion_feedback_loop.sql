-- ForgeOS migration 0005
-- Purpose: Conversion feedback loop artifacts tied to deliverables/content outcomes.

CREATE TABLE IF NOT EXISTS conversiontaxonomydefinition (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  organization_id TEXT NOT NULL,
  deliverable_id INTEGER NOT NULL,
  created_by_user_id TEXT NOT NULL,
  content_type TEXT NOT NULL,
  event_key TEXT NOT NULL,
  funnel_stage TEXT NOT NULL,
  definition TEXT NOT NULL,
  primary_cta TEXT,
  success_metric TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_conversiontaxonomydefinition_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_conversiontaxonomydefinition_deliverable FOREIGN KEY (deliverable_id) REFERENCES deliverable(id) ON DELETE CASCADE,
  CONSTRAINT uq_conversiontaxonomy_org_deliverable_event UNIQUE (organization_id, deliverable_id, event_key)
);

CREATE INDEX IF NOT EXISTS idx_conversiontaxonomy_org_deliverable
  ON conversiontaxonomydefinition(organization_id, deliverable_id);

CREATE INDEX IF NOT EXISTS idx_conversiontaxonomy_org_content_type
  ON conversiontaxonomydefinition(organization_id, content_type);

CREATE TABLE IF NOT EXISTS deliverableconversionoutcomesnapshot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  organization_id TEXT NOT NULL,
  deliverable_id INTEGER NOT NULL,
  created_by_user_id TEXT NOT NULL,
  period_label TEXT NOT NULL,
  visitors INTEGER,
  conversions INTEGER,
  conversion_rate REAL,
  observed_outcome TEXT,
  notes TEXT,
  recorded_at TEXT NOT NULL DEFAULT (datetime('now')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_deliverableconversionoutcome_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_deliverableconversionoutcome_deliverable FOREIGN KEY (deliverable_id) REFERENCES deliverable(id) ON DELETE CASCADE,
  CONSTRAINT ck_deliverableconversionoutcome_rate CHECK ((conversion_rate IS NULL) OR (conversion_rate >= 0 AND conversion_rate <= 1)),
  CONSTRAINT ck_deliverableconversionoutcome_visitors CHECK ((visitors IS NULL) OR visitors >= 0),
  CONSTRAINT ck_deliverableconversionoutcome_conversions CHECK ((conversions IS NULL) OR conversions >= 0)
);

CREATE INDEX IF NOT EXISTS idx_deliverableconversionoutcome_org_deliverable
  ON deliverableconversionoutcomesnapshot(organization_id, deliverable_id);

CREATE INDEX IF NOT EXISTS idx_deliverableconversionoutcome_org_recorded
  ON deliverableconversionoutcomesnapshot(organization_id, recorded_at);

CREATE TABLE IF NOT EXISTS deliverablectaexperiment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  organization_id TEXT NOT NULL,
  deliverable_id INTEGER NOT NULL,
  created_by_user_id TEXT NOT NULL,
  experiment_key TEXT NOT NULL,
  variant_label TEXT NOT NULL,
  hypothesis TEXT,
  observed_outcome TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  impressions INTEGER,
  conversions INTEGER,
  conversion_rate REAL,
  started_at TEXT,
  ended_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_deliverablectaexperiment_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_deliverablectaexperiment_deliverable FOREIGN KEY (deliverable_id) REFERENCES deliverable(id) ON DELETE CASCADE,
  CONSTRAINT ck_deliverablectaexperiment_status CHECK (status IN ('active','paused','completed')),
  CONSTRAINT ck_deliverablectaexperiment_rate CHECK ((conversion_rate IS NULL) OR (conversion_rate >= 0 AND conversion_rate <= 1)),
  CONSTRAINT ck_deliverablectaexperiment_impressions CHECK ((impressions IS NULL) OR impressions >= 0),
  CONSTRAINT ck_deliverablectaexperiment_conversions CHECK ((conversions IS NULL) OR conversions >= 0),
  CONSTRAINT uq_deliverablectaexperiment_org_deliverable_variant UNIQUE (organization_id, deliverable_id, experiment_key, variant_label)
);

CREATE INDEX IF NOT EXISTS idx_deliverablectaexperiment_org_deliverable
  ON deliverablectaexperiment(organization_id, deliverable_id);
