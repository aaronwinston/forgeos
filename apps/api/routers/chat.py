import json
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
