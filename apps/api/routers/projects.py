from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models import Project, Folder, Deliverable, Brief
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.get("/projects")
def list_projects(session: Session = Depends(get_session)):
    return session.exec(select(Project)).all()

@router.post("/projects")
def create_project(data: ProjectCreate, session: Session = Depends(get_session)):
    p = Project(name=data.name, description=data.description)
    session.add(p)
    session.commit()
    session.refresh(p)
    return p

@router.get("/projects/{project_id}")
def get_project(project_id: int, session: Session = Depends(get_session)):
    p = session.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

@router.put("/projects/{project_id}")
def update_project(project_id: int, data: ProjectCreate, session: Session = Depends(get_session)):
    p = session.get(Project, project_id)
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
def delete_project(project_id: int, session: Session = Depends(get_session)):
    p = session.get(Project, project_id)
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
def list_folders(project_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Folder).where(Folder.project_id == project_id)).all()

@router.get("/folders/{folder_id}")
def get_folder(folder_id: int, session: Session = Depends(get_session)):
    f = session.get(Folder, folder_id)
    if not f:
        raise HTTPException(status_code=404, detail="Folder not found")
    return f

@router.post("/folders")
def create_folder(data: FolderCreate, session: Session = Depends(get_session)):
    f = Folder(**data.dict())
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
    folder_id: int
    content_type: str
    title: str
    status: str = "draft"
    body_md: Optional[str] = None

class DeliverableUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    body_md: Optional[str] = None

@router.get("/folders/{folder_id}/deliverables")
def list_deliverables(folder_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Deliverable).where(Deliverable.folder_id == folder_id)).all()

@router.post("/deliverables")
def create_deliverable(data: DeliverableCreate, session: Session = Depends(get_session)):
    d = Deliverable(**data.dict())
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
    project_id: int
    deliverable_id: Optional[int] = None
    brief_md: str
    toggles_json: Optional[str] = None

@router.post("/briefs")
def create_brief(data: BriefCreate, session: Session = Depends(get_session)):
    b = Brief(**data.dict())
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
