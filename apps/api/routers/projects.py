from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models import Project, Folder, Deliverable, Brief, ScrapeItem
from middleware.auth import get_current_user, AuthContext
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json

router = APIRouter(prefix="/api", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.get("/projects")
def list_projects(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return session.exec(
        select(Project).where(Project.organization_id == auth.org_id)
    ).all()

@router.post("/projects")
def create_project(
    data: ProjectCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    p = Project(
        name=data.name,
        description=data.description,
        organization_id=auth.org_id,
        user_id=auth.user_id,
    )
    session.add(p)
    session.commit()
    session.refresh(p)
    return p

@router.get("/projects/{project_id}")
def get_project(
    project_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    p = session.exec(
        select(Project).where(
            (Project.id == project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

@router.put("/projects/{project_id}")
def update_project(
    project_id: int,
    data: ProjectCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    p = session.exec(
        select(Project).where(
            (Project.id == project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    p.name = data.name
    if data.description is not None:
        p.description = data.description
    session.add(p)
    session.commit()
    session.refresh(p)
    return p

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    p = session.exec(
        select(Project).where(
            (Project.id == project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(p)
    session.commit()
    return {"ok": True}

class FolderCreate(BaseModel):
    project_id: int
    parent_folder_id: Optional[int] = None
    name: str

@router.get("/projects/{project_id}/folders")
def list_folders(
    project_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify project belongs to org
    p = session.exec(
        select(Project).where(
            (Project.id == project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return session.exec(
        select(Folder).where(
            (Folder.project_id == project_id) & (Folder.organization_id == auth.org_id)
        )
    ).all()

@router.get("/folders/{folder_id}")
def get_folder(
    folder_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    f = session.exec(
        select(Folder).where(
            (Folder.id == folder_id) & (Folder.organization_id == auth.org_id)
        )
    ).first()
    if not f:
        raise HTTPException(status_code=404, detail="Folder not found")
    return f

@router.post("/folders")
def create_folder(
    data: FolderCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify project belongs to org
    p = session.exec(
        select(Project).where(
            (Project.id == data.project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    
    f = Folder(
        project_id=data.project_id,
        parent_folder_id=data.parent_folder_id,
        name=data.name,
        organization_id=auth.org_id,
    )
    session.add(f)
    session.commit()
    session.refresh(f)
    return f

@router.delete("/folders/{folder_id}")
def delete_folder(folder_id: int, session: Session = Depends(get_session)):
    f = session.get(Folder, folder_id)
    if not f:
        raise HTTPException(status_code=404, detail="Folder not found")
    session.delete(f)
    session.commit()
    return {"ok": True}

class DeliverableCreate(BaseModel):
    folder_id: Optional[int] = None
    content_type: str
    title: str
    status: str = "draft"
    body_md: Optional[str] = None
    metadata_json: Optional[str] = None

class DeliverableUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    body_md: Optional[str] = None

@router.get("/folders/{folder_id}/deliverables")
def list_deliverables(folder_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Deliverable).where(Deliverable.folder_id == folder_id)).all()

@router.post("/deliverables")
def create_deliverable(data: DeliverableCreate, session: Session = Depends(get_session)):
    # Get or create default folder if not specified
    if not data.folder_id:
        project = session.exec(
            select(Project).where(Project.user_id == "aaron")
        ).first()
        if not project:
            project = Project(user_id="aaron", name="Default Project")
            session.add(project)
            session.commit()
            session.refresh(project)
        
        folder = session.exec(
            select(Folder).where(Folder.project_id == project.id)
        ).first()
        if not folder:
            folder = Folder(project_id=project.id, name="Deliverables")
            session.add(folder)
            session.commit()
            session.refresh(folder)
        folder_id = folder.id
    else:
        folder_id = data.folder_id
    
    d = Deliverable(
        folder_id=folder_id,
        content_type=data.content_type,
        title=data.title,
        status=data.status,
        body_md=data.body_md,
    )
    session.add(d)
    session.commit()
    session.refresh(d)
    return d

@router.get("/deliverables/{deliverable_id}")
def get_deliverable(deliverable_id: int, session: Session = Depends(get_session)):
    d = session.get(Deliverable, deliverable_id)
    if not d:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    return d

@router.put("/deliverables/{deliverable_id}")
def update_deliverable(deliverable_id: int, data: DeliverableUpdate, session: Session = Depends(get_session)):
    d = session.get(Deliverable, deliverable_id)
    if not d:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    update_data = data.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(d, k, v)
    d.updated_at = datetime.utcnow()
    session.add(d)
    session.commit()
    session.refresh(d)
    return d

@router.delete("/deliverables/{deliverable_id}")
def delete_deliverable(deliverable_id: int, session: Session = Depends(get_session)):
    d = session.get(Deliverable, deliverable_id)
    if not d:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    session.delete(d)
    session.commit()
    return {"ok": True}

class BriefCreate(BaseModel):
    project_id: Optional[int] = None
    deliverable_id: Optional[int] = None
    title: Optional[str] = None
    brief_md: str
    toggles_json: Optional[str] = None

@router.post("/briefs")
def create_brief(data: BriefCreate, session: Session = Depends(get_session)):
    # Get or create default project if not specified
    if not data.project_id:
        project = session.exec(
            select(Project).where(Project.user_id == "aaron")
        ).first()
        if not project:
            project = Project(user_id="aaron", name="Default Project")
            session.add(project)
            session.commit()
            session.refresh(project)
        project_id = project.id
    else:
        project_id = data.project_id
    
    b = Brief(
        project_id=project_id,
        deliverable_id=data.deliverable_id,
        title=data.title or "Untitled Brief",
        brief_md=data.brief_md,
        toggles_json=data.toggles_json,
    )
    session.add(b)
    session.commit()
    session.refresh(b)
    return b

@router.get("/briefs/{brief_id}")
def get_brief(brief_id: int, session: Session = Depends(get_session)):
    b = session.get(Brief, brief_id)
    if not b:
        raise HTTPException(status_code=404, detail="Brief not found")
    return b

@router.get("/projects/{project_id}/briefs")
def list_project_briefs(project_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Brief).where(Brief.project_id == project_id)).all()

@router.get("/deliverables/{deliverable_id}/brief")
def get_deliverable_brief(deliverable_id: int, session: Session = Depends(get_session)):
    b = session.exec(select(Brief).where(Brief.deliverable_id == deliverable_id)).first()
    if not b:
        return None
    return b


class WorkspaceFromItemRequest(BaseModel):
    scrape_item_id: int
    title: str
    content_type: str = "blog"


@router.post("/workspace/from-briefing-item")
def workspace_from_briefing_item(
    data: WorkspaceFromItemRequest,
    session: Session = Depends(get_session),
):
    """
    Create a Deliverable + Brief with a ScrapeItem pre-attached as context,
    then return the deliverable ID for workspace navigation.
    """
    item = session.get(ScrapeItem, data.scrape_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Briefing item not found")

    # Get or create the default inbox project + folder
    project = session.exec(
        select(Project).where(Project.user_id == "aaron")
    ).first()
    if not project:
        project = Project(user_id="aaron", name="Default Project")
        session.add(project)
        session.commit()
        session.refresh(project)

    folder = session.exec(
        select(Folder).where(Folder.project_id == project.id)
    ).first()
    if not folder:
        folder = Folder(project_id=project.id, name="Inbox")
        session.add(folder)
        session.commit()
        session.refresh(folder)

    # Create deliverable
    deliverable = Deliverable(
        folder_id=folder.id,
        content_type=data.content_type,
        title=data.title,
        status="draft",
    )
    session.add(deliverable)
    session.commit()
    session.refresh(deliverable)

    # Create brief with the scrape item pre-loaded as intelligence context
    brief = Brief(
        project_id=project.id,
        deliverable_id=deliverable.id,
        title=data.title,
        brief_md="",
        intelligence_items_json=json.dumps([data.scrape_item_id]),
    )
    session.add(brief)
    session.commit()

    # Mark item as surfaced
    item.surfaced_to_user_at = datetime.utcnow()
    session.add(item)
    session.commit()

    return {"deliverable_id": deliverable.id, "brief_id": brief.id}


class CalendarEventCreate(BaseModel):
    deliverable_id: int
    title: str
    description: Optional[str] = None
    start_at: datetime
    end_at: datetime


@router.post("/calendar/events")
def create_calendar_event(data: CalendarEventCreate, session: Session = Depends(get_session)):
    """
    Create a calendar event linked to a deliverable.
    
    Event is created locally immediately and synced to Google Calendar asynchronously.
    Frontend receives event ID and sync status right away.
    """
    from services.calendar import create_event_atomic
    
    try:
        event = create_event_atomic(
            title=data.title,
            start_at=data.start_at,
            end_at=data.end_at,
            deliverable_id=data.deliverable_id,
            description=data.description,
        )
        return {
            "status": "created",
            "event": event,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create calendar event: {str(e)}")


@router.get("/calendar/events/{deliverable_id}")
def get_calendar_event(deliverable_id: int, session: Session = Depends(get_session)):
    """Get calendar event for a deliverable."""
    from models import CalendarEvent
    
    event = session.exec(
        select(CalendarEvent).where(CalendarEvent.deliverable_id == deliverable_id)
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="No calendar event for this deliverable")
    
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "start_at": event.start_at.isoformat(),
        "end_at": event.end_at.isoformat(),
        "status": event.status,
        "google_event_id": event.google_event_id,
        "synced_to_google_at": event.synced_to_google_at.isoformat() if event.synced_to_google_at else None,
        "last_synced_at": event.last_synced_at.isoformat() if event.last_synced_at else None,
    }


@router.put("/calendar/events/{event_id}")
def update_calendar_event(event_id: int, data: CalendarEventCreate, session: Session = Depends(get_session)):
    """Update a calendar event."""
    from models import CalendarEvent
    from services.calendar import sync_to_google
    
    event = session.get(CalendarEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    event.title = data.title
    event.description = data.description
    event.start_at = data.start_at
    event.end_at = data.end_at
    event.updated_at = datetime.utcnow()
    session.add(event)
    session.commit()
    
    sync_to_google(event_id)
    
    return {
        "status": "updated",
        "event_id": event_id,
    }


@router.delete("/calendar/events/{event_id}")
def delete_calendar_event(event_id: int, session: Session = Depends(get_session)):
    """Delete a calendar event (archives it, doesn't hard-delete)."""
    from models import CalendarEvent
    
    event = session.get(CalendarEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    event.status = "archived"
    event.updated_at = datetime.utcnow()
    session.add(event)
    session.commit()
    
    return {"status": "archived", "event_id": event_id}
