import logging
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel, Field as PydanticField
from database import get_session
from models import CalendarIntegration, DistributionIntegrationTarget
from middleware.auth import get_current_user, AuthContext
from config import settings
import secrets
import uuid
import os
from pathlib import Path
from urllib.parse import urlparse

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
    "https://www.googleapis.com/auth/webmasters.readonly",
]

CALENDAR_NAME = "ForgeOS — Content"
# Store OAuth states in user home directory (not /tmp for security)
STATE_CACHE_DIR = Path.home() / ".forgeos" / "oauth_states"
STATE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CHANNELS = {"cms", "analytics", "crm", "syndication"}
ALLOWED_DELIVERY_MODES = {"manual", "scheduled", "webhook"}


class IntegrationTargetPayload(BaseModel):
    channel_type: str
    target_key: str
    display_name: str
    endpoint_url: Optional[str] = None
    delivery_mode: str = "scheduled"
    enabled: bool = True
    preferences: dict[str, Any] = PydanticField(default_factory=dict)


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


def _get_org_integration(session: Session, org_id: str) -> Optional[CalendarIntegration]:
    return session.exec(
        select(CalendarIntegration).where(CalendarIntegration.organization_id == org_id)
    ).first()


def _validate_endpoint_url(endpoint_url: str) -> bool:
    parsed = urlparse(endpoint_url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _validate_integration_payload(payload: IntegrationTargetPayload) -> None:
    if payload.channel_type not in ALLOWED_CHANNELS:
        raise HTTPException(status_code=422, detail="Unsupported channel_type")

    if payload.delivery_mode not in ALLOWED_DELIVERY_MODES:
        raise HTTPException(status_code=422, detail="Unsupported delivery_mode")

    if not payload.target_key or not all(
        c.islower() or c.isdigit() or c in {"-", "_"} for c in payload.target_key
    ):
        raise HTTPException(
            status_code=422,
            detail="target_key must use lowercase letters, numbers, dashes, or underscores",
        )

    if payload.channel_type in {"cms", "crm"}:
        if not payload.endpoint_url:
            raise HTTPException(
                status_code=422,
                detail=f"endpoint_url is required for {payload.channel_type} targets",
            )
        if not _validate_endpoint_url(payload.endpoint_url):
            raise HTTPException(
                status_code=422,
                detail="endpoint_url must be a valid http(s) URL",
            )

    required_preferences_by_channel = {
        "cms": ("publish_path", "content_format"),
        "crm": ("object_type", "pipeline_stage"),
    }
    required = required_preferences_by_channel.get(payload.channel_type, ())
    missing = [field for field in required if not payload.preferences.get(field)]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required preferences for {payload.channel_type}: {', '.join(missing)}",
        )


def _serialize_target(target: DistributionIntegrationTarget) -> dict[str, Any]:
    preferences = json.loads(target.preferences_json) if target.preferences_json else {}
    return {
        "id": target.id,
        "organization_id": target.organization_id,
        "channel_type": target.channel_type,
        "target_key": target.target_key,
        "display_name": target.display_name,
        "endpoint_url": target.endpoint_url,
        "delivery_mode": target.delivery_mode,
        "enabled": target.enabled,
        "preferences": preferences,
        "created_at": target.created_at.isoformat(),
        "updated_at": target.updated_at.isoformat(),
    }


