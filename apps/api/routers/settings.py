from fastapi import APIRouter, UploadFile, File
from services.file_engine import list_skills, list_context_layers, list_core_docs, REPO_ROOT
import shutil

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("/context")
def get_context_files():
    return list_context_layers()

@router.get("/skills")
def get_skill_files():
    return list_skills()

@router.get("/core")
def get_core_files():
    return list_core_docs()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    staging_dir = REPO_ROOT / "_uploads"
    staging_dir.mkdir(exist_ok=True)
    dest = staging_dir / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    content = dest.read_text(errors="ignore")
    return {
        "filename": file.filename,
        "size": dest.stat().st_size,
        "preview": content[:500],
        "suggested_layer": _suggest_layer(file.filename, content),
    }

def _suggest_layer(filename: str, content: str) -> str:
    fn = filename.lower()
    if "messaging" in fn or "positioning" in fn:
        return "context/02_narrative/"
    if "strategy" in fn or "blueprint" in fn:
        return "context/03_strategy/"
    if "analyst" in fn or "ar-" in fn:
        return "context/06_influence/"
    if "research" in fn:
        return "context/07_research/"
    if "philosophy" in fn or "manifesto" in fn:
        return "context/01_philosophy/"
    return "context/05_patterns/"
