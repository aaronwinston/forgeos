# Phase 3: Google Calendar Integration — Backend Architecture

**Status:** ✅ Complete  
**Commits:** 7 (cda7e13 → 16f885c)  
**Scope:** OAuth 2.0 + bidirectional sync (backend only; UI in parallel)

---

## What's Implemented

### 1. OAuth 2.0 Flow
- **Endpoint:** `POST /api/integrations/google/authorize`
  - Returns authorization URL; user redirects to Google consent screen
  - Requests scopes: `calendar.readonly`, `calendar.events` (write to dedicated calendar only)

- **Callback:** `GET /api/integrations/google/callback?code=X&state=Y`
  - Exchanges authorization code for access token + refresh token
  - Creates dedicated "ForgeOS — Content" calendar in user's Google account
  - Stores credentials and calendar_id in DB (CalendarIntegration table)
  - Tokens encrypted at rest; never logged or exposed in responses

- **Disconnect:** `DELETE /api/integrations/google/disconnect`
  - Revokes token on Google side
  - Removes credentials from DB
  - User data (calendar events) preserved for reconnect

- **Status:** `GET /api/integrations/google/status`
  - Returns {connected, calendar_id, expires_at, last_synced_at}

### 2. Atomic Event Creation
- **Endpoint:** `POST /api/calendar/events`
  - Creates CalendarEvent row in DB immediately (atomic transaction)
  - Returns event with id right away (frontend shows "syncing" state)
  - Background task syncs to Google within 5 seconds
  - **If Google fails:** Event stays in DB, retries via scheduler every 5 minutes

### 3. Bidirectional Sync

#### Push (ForgeOS → Google)
- services.calendar.sync_to_google(event_id)
- Creates or updates event on Google Calendar
- Handles token refresh automatically (5 min before expiry)
- Logs all operations to CalendarSyncLog for audit trail
- Failure modes:
  - **401 Unauthorized:** Token expired, refresh on next sync
  - **403 Forbidden:** Permission denied, user must reconnect
  - **Network error:** Logged, retried by scheduler

#### Pull (Google → ForgeOS)
- services.calendar.poll_from_google() runs every 5 minutes via APScheduler
- Queries calendarId for events updated since last_synced_at
- **Conflict resolution:** Last-write-wins
  - If local event edited more recently (synced_to_google_at > google updated): ignore Google change
  - Both versions logged to CalendarSyncLog before decision
  - Losing version archived, not deleted
- Deleted events in Google: archived locally (status='archived')
- Returns summary: {updated_count, archived_count, errors}

### 4. Manual Sync
- **Endpoint:** `POST /api/integrations/google/sync-now`
  - Triggers poll immediately (for testing / urgent reconnect)
- **Status:** `GET /api/integrations/google/sync-status`
  - Returns {connected, synced_count, pending_events, last_synced_at, errors_last_sync}

---

## Testing Checklist

- [ ] OAuth flow: Settings → Connect Google → redirects → grants → connected
- [ ] First event: Create deliverable with calendar → appears in Google within 5s
- [ ] Google edit: Edit event in Google → appears in ForgeOS within 5 min
- [ ] Conflict: Edit same event locally + Google → last edit wins (log both)
- [ ] Disconnect/Reconnect: Disconnect → delete creds → reconnect → new tokens
- [ ] Offline: Kill Google API → local calendar works → resumes when back
- [ ] Archive: Delete event in Google → local event archived (not deleted)
- [ ] Manual sync: POST /sync-now returns summary

---

## API Ready for Frontend

All endpoints documented in routers/integrations.py and routers/projects.py.
Frontend can now implement:
1. Settings → Integrations → Connect Google Calendar button
2. Deliverable form → calendar event section
3. Dashboard → sync status badges

See frontend task for UI implementation.
