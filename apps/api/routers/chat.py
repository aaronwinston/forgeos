import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from database import get_session
from models import ChatSession, ChatMessage, ScrapeItem, Brief
from services.generation import stream_chat, generate_brief, execute_playbook, CONTENT_TYPE_TO_PLAYBOOK
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    project_id: Optional[int] = None
    message: str
    skill_names: list[str] = []
    context_refs: list[str] = []
    scrape_item_ids: list[int] = []
    toggles: dict = {}

class BriefRequest(BaseModel):
    project_id: int
    user_prompt: str
    content_type: str
    toggles: dict = {}

class GenerateRequest(BaseModel):
    brief_md: str
    content_type: str
    playbook: str = "auto"
    toggles: dict = {}

class TogglesRequest(BaseModel):
    brief_first: bool = False
    audience: str = ""
    voice: str = "thoughtful"
    skills: list[str] = []
    playbook: str = "auto"
    content_type: str = "blog"

class ContextLayersRequest(BaseModel):
    layers: list[str]

class SkillsRequest(BaseModel):
    skills: list[str]

class IntelligenceItemsRequest(BaseModel):
    items: list[int]

class BriefUpdateRequest(BaseModel):
    title: Optional[str] = None
    audience: Optional[str] = None
    description: Optional[str] = None
    toggles: Optional[dict] = None

@router.post("/session")
def create_session(
    project_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    s = ChatSession(project_id=project_id)
    session.add(s)
    session.commit()
    session.refresh(s)
    return s

@router.get("/session/{session_id}/messages")
def get_messages(session_id: int, session: Session = Depends(get_session)):
    msgs = session.exec(
        select(ChatMessage).where(ChatMessage.session_id == session_id)
    ).all()
    return msgs

@router.post("/stream")
async def chat_stream(req: ChatRequest, session: Session = Depends(get_session)):
    if req.session_id:
        chat_session = session.get(ChatSession, req.session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        chat_session = ChatSession(project_id=req.project_id)
        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)

    history = session.exec(
        select(ChatMessage).where(ChatMessage.session_id == chat_session.id)
    ).all()
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": req.message})

    user_msg = ChatMessage(session_id=chat_session.id, role="user", content=req.message)
    session.add(user_msg)
    session.commit()

    scrape_items = []
    for item_id in req.scrape_item_ids:
        item = session.get(ScrapeItem, item_id)
        if item:
            scrape_items.append({"title": item.title, "body": item.body, "source_url": item.source_url})

    session_bind = session.bind
    chat_session_id = chat_session.id

    async def event_generator():
        full_response = ""
        try:
            async for chunk in stream_chat(
                messages=messages,
                skill_names=req.skill_names or None,
                context_refs=req.context_refs or None,
                scrape_items=scrape_items or None,
                toggles=req.toggles or None,
            ):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            with Session(session_bind) as save_session:
                ai_msg = ChatMessage(
                    session_id=chat_session_id,
                    role="assistant",
                    content=full_response
                )
                save_session.add(ai_msg)
                save_session.commit()

            yield f"data: {json.dumps({'done': True, 'session_id': chat_session_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/brief")
async def generate_brief_endpoint(req: BriefRequest, session: Session = Depends(get_session)):
    brief_md = await generate_brief(
        user_prompt=req.user_prompt,
        content_type=req.content_type,
        toggles=req.toggles,
    )
    b = Brief(
        project_id=req.project_id,
        brief_md=brief_md,
        toggles_json=json.dumps(req.toggles),
    )
    session.add(b)
    session.commit()
    session.refresh(b)
    return {"brief_id": b.id, "brief_md": brief_md}

@router.post("/generate")
async def generate_deliverable(req: GenerateRequest):
    playbook_name = req.playbook
    if playbook_name == "auto":
        playbook_name = CONTENT_TYPE_TO_PLAYBOOK.get(req.content_type, "blog-production")

    async def event_gen():
        async for chunk in execute_playbook(req.brief_md, playbook_name, req.toggles):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


