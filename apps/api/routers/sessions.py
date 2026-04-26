import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from database import get_session
from models import PipelineRun, Brief, Deliverable, Folder, Project
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

_session_queues: dict[int, asyncio.Queue] = {}

class SessionCreate(BaseModel):
    title: str
    type: str = "blog"
    audience: Optional[str] = None
    description: Optional[str] = None

class SessionUpdate(BaseModel):
    status: Optional[str] = None
    current_agent: Optional[str] = None
    progress: Optional[int] = None
    output: Optional[str] = None

@router.post("")
def create_session(data: SessionCreate, session: Session = Depends(get_session)):
    # Ensure we have a default project
    project = session.exec(
        select(Project).where(Project.user_id == "aaron")
    ).first()
    if not project:
        project = Project(user_id="aaron", name="Default Project")
        session.add(project)
        session.commit()
        session.refresh(project)
    
    # Ensure we have a default folder
    folder = session.exec(
        select(Folder).where(Folder.project_id == project.id)
    ).first()
    if not folder:
        folder = Folder(project_id=project.id, name="Deliverables")
        session.add(folder)
        session.commit()
        session.refresh(folder)
    
    # Create Brief
    brief = Brief(
        user_id="aaron",
        project_id=project.id,
        title=data.title,
        audience=data.audience,
        description=data.description,
        brief_md=data.description or f"Create a {data.type} for {data.audience or 'our audience'}: {data.title}"
    )
    session.add(brief)
    session.commit()
    session.refresh(brief)
    
    # Create Deliverable
    deliverable = Deliverable(
        folder_id=folder.id,
        title=data.title,
        content_type=data.type,
        status="draft",
        body_md=""
    )
    session.add(deliverable)
    session.commit()
    session.refresh(deliverable)
    
    # Create PipelineRun
    pipeline_run = PipelineRun(
        brief_id=brief.id,
        deliverable_id=deliverable.id,
        title=data.title,
        type=data.type,
        audience=data.audience,
        description=data.description,
        status="pending"
    )
    session.add(pipeline_run)
    session.commit()
    session.refresh(pipeline_run)
    
    return {
        "pipeline_run": pipeline_run,
        "brief": brief,
        "deliverable": deliverable
    }

@router.get("")
def list_sessions(session: Session = Depends(get_session)):
    sessions = session.exec(
        select(PipelineRun)
        .where(PipelineRun.deleted == False)
        .order_by(PipelineRun.created_at.desc())
    ).all()
    return sessions

@router.get("/{session_id}")
def get_session_by_id(session_id: int, session: Session = Depends(get_session)):
    s = session.get(PipelineRun, session_id)
    if not s or s.deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return s

@router.put("/{session_id}")
def update_session(session_id: int, data: SessionUpdate, session: Session = Depends(get_session)):
    s = session.get(PipelineRun, session_id)
    if not s or s.deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    for field, value in data.dict(exclude_none=True).items():
        setattr(s, field, value)
    s.updated_at = datetime.utcnow()
    session.add(s)
    session.commit()
    session.refresh(s)
    return s

@router.delete("/{session_id}")
def delete_session(session_id: int, session: Session = Depends(get_session)):
    s = session.get(PipelineRun, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    s.deleted = True
    s.updated_at = datetime.utcnow()
    session.add(s)
    session.commit()
    return {"ok": True}

@router.post("/{session_id}/run")
async def run_session(session_id: int, session: Session = Depends(get_session)):
    s = session.get(PipelineRun, session_id)
    if not s or s.deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    
    queue = asyncio.Queue()
    _session_queues[session_id] = queue
    
    brief = s.description or f"Create a {s.type} for {s.audience or 'our audience'}: {s.title}"
    playbook_name = s.type or "blog-production"
    
    async def run():
        from services.generation import execute_playbook
        from database import engine
        from sqlmodel import Session as DBSession
        
        async def on_update(event: dict):
            await queue.put(event)
            with DBSession(engine) as db:
                sess = db.get(PipelineRun, session_id)
                if sess:
                    if event.get("type") == "agent_update":
                        sess.current_agent = event["agent"]
                        sess.progress = event["progress"]
                        sess.status = "active"
                    elif event.get("type") == "agent_complete":
                        sess.progress = event["progress"]
                    db.add(sess)
                    db.commit()
        
        final_output = ""
        with DBSession(engine) as db:
            async for chunk in execute_playbook(
                brief, 
                playbook_name, 
                pipeline_run_id=session_id,
                db_session=db
            ):
                final_output += chunk
                await on_update({
                    "type": "agent_update",
                    "agent": "playbook",
                    "status": "active",
                    "progress": int(len(final_output) / 100),
                    "output": final_output
                })
        
        with DBSession(engine) as db:
            sess = db.get(PipelineRun, session_id)
            if sess:
                sess.status = "complete"
                sess.progress = 100
                sess.updated_at = datetime.utcnow()
                db.add(sess)
                db.commit()
        
        await queue.put({"type": "done", "output": final_output})
        del _session_queues[session_id]
    
    asyncio.create_task(run())
    return {"ok": True, "session_id": session_id}

@router.get("/{session_id}/stream")
async def stream_session(session_id: int):
    queue = _session_queues.get(session_id)
    
    async def event_gen():
        if queue is None:
            yield f"data: {json.dumps({'type': 'no_stream'})}\n\n"
            return
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("type") == "done":
                break
    
    return StreamingResponse(event_gen(), media_type="text/event-stream")
