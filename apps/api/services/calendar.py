import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlmodel import Session, select
from database import engine
from models import CalendarIntegration, CalendarEvent, CalendarSyncLog, Deliverable
from config import settings
import asyncio

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    raise ImportError("Google API libraries required. Install: pip install google-auth-oauthlib google-api-python-client")

logger = logging.getLogger(__name__)


def create_event_atomic(
    title: str,
    start_at: datetime,
    end_at: datetime,
    deliverable_id: int,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a calendar event in ForgeOS with automatic sync to Google (if connected).
    
    This operation is atomic: the local event is created and returned immediately,
    even if Google sync fails. Sync retries happen in the background via scheduler.
    
    Args:
        title: Event title
        start_at: Event start (ISO 8601 datetime)
        end_at: Event end (ISO 8601 datetime)
        deliverable_id: Foreign key to Deliverable
        description: Optional event description
    
    Returns:
        Created CalendarEvent as dict with id, status, synced_to_google_at
    
    Raises:
        ValueError: if deliverable_id doesn't exist
    """
    with Session(engine) as session:
        deliverable = session.exec(
            select(Deliverable).where(Deliverable.id == deliverable_id)
        ).first()
        if not deliverable:
            raise ValueError(f"Deliverable {deliverable_id} not found")
        
        event = CalendarEvent(
            deliverable_id=deliverable_id,
            title=title,
            description=description,
            start_at=start_at,
            end_at=end_at,
            status="active",
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        event_id = event.id
        logger.info(f"Created calendar event {event_id} for deliverable {deliverable_id}: {title}")
    
    asyncio.create_task(_sync_to_google_async(event_id))
    
    return {
        "id": event_id,
        "title": title,
        "description": description,
        "start_at": start_at.isoformat(),
        "end_at": end_at.isoformat(),
        "status": "active",
        "synced_to_google_at": None,
    }


async def _sync_to_google_async(event_id: int):
    """
    Schedule sync to Google Calendar asynchronously with 5-second delay.
    Runs in background; failures logged but don't block user.
    """
    await asyncio.sleep(5)
    sync_to_google(event_id)


def sync_to_google(event_id: int) -> Dict[str, Any]:
    """
    Push a local calendar event to Google Calendar.
    
    If google_event_id is None, inserts a new event on Google.
    If google_event_id exists, updates the existing event on Google.
    
    Handles token refresh automatically. Logs all operations and conflicts.
    
    Args:
        event_id: CalendarEvent.id
    
    Returns:
        Dict with status, google_event_id, error (if any)
    """
    with Session(engine) as session:
        event = session.exec(
            select(CalendarEvent).where(CalendarEvent.id == event_id)
        ).first()
        if not event:
            logger.error(f"Calendar event {event_id} not found")
            return {"status": "error", "error": "Event not found"}
        
        integration = session.exec(
            select(CalendarIntegration).where(CalendarIntegration.user_id == "aaron")
        ).first()
        if not integration:
            _log_sync("push", event_id, "pending", "Google Calendar not connected")
            return {"status": "pending", "error": "Google Calendar not connected"}
        
        try:
            credentials = _get_valid_credentials(integration, session)
            service = build("calendar", "v3", credentials=credentials)
            
            body = {
                "summary": event.title,
                "description": event.description or "",
                "start": {"dateTime": event.start_at.isoformat(), "timeZone": "UTC"},
                "end": {"dateTime": event.end_at.isoformat(), "timeZone": "UTC"},
            }
            
            if event.google_event_id:
                service.events().update(
                    calendarId=integration.calendar_id,
                    eventId=event.google_event_id,
                    body=body,
                ).execute()
                logger.info(f"Updated Google event {event.google_event_id} for local event {event_id}")
                _log_sync("push_update", event_id, "success", None, event.google_event_id)
            else:
                result = service.events().insert(
                    calendarId=integration.calendar_id,
                    body=body,
                ).execute()
                event.google_event_id = result["id"]
                _log_sync("push_insert", event_id, "success", None, result["id"])
                logger.info(f"Inserted Google event {result['id']} for local event {event_id}")
            
            event.synced_to_google_at = datetime.utcnow()
            session.add(event)
            session.commit()
            
            return {
                "status": "success",
                "event_id": event_id,
                "google_event_id": event.google_event_id,
            }
        
        except HttpError as e:
            if e.resp.status == 401:
                logger.warning(f"Token expired during push sync for event {event_id}, will retry")
                _log_sync("push", event_id, "pending", "Token expired")
                return {"status": "pending", "error": "Token expired"}
            elif e.resp.status == 403:
                logger.error(f"Permission denied pushing event {event_id}: {e}")
                _log_sync("push", event_id, "error", f"Permission denied: {str(e)}")
                return {"status": "error", "error": "Permission denied"}
            else:
                logger.error(f"Google API error pushing event {event_id}: {e}")
                _log_sync("push", event_id, "error", f"API error: {str(e)}")
                return {"status": "error", "error": str(e)}
        
        except Exception as e:
            logger.error(f"Unexpected error syncing event {event_id}: {str(e)}")
            _log_sync("push", event_id, "error", f"Unexpected error: {str(e)}")
            return {"status": "error", "error": str(e)}


def poll_from_google() -> Dict[str, Any]:
    """
    Poll Google Calendar for changes since last sync.
    
    Applies updates, handles conflicts via last-write-wins, archives deleted events.
    Token refresh handled automatically.
    
    Returns:
        Dict with updated_count, archived_count, errors
    """
    with Session(engine) as session:
        integration = session.exec(
            select(CalendarIntegration).where(CalendarIntegration.user_id == "aaron")
        ).first()
        
        if not integration:
            logger.debug("Google Calendar not connected, skipping poll")
            return {"status": "skipped", "reason": "Not connected"}
        
        try:
            credentials = _get_valid_credentials(integration, session)
            service = build("calendar", "v3", credentials=credentials)
            
            updated_min = integration.last_synced_at or (datetime.utcnow() - timedelta(hours=24))
            
            events_result = service.events().list(
                calendarId=integration.calendar_id,
                updatedMin=updated_min.isoformat() + "Z",
                showDeleted=True,
                pageSize=100,
            ).execute()
            
            events = events_result.get("items", [])
            updated_count = 0
            archived_count = 0
            errors = []
            
            for google_event in events:
                try:
                    result = _apply_google_event(session, integration, google_event)
                    if result["action"] == "updated":
                        updated_count += 1
                    elif result["action"] == "archived":
                        archived_count += 1
                except Exception as e:
                    error_msg = f"Failed to apply event {google_event.get('id')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    _log_sync("poll", None, "error", error_msg)
            
            integration.last_synced_at = datetime.utcnow()
            session.add(integration)
            session.commit()
            
            logger.info(f"Poll completed: {updated_count} updated, {archived_count} archived")
            _log_sync("poll", None, "success", None, json.dumps({
                "updated": updated_count,
                "archived": archived_count,
                "errors": len(errors)
            }))
            
            return {
                "status": "success",
                "updated_count": updated_count,
                "archived_count": archived_count,
                "errors": errors,
            }
        
        except HttpError as e:
            if e.resp.status == 401:
                logger.warning("Token expired during poll, will retry next cycle")
                _log_sync("poll", None, "pending", "Token expired")
                return {"status": "pending", "reason": "Token expired"}
            else:
                logger.error(f"Google API error during poll: {e}")
                _log_sync("poll", None, "error", str(e))
                return {"status": "error", "error": str(e)}
        
        except Exception as e:
            logger.error(f"Unexpected error during poll: {str(e)}")
            _log_sync("poll", None, "error", str(e))
            return {"status": "error", "error": str(e)}


def _apply_google_event(session: Session, integration: CalendarIntegration, google_event: Dict[str, Any]) -> Dict[str, str]:
    """
    Apply a single Google event to the local database.
    
    Conflict resolution:
    - If local event edited more recently (synced_to_google_at > google updated time):
      last-write-wins, Google change ignored, logged
    - Otherwise: apply Google update
    - Deleted events: archived, not deleted
    """
    google_event_id = google_event["id"]
    
    local_event = session.exec(
        select(CalendarEvent).where(CalendarEvent.google_event_id == google_event_id)
    ).first()
    
    if google_event.get("status") == "cancelled":
        if local_event:
            _log_sync("poll_delete", local_event.id, "success", None, google_event_id)
            local_event.status = "archived"
            session.add(local_event)
            logger.info(f"Archived local event {local_event.id} (deleted in Google)")
            return {"action": "archived", "event_id": local_event.id}
        return {"action": "skipped", "reason": "No local match for deleted event"}
    
    if not local_event:
        logger.debug(f"Google event {google_event_id} not in ForgeOS (from other app)")
        return {"action": "skipped", "reason": "No local match"}
    
    google_updated = datetime.fromisoformat(google_event["updated"].replace("Z", "+00:00"))
    
    if local_event.synced_to_google_at and local_event.synced_to_google_at > google_updated:
        logger.info(
            f"Conflict: local event {local_event.id} edited {local_event.synced_to_google_at}, "
            f"Google event {google_event_id} updated {google_updated}. Local wins."
        )
        _log_sync(
            "poll_conflict",
            local_event.id,
            "resolved_local",
            f"Local {local_event.synced_to_google_at} > Google {google_updated}",
            google_event_id,
        )
        return {"action": "conflict_local_wins", "event_id": local_event.id}
    
    old_title = local_event.title
    old_start = local_event.start_at
    old_end = local_event.end_at
    
    local_event.title = google_event.get("summary", local_event.title)
    local_event.description = google_event.get("description", "")
    local_event.start_at = datetime.fromisoformat(
        google_event["start"].get("dateTime", google_event["start"].get("date")).replace("Z", "+00:00")
    )
    local_event.end_at = datetime.fromisoformat(
        google_event["end"].get("dateTime", google_event["end"].get("date")).replace("Z", "+00:00")
    )
    local_event.last_synced_at = datetime.utcnow()
    session.add(local_event)
    
    logger.info(f"Updated local event {local_event.id} from Google: {old_title} -> {local_event.title}")
    _log_sync(
        "poll_update",
        local_event.id,
        "success",
        f"Title: {old_title} -> {local_event.title}, Start: {old_start} -> {local_event.start_at}",
        google_event_id,
    )
    
    return {"action": "updated", "event_id": local_event.id}


def _get_valid_credentials(integration: CalendarIntegration, session: Session) -> Credentials:
    """
    Get valid OAuth credentials, refreshing if necessary.
    
    If token expires within 5 minutes, refresh immediately.
    Logs error but does not raise on transient failures (will be retried on next cycle).
    """
    if integration.expires_at <= datetime.utcnow() + timedelta(minutes=5):
        logger.debug("Token expiring soon, refreshing...")
        credentials = Credentials(
            token=integration.access_token,
            refresh_token=integration.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
        )
        
        try:
            request = Request()
            credentials.refresh(request)
            
            integration.access_token = credentials.token
            # Fix: Use credentials.expiry directly
            integration.expires_at = credentials.expiry
            session.add(integration)
            session.commit()
            logger.info("Token refreshed successfully")
            return credentials
        except Exception as e:
            # Only retry on transient errors (5xx), not auth errors (401)
            if "401" in str(e) or "invalid_grant" in str(e):
                logger.error(f"Token refresh failed permanently (401 Unauthorized): {e}")
                logger.error("User may need to reconnect Google Calendar")
                raise  # Propagate auth errors
            else:
                logger.warning(f"Token refresh failed transiently: {e}. Will retry on next sync cycle.")
                return None  # Return None to signal skip this sync
    
    return Credentials(
        token=integration.access_token,
        refresh_token=integration.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    )


def _log_sync(operation: str, event_id: Optional[int], status: str, error_msg: Optional[str] = None, details: Optional[str] = None):
    """
    Log a sync operation to CalendarSyncLog for audit trail.
    
    Args:
        operation: push_insert, push_update, poll, poll_delete, poll_conflict, poll_update, etc.
        event_id: CalendarEvent.id (None for poll operations)
        status: success, error, pending, resolved_local
        error_msg: Error message (if status=error)
        details: JSON details about the operation
    """
    with Session(engine) as session:
        log = CalendarSyncLog(
            event_id=event_id,
            operation=operation,
            status=status,
            error_message=error_msg,
            details_json=details,
        )
        session.add(log)
        session.commit()