# Brief toggles and context management
@router.post("/briefs/{brief_id}/toggles")
def update_brief_toggles(brief_id: int, req: TogglesRequest, session: Session = Depends(get_session)):
    """Update Brief toggles (brief_first, audience, voice, skills, playbook, content_type)"""
    brief = session.get(Brief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    toggles = req.dict()
    brief.toggles_json = json.dumps(toggles)
    brief.updated_at = datetime.utcnow()
    session.add(brief)
    session.commit()
    session.refresh(brief)
    return {"id": brief.id, "toggles": toggles}


@router.post("/briefs/{brief_id}/context-layers")
def update_context_layers(brief_id: int, req: ContextLayersRequest, session: Session = Depends(get_session)):
    """Update Brief context_layers array"""
    brief = session.get(Brief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    brief.context_layers_json = json.dumps(req.layers)
    session.add(brief)
    session.commit()
    session.refresh(brief)
    return {"id": brief.id, "context_layers": req.layers}


@router.delete("/briefs/{brief_id}/context-layers/{layer_name}")
def remove_context_layer(brief_id: int, layer_name: str, session: Session = Depends(get_session)):
    """Remove one context layer from Brief"""
    brief = session.get(Brief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    layers = json.loads(brief.context_layers_json or "[]")
    layers = [l for l in layers if l != layer_name]
    brief.context_layers_json = json.dumps(layers)
    session.add(brief)
    session.commit()
    session.refresh(brief)
    return {"id": brief.id, "context_layers": layers}


@router.post("/briefs/{brief_id}/skills")
def update_skills(brief_id: int, req: SkillsRequest, session: Session = Depends(get_session)):
    """Update Brief skills array"""
    brief = session.get(Brief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    brief.skills_json = json.dumps(req.skills)
    session.add(brief)
    session.commit()
    session.refresh(brief)
    return {"id": brief.id, "skills": req.skills}


@router.delete("/briefs/{brief_id}/skills/{skill_name}")
def remove_skill(brief_id: int, skill_name: str, session: Session = Depends(get_session)):
    """Remove one skill from Brief"""
    brief = session.get(Brief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    skills = json.loads(brief.skills_json or "[]")
    skills = [s for s in skills if s != skill_name]
    brief.skills_json = json.dumps(skills)
    session.add(brief)
    session.commit()
    session.refresh(brief)
    return {"id": brief.id, "skills": skills}


@router.post("/briefs/{brief_id}/intelligence-items")
def update_intelligence_items(brief_id: int, req: IntelligenceItemsRequest, session: Session = Depends(get_session)):
    """Update Brief intelligence_items array"""
    brief = session.get(Brief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    brief.intelligence_items_json = json.dumps(req.items)
    session.add(brief)
    session.commit()
    session.refresh(brief)
    return {"id": brief.id, "intelligence_items": req.items}


@router.delete("/briefs/{brief_id}/intelligence-items/{item_id}")
def remove_intelligence_item(brief_id: int, item_id: int, session: Session = Depends(get_session)):
    """Remove one intelligence item from Brief"""
    brief = session.get(Brief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    items = json.loads(brief.intelligence_items_json or "[]")
    items = [i for i in items if i != item_id]
    brief.intelligence_items_json = json.dumps(items)
    session.add(brief)
    session.commit()
    session.refresh(brief)
    return {"id": brief.id, "intelligence_items": items}


@router.put("/briefs/{brief_id}")
def update_brief(brief_id: int, req: BriefUpdateRequest, session: Session = Depends(get_session)):
    """Update Brief fields: title, audience, description, and toggles"""
    brief = session.get(Brief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    if req.title is not None:
        brief.title = req.title
    if req.audience is not None:
        brief.audience = req.audience
    if req.description is not None:
        brief.description = req.description
        brief.brief_md = req.description
    if req.toggles is not None:
        brief.toggles_json = json.dumps(req.toggles)
    
    brief.updated_at = datetime.utcnow()
    session.add(brief)
    session.commit()
    session.refresh(brief)
    
    return {
        "id": brief.id,
        "title": brief.title,
        "audience": brief.audience,
        "description": brief.description,
        "brief_md": brief.brief_md,
        "toggles": json.loads(brief.toggles_json) if brief.toggles_json else {},
    }


# Let's Build modal endpoints
class BriefGuideRequest(BaseModel):
    messages: list[dict]
    toggles: dict = {}
    mode: str = "guided"


class BriefYoloRequest(BaseModel):
    prompt: str
    toggles: dict = {}


@router.post("/brief-guided")
async def brief_guided(req: BriefGuideRequest, session: Session = Depends(get_session)):
    """Guided mode: conversational brief creation with streaming and state machine.
    
    Agent returns JSON when complete: {"state": "complete", "brief_md": "..."}
    """
    system = """You are a creative brief guide helping Aaron create marketing content.

Your job: Ask only the key questions needed for a complete brief, then return structured JSON.

Questions to ask (in order):
1. Audience: Who is this for?
2. Voice: What tone? (opinionated/thoughtful/objective/technical/founder)
3. Format: What type? (blog/email/social/press/case-study/analyst)
4. Success Criteria: How will we know this worked?
5. Supporting Context: Any important details?

CRITICAL RULES:
- Skip any question where the user/toggles already provided an answer
- When you have answers to all unasked questions, generate a complete brief
- Return your final response as JSON ONLY, no other text:

{
  "state": "complete",
  "brief_md": "# Brief\\n\\n**Objective**: ...\\n\\n**Audience**: ...\\n\\n**Core Message**: ...\\n\\n**Supporting Points**: ...\\n\\n**Tone**: ...\\n\\n**Success Criteria**: ..."
}

Do NOT output anything else after the JSON. The JSON is your final response."""

    # Build toggle context from presets
    toggle_context = ""
    if req.toggles:
        toggle_context = "\n\nPreset Values (skip questions for these):\n"
        for k, v in req.toggles.items():
            if v:
                toggle_context += f"- {k}: {v}\n"
    
    # Inject system + toggles into messages
    messages = req.messages.copy()
    
    async def event_generator():
        full_response = ""
        try:
            async for chunk in stream_chat(
                messages=messages,
                toggles=req.toggles,
            ):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Parse the response to check if agent completed (returned JSON with state: complete)
            try:
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', full_response, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                    if response_data.get("state") == "complete":
                        # Agent successfully generated brief
                        brief_md = response_data.get("brief_md", "")
                        yield f"data: {json.dumps({'done': True, 'brief_md': brief_md, 'state': 'complete'})}\n\n"
                    else:
                        # Incomplete (agent asking another question)
                        yield f"data: {json.dumps({'done': False, 'state': 'incomplete'})}\n\n"
                else:
                    # No JSON found, agent is asking a question
                    yield f"data: {json.dumps({'done': False, 'state': 'incomplete'})}\n\n"
            except (json.JSONDecodeError, AttributeError):
                # If we can't parse, assume incomplete
                yield f"data: {json.dumps({'done': False, 'state': 'incomplete'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/brief-yolo")
async def brief_yolo(req: BriefYoloRequest, session: Session = Depends(get_session)):
    """YOLO mode: atomic one-shot brief + deliverable creation.
    
    Creates Brief and Deliverable in a single transaction.
    Returns both on success, or error if any step fails.
    """
    try:
        content_type = req.toggles.get("content_type", "blog")
        
        # Generate brief using existing function
        brief_md = await generate_brief(
            user_prompt=req.prompt,
            content_type=content_type,
            toggles=req.toggles,
        )
        
        # Get or create default project
        project = session.exec(
            select(Project).where(Project.user_id == "aaron")
        ).first()
        if not project:
            project = Project(user_id="aaron", name="Default Project")
            session.add(project)
            session.commit()
            session.refresh(project)
        
        # Get or create default folder
        folder = session.exec(
            select(Folder).where(Folder.project_id == project.id)
        ).first()
        if not folder:
            folder = Folder(project_id=project.id, name="Deliverables")
            session.add(folder)
            session.commit()
            session.refresh(folder)
        
        # Create Brief (atomic transaction)
        brief = Brief(
            project_id=project.id,
            title=content_type.replace("_", " ").title(),
            brief_md=brief_md,
            toggles_json=json.dumps(req.toggles),
        )
        session.add(brief)
        session.flush()  # Get ID without committing yet
        
        # Create Deliverable in same transaction
        deliverable = Deliverable(
            folder_id=folder.id,
            content_type=content_type,
            title=content_type.replace("_", " ").title(),
            status="draft",
            body_md="",
        )
        session.add(deliverable)
        
        # Commit both together (atomic)
        session.commit()
        session.refresh(brief)
        session.refresh(deliverable)
        
        return {
            "brief": {
                "id": brief.id,
                "title": brief.title,
                "brief_md": brief.brief_md,
                "toggles_json": brief.toggles_json,
            },
            "deliverable": {
                "id": deliverable.id,
                "folder_id": deliverable.folder_id,
                "content_type": deliverable.content_type,
                "title": deliverable.title,
                "status": deliverable.status,
            }
        }
    except Exception as e:
        # Rollback on any error
        session.rollback()
        raise HTTPException(status_code=400, detail=f"YOLO creation failed: {str(e)}")
