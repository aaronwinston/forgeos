from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.file_engine import (
    load_markdown_file, write_markdown_file, list_skills,
    list_playbooks, list_context_layers, list_core_docs, get_file_tree
)

router = APIRouter(prefix="/api/files", tags=["files"])

class WriteRequest(BaseModel):
    path: str
    content: str

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
