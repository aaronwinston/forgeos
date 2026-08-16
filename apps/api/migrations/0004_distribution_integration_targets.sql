-- ForgeOS migration 0004
-- Purpose: Org-scoped distribution integration targets for CMS/CRM/analytics/syndication.

CREATE TABLE IF NOT EXISTS distributionintegrationtarget (
  id TEXT PRIMARY KEY NOT NULL,
  organization_id TEXT NOT NULL,
  created_by_user_id TEXT NOT NULL,
  channel_type TEXT NOT NULL,
  target_key TEXT NOT NULL,
  display_name TEXT NOT NULL,
  endpoint_url TEXT,
  delivery_mode TEXT NOT NULL DEFAULT 'scheduled',
  enabled INTEGER NOT NULL DEFAULT 1,
  preferences_json TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_distributionintegrationtarget_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT uq_distributionintegrationtarget_org_channel_key UNIQUE (organization_id, channel_type, target_key),
  CONSTRAINT ck_distributionintegrationtarget_channel CHECK (channel_type IN ('cms','analytics','crm','syndication')),
  CONSTRAINT ck_distributionintegrationtarget_delivery_mode CHECK (delivery_mode IN ('manual','scheduled','webhook'))
);

CREATE INDEX IF NOT EXISTS idx_distributionintegrationtarget_org_channel
  ON distributionintegrationtarget(organization_id, channel_type);
