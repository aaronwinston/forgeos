from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.file_engine import (
    load_markdown_file, write_markdown_file, list_skills,
    list_playbooks, list_context_layers, list_core_docs, get_file_tree
)
from services.file_expansion import FileExpansionService
from typing import Optional, List

router = APIRouter(prefix="/api/files", tags=["files"])

class WriteRequest(BaseModel):
    path: str
    content: str

class ExpandInitRequest(BaseModel):
    file_path: str

class ExpandMessageRequest(BaseModel):
    file_path: str
    conversation_id: str
    message: str
    request_draft: bool = False

class ExpandDraftRequest(BaseModel):
    file_path: str
    conversation_id: str

@router.get("/tree")
def file_tree():
    return get_file_tree()

@router.get("/skills")
def get_skills():
    return list_skills()

@router.get("/playbooks")
def get_playbooks():
    return list_playbooks()

@router.get("/context-layers")
def get_context_layers():
    return list_context_layers()

@router.get("/core-docs")
def get_core_docs():
    return list_core_docs()

@router.get("/read")
def read_file(path: str):
    try:
        return load_markdown_file(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/write")
def write_file(req: WriteRequest):
    try:
        return write_markdown_file(req.path, req.content)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/expand/init")
async def expand_init(req: ExpandInitRequest):
    """Initialize a file expansion session."""
    try:
        service = FileExpansionService()
        content, success = service.read_file(req.file_path)
        
        if not success:
            raise HTTPException(status_code=404, detail=content)
        
        context = service.get_context_for_file(req.file_path)
        system_prompt = service.generate_expansion_prompt(req.file_path, content, context)
        
        # Generate initial question
        from anthropic import Anthropic
        client = Anthropic()
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": "I'm ready to expand this file. What's your first question?"
                }
            ]
        )
        
        initial_response = message.content[0].text if message.content else ""
        
        import uuid
        conversation_id = str(uuid.uuid4())
        
        return {
            "conversation_id": conversation_id,
            "file_path": req.file_path,
            "initial_message": initial_response,
            "word_count": len(content.split())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/expand/message")
async def expand_message(req: ExpandMessageRequest):
    """Send a message in the file expansion conversation."""
    try:
        service = FileExpansionService()
        content, _ = service.read_file(req.file_path)
        context = service.get_context_for_file(req.file_path)
        system_prompt = service.generate_expansion_prompt(req.file_path, content, context)
        
        # For simplicity, we don't persist conversation state in this basic version
        # In production, you'd store conversation history in the database
        
        from anthropic import Anthropic
        client = Anthropic()
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": req.message
                }
            ]
        )
        
        response = message.content[0].text if message.content else ""
        
        return {
            "conversation_id": req.conversation_id,
            "response": response,
            "ready_for_draft": "draft" in response.lower() or "now" in response.lower()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/expand/draft")
async def expand_draft(req: ExpandDraftRequest):
    """Generate the final draft."""
    try:
        service = FileExpansionService()
        content, _ = service.read_file(req.file_path)
        
        # In production, fetch actual conversation history from database
        # For MVP, use a simple context
        draft = service.generate_draft(
            req.file_path,
            content,
            [
                {
                    "role": "user",
                    "content": "Based on what we've discussed, please generate the draft now."
                }
            ]
        )
        
        return {
            "file_path": req.file_path,
            "draft": draft,
            "word_count": len(draft.split())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/expand/save-draft")
async def save_draft(req: WriteRequest):
    """Save the expanded draft to the file."""
    try:
        return write_markdown_file(req.path, req.content)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