@router.get("/targets")
def list_distribution_targets(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    targets = session.exec(
        select(DistributionIntegrationTarget)
        .where(DistributionIntegrationTarget.organization_id == auth.org_id)
        .order_by(DistributionIntegrationTarget.created_at.desc())
    ).all()
    return [_serialize_target(target) for target in targets]


@router.post("/targets")
def create_distribution_target(
    payload: IntegrationTargetPayload,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _validate_integration_payload(payload)

    target = DistributionIntegrationTarget(
        organization_id=auth.org_id,
        created_by_user_id=auth.user_id,
        channel_type=payload.channel_type,
        target_key=payload.target_key,
        display_name=payload.display_name.strip(),
        endpoint_url=payload.endpoint_url,
        delivery_mode=payload.delivery_mode,
        enabled=payload.enabled,
        preferences_json=json.dumps(payload.preferences),
    )
    session.add(target)
    try:
        session.commit()
    except Exception as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Integration target already exists for this organization/channel/key",
        ) from exc

    session.refresh(target)
    return _serialize_target(target)


@router.put("/targets/{target_id}")
def update_distribution_target(
    target_id: str,
    payload: IntegrationTargetPayload,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _validate_integration_payload(payload)

    target = session.exec(
        select(DistributionIntegrationTarget).where(
            DistributionIntegrationTarget.id == target_id,
            DistributionIntegrationTarget.organization_id == auth.org_id,
        )
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Integration target not found")

    target.channel_type = payload.channel_type
    target.target_key = payload.target_key
    target.display_name = payload.display_name.strip()
    target.endpoint_url = payload.endpoint_url
    target.delivery_mode = payload.delivery_mode
    target.enabled = payload.enabled
    target.preferences_json = json.dumps(payload.preferences)
    target.updated_at = datetime.now(timezone.utc)
    session.add(target)
    session.commit()
    session.refresh(target)
    return _serialize_target(target)


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
def authorize_google_calendar(auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
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
def google_callback(code: str, state: str, auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
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
            select(CalendarIntegration).where(CalendarIntegration.organization_id == auth.org_id)
        ).first()
        
        if integration:
            integration.access_token = credentials.token
            integration.refresh_token = credentials.refresh_token or integration.refresh_token
            integration.expires_at = expires_at
            integration.calendar_id = calendar_id
            integration.updated_at = datetime.now(timezone.utc)
        else:
            integration = CalendarIntegration(
                organization_id=auth.org_id,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                expires_at=expires_at,
                calendar_id=calendar_id,
            )
            session.add(integration)
        
        session.commit()
        logger.info(f"Google Calendar integration established for org {auth.org_id}, calendar_id={calendar_id}")
        
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
            CalendarEvent.organization_id == integration.organization_id,
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
def disconnect_google_calendar(auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Revoke Google Calendar access and remove stored credentials.
    User data (calendar events) remain in the database for potential reconnect.
    """
    try:
        integration = _get_org_integration(session, auth.org_id)
        
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
def get_google_status(auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
    """Get current Google Calendar integration status."""
    integration = _get_org_integration(session, auth.org_id)
    
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
def get_sync_status(auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
    """Get calendar sync status and pending events."""
    from models import CalendarEvent, CalendarSyncLog
    
    integration = _get_org_integration(session, auth.org_id)
    
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
            (CalendarEvent.organization_id == auth.org_id) & (CalendarEvent.synced_to_google_at == None) & (CalendarEvent.status == "active")
        )
    ).all()
    
    recent_errors = session.exec(
        select(CalendarSyncLog)
        .where(
            (CalendarSyncLog.organization_id == auth.org_id)
            & (CalendarSyncLog.status == "error")
        )
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
        "synced_count": session.exec(select(CalendarEvent).where((CalendarEvent.organization_id == auth.org_id) & (CalendarEvent.synced_to_google_at != None))).all().__len__(),
        "pending_events": len(pending),
        "last_synced_at": integration.last_synced_at.isoformat() if integration.last_synced_at else None,
        "errors_last_sync": errors,
    }


@router.post("/google/sync-now")
def sync_now(auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
    """Manually trigger a calendar sync from Google."""
    from services.calendar import poll_from_google
    
    try:
        result = poll_from_google(organization_id=auth.org_id)
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


@router.post("/google/gsc/authorize")
def authorize_google_gsc(auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Step 1 (GSC): Generate authorization URL for Google Search Console.
    Uses same OAuth flow as Calendar (webmasters.readonly scope already in GOOGLE_SCOPES).
    """
    try:
        flow = create_google_oauth_flow()
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
        )
        store_oauth_state(state, ttl_seconds=600)
        return {
            "authorization_url": auth_url,
            "state": state,
        }
    except Exception as e:
        logger.error(f"GSC OAuth flow creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create authorization URL")


@router.get("/google/gsc/properties")
def get_gsc_properties(auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Get list of verified GSC properties for user to select from.
    Requires active Google OAuth integration.
    """
    try:
        integration = _get_org_integration(session, auth.org_id)
        
        if not integration or not integration.access_token:
            raise HTTPException(
                status_code=401,
                detail="Google OAuth not connected. Authorize Calendar/GSC first."
            )
        
        credentials = _refresh_credentials_if_needed(integration)
        service = build("webmasters", "v3", credentials=credentials)
        
        response = service.sites().list().execute()
        sites = response.get("siteEntry", [])
        
        properties = [
            {
                "name": site.get("siteUrl"),
                "permission_level": site.get("permissionLevel")
            }
            for site in sites
        ]
        
        logger.info(f"Listed {len(properties)} GSC properties for org {auth.org_id}")
        return {"properties": properties}
        
    except HttpError as e:
        logger.error(f"Failed to list GSC properties: {e}")
        raise HTTPException(status_code=400, detail="Failed to retrieve GSC properties")
    except Exception as e:
        logger.error(f"GSC properties lookup failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving GSC properties")


@router.post("/google/gsc/select-property")
def select_gsc_property(property_url: str, auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    User selects which GSC property to track.
    Stores in CalendarIntegration for now (could extend model later).
    """
    try:
        integration = _get_org_integration(session, auth.org_id)
        
        if not integration:
            raise HTTPException(status_code=401, detail="Google OAuth not connected")
        
        # Store selected property as metadata
        metadata = {}
        if integration.calendar_id:
            metadata["calendar_id"] = integration.calendar_id
        metadata["gsc_property"] = property_url
        
        integration.calendar_id = property_url  # Reuse calendar_id field for GSC property
        integration.updated_at = datetime.now(timezone.utc)
        session.add(integration)
        session.commit()
        
        logger.info(f"Org {auth.org_id} selected GSC property: {property_url}")
        return {
            "status": "success",
            "selected_property": property_url,
            "message": "GSC property selected. Data will be pulled on next scheduled sync."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to select GSC property: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save GSC property selection")
