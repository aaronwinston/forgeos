"""
Calendar router — Phase 3 Google Calendar integration (UI/event-management scope).

Endpoints:
  GET    /api/calendar/events           list events in a date range
  POST   /api/calendar/events           create CalendarEvent + Deliverable atomically
  GET    /api/calendar/events/upcoming  next 7 days, max 5 (Up Next widget)
  PATCH  /api/calendar/events/{id}      update (reschedule, status, sync_status)
  DELETE /api/calendar/events/{id}      hard delete

The Google Calendar sync layer (google_event_id, sync_status) is wired here but
the actual OAuth round-trip is owned by the Phase 3.3 Opus scope via /api/integrations.
This router accepts sync_status updates from that layer via PATCH and exposes the
field on GET so the UI can render ✓ / ⟳ / ⚠ badges.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models import CalendarEvent, Deliverable, Folder, Project
from middleware.auth import get_current_user, AuthContext
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_CONTENT_TYPES = {"blog", "email", "press-release", "case-study", "whitepaper", "launch"}
VALID_STATUSES = {"pending", "confirmed", "cancelled"}
VALID_SYNC_STATUSES = {"synced", "syncing", "offline"}


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class CalendarEventCreate(BaseModel):
    title: str
    content_type: str = "blog"
    start_at: datetime
    end_at: Optional[datetime] = None
    all_day: bool = True
    status: str = "confirmed"
    notes: Optional[str] = None
    # Link to existing deliverable (skips atomic creation)
    deliverable_id: Optional[int] = None
    # If provided, a new Deliverable is created atomically in this folder
    project_id: Optional[int] = None
    folder_id: Optional[int] = None


class CalendarEventPatch(BaseModel):
    title: Optional[str] = None
    content_type: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    all_day: Optional[bool] = None
    status: Optional[str] = None
    # Updated by Google sync layer
    sync_status: Optional[str] = None
    google_event_id: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    synced_to_google_at: Optional[datetime] = None
    notes: Optional[str] = None
    deliverable_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _event_to_dict(event: CalendarEvent) -> dict:
    return {
        "id": event.id,
        "deliverable_id": event.deliverable_id,
        "project_id": event.project_id,
        "google_event_id": event.google_event_id,
        "title": event.title,
        "content_type": event.content_type,
        "description": event.description,
        "notes": event.notes,
        "start_at": event.start_at.isoformat(),
        "end_at": event.end_at.isoformat() if event.end_at else None,
        "all_day": event.all_day,
        "status": event.status,
        "sync_status": event.sync_status,
        "last_synced_at": event.last_synced_at.isoformat() if event.last_synced_at else None,
        "synced_to_google_at": event.synced_to_google_at.isoformat() if event.synced_to_google_at else None,
        "created_at": event.created_at.isoformat(),
        "updated_at": event.updated_at.isoformat(),
    }


def _now_utc() -> datetime:
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Routes — ordering matters: static paths before parameterised ones
# ---------------------------------------------------------------------------

@router.get("/events/upcoming")
def get_upcoming_events(
    auth: AuthContext = Depends(get_current_user),
    limit: int = 5,
    session: Session = Depends(get_session),
):
    """Return the next 7 days of events ordered by start_at ASC, capped at limit.
    Used by the dashboard 'Up Next' widget.
    """
    now = _now_utc()
    horizon = now + timedelta(days=7)
    events = session.exec(
        select(CalendarEvent)
        .where(CalendarEvent.organization_id == auth.org_id)
        .where(CalendarEvent.start_at >= now)
        .where(CalendarEvent.start_at <= horizon)
        .where(CalendarEvent.status != "cancelled")
        .order_by(CalendarEvent.start_at)
        .limit(limit)
    ).all()
    return [_event_to_dict(e) for e in events]


@router.get("/projects/{project_id}/folders")
def list_project_folders(project_id: int, auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
    """Return all folders for a project, used by NewEventModal to let the user
    choose where to place the deliverable instead of always falling back to auto-create.
    """
    folders = session.exec(
        select(Folder).where(Folder.project_id == project_id).where(Folder.organization_id == auth.org_id).order_by(Folder.name)
    ).all()
    return [{"id": f.id, "name": f.name, "parent_folder_id": f.parent_folder_id} for f in folders]


@router.get("/events")
def list_events(
    auth: AuthContext = Depends(get_current_user),
    start: Optional[str] = None,
    end: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """List events within an optional ISO date range [start, end].
    Defaults to all events when no params given.
    """
    query = select(CalendarEvent).where(CalendarEvent.organization_id == auth.org_id)
    if start:
        try:
            start_dt = datetime.fromisoformat(start)
            query = query.where(CalendarEvent.start_at >= start_dt)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid 'start' format — use ISO 8601")
    if end:
        try:
            end_dt = datetime.fromisoformat(end)
            query = query.where(CalendarEvent.start_at <= end_dt)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid 'end' format — use ISO 8601")

    events = session.exec(query.order_by(CalendarEvent.start_at)).all()
    return [_event_to_dict(e) for e in events]


@router.post("/events", status_code=201)
def create_event(data: CalendarEventCreate, auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
    """Create a CalendarEvent, optionally paired with a new Deliverable.

    Deliverable creation priority (evaluated in order):
      1. deliverable_id provided → link to existing deliverable, no new one created
      2. folder_id provided      → create Deliverable in that folder (atomic)
      3. project_id provided     → find or create a 'Content' folder in the project,
                                   then create Deliverable there (atomic, no folder
                                   lookup required from the client)
      4. neither                 → event only, no deliverable

    Returns the event dict plus 'deliverable': {id, title} when one was created or linked.
    """
    if data.content_type not in VALID_CONTENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"content_type must be one of {sorted(VALID_CONTENT_TYPES)}",
        )
    if data.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"status must be one of {sorted(VALID_STATUSES)}",
        )

    deliverable_id = data.deliverable_id
    new_deliverable = None
    resolved_folder_id = data.folder_id

    if deliverable_id is None:
        # Priority 2: explicit folder_id
        if resolved_folder_id is not None:
            folder = session.get(Folder, resolved_folder_id)
            if not folder or folder.organization_id != auth.org_id:
                raise HTTPException(status_code=404, detail="Folder not found")

        # Priority 3: project_id without folder_id — find or create default folder
        elif data.project_id is not None:
            project = session.get(Project, data.project_id)
            if not project or project.organization_id != auth.org_id:
                raise HTTPException(status_code=404, detail="Project not found")
            # Find an existing "Content" folder, else create it
            folder = session.exec(
                select(Folder)
                .where(Folder.project_id == data.project_id)
                .where(Folder.organization_id == auth.org_id)
                .where(Folder.name == "Content")
            ).first()
            if not folder:
                folder = Folder(organization_id=auth.org_id, project_id=data.project_id, name="Content")
                session.add(folder)
                session.flush()
            resolved_folder_id = folder.id

        # Create deliverable atomically if we resolved a folder
        if resolved_folder_id is not None:
            new_deliverable = Deliverable(
                organization_id=auth.org_id,
                folder_id=resolved_folder_id,
                content_type=data.content_type,
                title=data.title,
                status="draft",
            )
            session.add(new_deliverable)
            session.flush()
            deliverable_id = new_deliverable.id

    event = CalendarEvent(
        organization_id=auth.org_id,
        deliverable_id=deliverable_id,
        project_id=data.project_id,
        title=data.title,
        content_type=data.content_type,
        start_at=data.start_at,
        end_at=data.end_at,
        all_day=data.all_day,
        status=data.status,
        notes=data.notes,
        sync_status="offline",
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    if new_deliverable:
        session.refresh(new_deliverable)

    response = _event_to_dict(event)
    if new_deliverable:
        response["deliverable"] = {"id": new_deliverable.id, "title": new_deliverable.title}
    elif deliverable_id:
        response["deliverable"] = {"id": deliverable_id, "title": data.title}

    return response


@router.patch("/events/{event_id}")
def patch_event(
    event_id: int,
    data: CalendarEventPatch,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Partial update — handles drag-reschedule, status changes, and sync_status
    updates from the Google Calendar sync layer.
    """
    event = session.get(CalendarEvent, event_id)
    if not event or event.organization_id != auth.org_id:
        raise HTTPException(status_code=404, detail="Calendar event not found")

    if data.title is not None:
        event.title = data.title
    if data.content_type is not None:
        if data.content_type not in VALID_CONTENT_TYPES:
            raise HTTPException(
                status_code=422,
                detail=f"content_type must be one of {sorted(VALID_CONTENT_TYPES)}",
            )
        event.content_type = data.content_type
    if data.start_at is not None:
        event.start_at = data.start_at
    if data.end_at is not None:
        event.end_at = data.end_at
    if data.all_day is not None:
        event.all_day = data.all_day
    if data.status is not None:
        if data.status not in VALID_STATUSES:
            raise HTTPException(
                status_code=422,
                detail=f"status must be one of {sorted(VALID_STATUSES)}",
            )
        event.status = data.status
    if data.sync_status is not None:
        if data.sync_status not in VALID_SYNC_STATUSES:
            raise HTTPException(
                status_code=422,
                detail=f"sync_status must be one of {sorted(VALID_SYNC_STATUSES)}",
            )
        event.sync_status = data.sync_status
    if data.google_event_id is not None:
        event.google_event_id = data.google_event_id
    if data.last_synced_at is not None:
        event.last_synced_at = data.last_synced_at
    if data.synced_to_google_at is not None:
        event.synced_to_google_at = data.synced_to_google_at
    if data.notes is not None:
        event.notes = data.notes
    if data.deliverable_id is not None:
        event.deliverable_id = data.deliverable_id

    event.updated_at = _now_utc()
    session.add(event)
    session.commit()
    session.refresh(event)
    return _event_to_dict(event)


@router.delete("/events/{event_id}")
def delete_event(event_id: int, auth: AuthContext = Depends(get_current_user), session: Session = Depends(get_session)):
    event = session.get(CalendarEvent, event_id)
    if not event or event.organization_id != auth.org_id:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    session.delete(event)
    session.commit()
    return {"ok": True}
