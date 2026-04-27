import logging
import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import engine
from models import CalendarIntegration
from config import settings
import secrets
import uuid
import os
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.service_account import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError("Google API client libraries required. Install: pip install google-auth-oauthlib google-api-python-client")

router = APIRouter(prefix="/api/integrations", tags=["integrations"])
logger = logging.getLogger(__name__)

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

CALENDAR_NAME = "ForgeOS — Content"
STATE_CACHE_DIR = Path("/tmp/forgeos_oauth_states")  # Store OAuth states temporarily
STATE_CACHE_DIR.mkdir(exist_ok=True)


def store_oauth_state(state: str, ttl_seconds: int = 600):
    """Store OAuth state parameter for CSRF validation. Default TTL: 10 minutes."""
    state_file = STATE_CACHE_DIR / f"{state}.json"
    state_file.write_text(json.dumps({
        "state": state,
        "created_at": datetime.utcnow(timezone.utc).isoformat(),
        "expires_at": (datetime.utcnow(timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat(),
    }))


def validate_oauth_state(state: str) -> bool:
    """Validate OAuth state parameter against stored value. Returns True if valid."""
    if not state:
        return False
    state_file = STATE_CACHE_DIR / f"{state}.json"
    if not state_file.exists():
        return False
    try:
        data = json.loads(state_file.read_text())
        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.utcnow(timezone.utc) > expires_at:
            state_file.unlink()  # Clean up expired state
            return False
        state_file.unlink()  # Clean up used state
        return True
    except Exception as e:
        logger.error(f"State validation error: {e}")
        return False


def get_db():
    with Session(engine) as session:
        yield session


def create_google_oauth_flow():
    """Create OAuth 2.0 flow for Google Calendar."""
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth credentials not configured. Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in .env"
        )
    
    return Flow.from_client_config(
        {
            "installed": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI],
            }
        },
        scopes=GOOGLE_SCOPES,
    )


@router.post("/google/authorize")
def authorize_google_calendar(session: Session = Depends(get_db)):
    """
    Step 1: Generate authorization URL to send user to Google consent screen.
    Returns URL that frontend should redirect user to.
    """
    try:
        flow = create_google_oauth_flow()
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
        )
        # Store state for CSRF validation (valid for 10 minutes)
        store_oauth_state(state, ttl_seconds=600)
        return {
            "authorization_url": auth_url,
            "state": state,
        }
    except Exception as e:
        logger.error(f"OAuth flow creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create authorization URL")


@router.get("/google/callback")
def google_callback(code: str, state: str, session: Session = Depends(get_db)):
    """
    Step 2: Google redirects user back here with authorization code.
    Validate state parameter to prevent CSRF, then exchange code for access token.
    """
    # Validate state parameter (CSRF protection)
    if not validate_oauth_state(state):
        logger.warning(f"Invalid or expired OAuth state: {state}")
        raise HTTPException(status_code=403, detail="Invalid or expired authorization state")
    
    try:
        flow = create_google_oauth_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        if not credentials.valid:
            raise HTTPException(status_code=400, detail="Failed to obtain valid credentials")

        service = build("calendar", "v3", credentials=credentials)
        
        calendar_id = _create_or_get_calendar(service)
        
        # Fix: Use credentials.expiry directly (it's already a datetime object)
        expires_at = credentials.expiry
        
        integration = session.exec(
            select(CalendarIntegration).where(CalendarIntegration.user_id == "aaron")
        ).first()
        
        if integration:
            integration.access_token = credentials.token
            integration.refresh_token = credentials.refresh_token or integration.refresh_token
            integration.expires_at = expires_at
            integration.calendar_id = calendar_id
            integration.updated_at = datetime.utcnow()
        else:
            integration = CalendarIntegration(
                user_id="aaron",
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                expires_at=expires_at,
                calendar_id=calendar_id,
            )
            session.add(integration)
        
        session.commit()
        logger.info(f"Google Calendar integration established for user aaron, calendar_id={calendar_id}")
        
        # Blocker #4 Fix: Retry offline events after OAuth connection
        _retry_offline_events(session, integration)
        
        return {
            "status": "success",
            "message": "Google Calendar connected successfully",
            "calendar_id": calendar_id,
            "redirect_to": "/settings?tab=integrations",
        }
    except HttpError as e:
        logger.error(f"Google API error during callback: {e}")
        raise HTTPException(status_code=400, detail="Failed to complete Google authentication")
    except Exception as e:
        logger.error(f"Callback processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process callback")


def _retry_offline_events(session: Session, integration: CalendarIntegration):
    """Retry events that were created offline before Google connection."""
    from models import CalendarEvent
    offline_events = session.exec(
        select(CalendarEvent).where(
            CalendarEvent.sync_status == "offline",
            CalendarEvent.synced_to_google_at == None,
        )
    ).all()
    
    if not offline_events:
        return
    
    logger.info(f"Retrying {len(offline_events)} offline events after OAuth connection")
    
    # Import sync function from services/calendar.py
    try:
        from services.calendar import sync_to_google
        for event in offline_events:
            try:
                sync_to_google(event.id)
                logger.info(f"Successfully synced offline event {event.id} to Google")
            except Exception as e:
                logger.error(f"Failed to sync offline event {event.id}: {e}")
    except ImportError:
        logger.error("Could not import sync_to_google; offline events will remain pending")


