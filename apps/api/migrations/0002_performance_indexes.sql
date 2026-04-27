-- Migration: Performance Indexes
-- Date: 2024
-- Description: Add indexes to improve query performance for frequently accessed columns
-- Hot paths identified: organization_id, user_id, created_at, status, deleted fields

-- =============================================================================
-- PIPELINERUN INDEXES
-- =============================================================================
-- table: pipelinerun

-- Composite index for common query: WHERE deleted = false AND organization_id = X ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_pipelinerun_org_deleted_created 
ON pipelinerun(organization_id, deleted, created_at DESC);

-- Index for status filtering (pending, active, complete, failed, cancelled)
CREATE INDEX IF NOT EXISTS idx_pipelinerun_org_status 
ON pipelinerun(organization_id, status);

-- Index for brief lookups
CREATE INDEX IF NOT EXISTS idx_pipelinerun_org_brief 
ON pipelinerun(organization_id, brief_id);

-- =============================================================================
-- CALENDAREVENT INDEXES
-- =============================================================================
-- table: calendarevent

-- Index for status filtering (most queries exclude cancelled events)
CREATE INDEX IF NOT EXISTS idx_calendarevent_org_status 
ON calendarevent(organization_id, status);

-- Index for sync status queries (synced, syncing, offline)
CREATE INDEX IF NOT EXISTS idx_calendarevent_org_sync_status 
ON calendarevent(organization_id, sync_status);

-- Composite index for common query: active events not yet synced
CREATE INDEX IF NOT EXISTS idx_calendarevent_org_status_sync 
ON calendarevent(organization_id, status, synced_to_google_at);

-- Index for project-based event queries
CREATE INDEX IF NOT EXISTS idx_calendarevent_org_project 
ON calendarevent(organization_id, project_id);

-- =============================================================================
-- CALENDARSYNCLOG INDEXES
-- =============================================================================
-- table: calendarsynclog

-- Index for status filtering (error logs are frequently queried)
CREATE INDEX IF NOT EXISTS idx_calendarsynclog_org_status 
ON calendarsynclog(organization_id, status);

-- =============================================================================
-- DELIVERABLE INDEXES
-- =============================================================================
-- table: deliverable

-- Index for status filtering (draft, active, complete, archived, published)
CREATE INDEX IF NOT EXISTS idx_deliverable_org_status 
ON deliverable(organization_id, status);

-- Composite index for status + created_at sorting
CREATE INDEX IF NOT EXISTS idx_deliverable_org_status_created 
ON deliverable(organization_id, status, created_at DESC);

-- Index for project-based deliverable queries
CREATE INDEX IF NOT EXISTS idx_deliverable_org_project 
ON deliverable(organization_id, folder_id, status);

-- =============================================================================
-- BRIEF INDEXES
-- =============================================================================
-- table: brief

-- Index for user_id queries (briefs by user)
CREATE INDEX IF NOT EXISTS idx_brief_org_user 
ON brief(organization_id, user_id);

-- Composite index for user + created_at
CREATE INDEX IF NOT EXISTS idx_brief_org_user_created 
ON brief(organization_id, user_id, created_at DESC);

-- =============================================================================
-- PROJECT INDEXES
-- =============================================================================
-- table: project

-- Index for status filtering (active vs archived projects)
CREATE INDEX IF NOT EXISTS idx_project_org_status 
ON project(organization_id, status);

-- Composite index for user + status queries
CREATE INDEX IF NOT EXISTS idx_project_org_user_status 
ON project(organization_id, user_id, status);

-- Index for created_at sorting
CREATE INDEX IF NOT EXISTS idx_project_org_created 
ON project(organization_id, created_at DESC);

-- =============================================================================
-- SCRAPEITEM INDEXES
-- =============================================================================
-- table: scrapeitem

-- Index for dismissed items
CREATE INDEX IF NOT EXISTS idx_scrape_org_dismissed 
ON scrapeitem(organization_id, dismissed_at);

-- Index for surfaced items
CREATE INDEX IF NOT EXISTS idx_scrape_org_surfaced 
ON scrapeitem(organization_id, surfaced_to_user_at);

