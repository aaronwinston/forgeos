-- ForgeOS migration 0007
-- Purpose: Add structured project tracking payload for SEO/AEO workflows.

ALTER TABLE project ADD COLUMN tracking_json TEXT;