def _create_or_get_calendar(service):
    """
    Create dedicated 'ForgeOS — Content' calendar if it doesn't exist.
    Returns calendar_id.
    """
    try:
        calendar_list = service.calendarList().list().execute()
        for calendar in calendar_list.get("items", []):
            if calendar.get("summary") == CALENDAR_NAME:
                logger.info(f"Found existing ForgeOS calendar: {calendar['id']}")
                return calendar["id"]
        
        body = {
            "summary": CALENDAR_NAME,
            "description": "Events synced from ForgeOS content management system",
            "timeZone": "UTC",
        }
        created_calendar = service.calendars().insert(body=body).execute()
        calendar_id = created_calendar["id"]
        logger.info(f"Created new ForgeOS calendar: {calendar_id}")
        return calendar_id
    except HttpError as e:
        logger.error(f"Calendar creation/lookup failed: {e}")
        raise


@router.delete("/google/disconnect")
def disconnect_google_calendar(session: Session = Depends(get_db)):
    """
    Revoke Google Calendar access and remove stored credentials.
    User data (calendar events) remain in the database for potential reconnect.
    """
    try:
        integration = session.exec(
            select(CalendarIntegration).where(CalendarIntegration.user_id == "aaron")
        ).first()
        
        if not integration:
            raise HTTPException(status_code=404, detail="No Google Calendar integration found")
        
        try:
            service = build(
                "calendar",
                "v3",
                credentials=_refresh_credentials_if_needed(integration),
            )
            service.calendarList().delete(calendarId=integration.calendar_id).execute()
            logger.info(f"Revoked access to calendar {integration.calendar_id}")
        except Exception as e:
            logger.warning(f"Could not revoke calendar access (may already be revoked): {e}")
        
        session.delete(integration)
        session.commit()
        logger.info("Google Calendar integration disconnected")
        
        return {
            "status": "success",
            "message": "Google Calendar disconnected. Events remain in local database."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disconnect failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to disconnect Google Calendar")


@router.get("/google/status")
def get_google_status(session: Session = Depends(get_db)):
    """Get current Google Calendar integration status."""
    integration = session.exec(
        select(CalendarIntegration).where(CalendarIntegration.user_id == "aaron")
    ).first()
    
    if not integration:
        return {
            "connected": False,
            "calendar_id": None,
            "expires_at": None,
            "last_synced_at": None,
        }
    
    return {
        "connected": True,
        "calendar_id": integration.calendar_id,
        "expires_at": integration.expires_at.isoformat(),
        "last_synced_at": integration.last_synced_at.isoformat() if integration.last_synced_at else None,
    }


@router.get("/google/sync-status")
def get_sync_status(session: Session = Depends(get_db)):
    """Get calendar sync status and pending events."""
    from models import CalendarEvent, CalendarSyncLog
    
    integration = session.exec(
        select(CalendarIntegration).where(CalendarIntegration.user_id == "aaron")
    ).first()
    
    if not integration:
        return {
            "connected": False,
            "synced_count": 0,
            "pending_events": 0,
            "last_synced_at": None,
            "errors_last_sync": [],
        }
    
    pending = session.exec(
        select(CalendarEvent).where(
            (CalendarEvent.synced_to_google_at == None) & (CalendarEvent.status == "active")
        )
    ).all()
    
    recent_errors = session.exec(
        select(CalendarSyncLog)
        .where(CalendarSyncLog.status == "error")
        .order_by(CalendarSyncLog.created_at.desc())
    ).first()
    
    errors = []
    if recent_errors:
        errors.append({
            "operation": recent_errors.operation,
            "error": recent_errors.error_message,
            "timestamp": recent_errors.created_at.isoformat(),
        })
    
    return {
        "connected": True,
        "synced_count": session.exec(select(CalendarEvent).where(CalendarEvent.synced_to_google_at != None)).all().__len__(),
        "pending_events": len(pending),
        "last_synced_at": integration.last_synced_at.isoformat() if integration.last_synced_at else None,
        "errors_last_sync": errors,
    }


@router.post("/google/sync-now")
def sync_now(session: Session = Depends(get_db)):
    """Manually trigger a calendar sync from Google."""
    from services.calendar import poll_from_google
    
    try:
        result = poll_from_google()
        return {
            "status": "success",
            "result": result,
        }
    except Exception as e:
        logger.error(f"Manual sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


def _refresh_credentials_if_needed(integration: CalendarIntegration):
    """Refresh OAuth token if expired (not implemented here; handled in services/calendar.py)."""
    from google.oauth2.credentials import Credentials
    
    credentials = Credentials(
        token=integration.access_token,
        refresh_token=integration.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    )
    
    if credentials.expired:
        request = Request()
        credentials.refresh(request)
    
    return credentials