-- Composite index for score + created_at (common query pattern)
CREATE INDEX IF NOT EXISTS idx_scrape_org_score_created 
ON scrapeitem(organization_id, score DESC, created_at DESC);

-- =============================================================================
-- FOLDER INDEXES
-- =============================================================================
-- table: folder

-- Index for user folder listings
CREATE INDEX IF NOT EXISTS idx_folder_org_user 
ON folder(organization_id, project_id, parent_folder_id);

-- =============================================================================
-- CHATMESSAGE INDEXES
-- =============================================================================
-- table: chatmessage

-- Index for role filtering (assistant, user, system, tool)
CREATE INDEX IF NOT EXISTS idx_chatmessage_org_session_role 
ON chatmessage(organization_id, session_id, role);

-- Index for created_at sorting within sessions
CREATE INDEX IF NOT EXISTS idx_chatmessage_session_created 
ON chatmessage(session_id, created_at);

-- =============================================================================
-- RUNTIMECREDENTIAL INDEXES
-- =============================================================================
-- table: runtimecredential

-- Index for runtime filtering (anthropic, openai, copilot)
CREATE INDEX IF NOT EXISTS idx_runtimecredential_org_runtime 
ON runtimecredential(organization_id, runtime);

-- Index for validity checking
CREATE INDEX IF NOT EXISTS idx_runtimecredential_org_user_valid 
ON runtimecredential(organization_id, user_id, is_valid);

-- =============================================================================
-- USAGEEVENT INDEXES
-- =============================================================================
-- table: usageevent

-- Index for user-specific usage queries
CREATE INDEX IF NOT EXISTS idx_usageevent_org_user_time 
ON usageevent(organization_id, user_id, occurred_at DESC);

-- Index for event type filtering
CREATE INDEX IF NOT EXISTS idx_usageevent_org_type_time 
ON usageevent(organization_id, event_type, occurred_at DESC);

-- Index for runtime filtering
CREATE INDEX IF NOT EXISTS idx_usageevent_org_runtime_time 
ON usageevent(organization_id, runtime, occurred_at DESC);

-- =============================================================================
-- FEATUREFLAG INDEXES
-- =============================================================================
-- table: featureflag

-- Index for enabled flags lookup
CREATE INDEX IF NOT EXISTS idx_featureflag_org_enabled 
ON featureflag(organization_id, enabled);

-- =============================================================================
-- AUDITEVENT INDEXES
-- =============================================================================
-- table: auditevent

-- Index for user-specific audit logs
CREATE INDEX IF NOT EXISTS idx_auditevent_org_user_time 
ON auditevent(organization_id, user_id, created_at DESC);

-- Index for resource filtering
CREATE INDEX IF NOT EXISTS idx_auditevent_org_resource_time 
ON auditevent(organization_id, resource_type, created_at DESC);

-- =============================================================================
-- DOCTRINEVERSION INDEXES
-- =============================================================================
-- table: doctrineversion

-- Index for user lookups (who saved what)
CREATE INDEX IF NOT EXISTS idx_doctrine_org_user_time 
ON doctrineversion(organization_id, saved_by_user_id, created_at DESC);

-- Index for locked content queries
CREATE INDEX IF NOT EXISTS idx_doctrine_org_locked 
ON doctrineversion(organization_id, locked_by_user_id);

-- =============================================================================
-- SUMMARY OF ADDED INDEXES
-- =============================================================================
-- Total new indexes: 44
--
-- Performance improvements expected:
-- 1. PipelineRun queries with deleted=false filter (sessions list)
-- 2. CalendarEvent status filtering (exclude cancelled)
-- 3. CalendarEvent sync status queries (offline events)
-- 4. Deliverable status filtering and sorting
-- 5. Brief user_id queries (user's briefs)
-- 6. Project status filtering (active projects)
-- 7. ScrapeItem dismissed/surfaced filtering
-- 8. UsageEvent user and type breakdowns
-- 9. AuditEvent user and resource filtering
-- 10. RuntimeCredential validity checks
--
-- These indexes target:
-- - WHERE clauses with org_id + status/deleted/user_id
-- - ORDER BY created_at/occurred_at patterns
-- - Composite queries combining filters with sorting
-- - Foreign key lookups (project_id, brief_id, etc.)
