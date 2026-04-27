from fastapi import APIRouter, UploadFile, File
from services.file_engine import list_skills, list_context_layers, list_core_docs, REPO_ROOT
import subprocess

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

@router.get("/references")
def get_references(path: str):
    """Get count of skills and playbooks that reference a given file"""
    skills_count = 0
    playbooks_count = 0
    
    try:
        # Search for references in skills
        result = subprocess.run(
            ["grep", "-r", "--", path],
            cwd=str(REPO_ROOT / "skills"),
            capture_output=True,
            text=True
        )
        if result.stdout:
            skills_count = len(set(l.split(":")[0] for l in result.stdout.strip().split("\n") if l))
        
        # Search for references in playbooks
        result = subprocess.run(
            ["grep", "-r", "--", path],
            cwd=str(REPO_ROOT / "playbooks"),
            capture_output=True,
            text=True
        )
        if result.stdout:
            playbooks_count = len(set(l.split(":")[0] for l in result.stdout.strip().split("\n") if l))
    except Exception:
        pass
    
    return {"skills": skills_count, "playbooks": playbooks_count}

@router.get("/api-keys")
def get_api_keys():
    """Get masked API keys from environment"""
    import os
    keys = []
    key_names = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GITHUB_TOKEN"]
    
    for key_name in key_names:
        value = os.getenv(key_name, "")
        if value:
            masked = value[:3] + "*" * max(0, len(value) - 6) + value[-3:] if len(value) > 6 else "*" * len(value)
            keys.append({
                "name": key_name,
                "value": value,
                "masked": masked
            })
    
    return keys

@router.get("/scrape-config")
def get_scrape_config():
    """Get scrape configuration"""
    return [
        {
            "id": "hackernews",
            "name": "Hacker News",
            "enabled": True,
            "params": {"daily_limit": "30"}
        },
        {
            "id": "github",
            "name": "GitHub",
            "enabled": True,
            "params": {"topics": "ai, machine-learning", "stars_min": "100"}
        },
        {
            "id": "arxiv",
            "name": "ArXiv",
            "enabled": True,
            "params": {"categories": "cs.AI, cs.LG"}
        },
        {
            "id": "reddit",
            "name": "Reddit",
            "enabled": False,
            "params": {"subreddits": "MachineLearning, artificial"}
        },
        {
            "id": "rss",
            "name": "RSS Feeds",
            "enabled": False,
            "params": {}
        }
    ]

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    destination: str = "reference",
    project_id: str | None = None,
):
    """
    Parse and append an uploaded document to a destination context file.

    destination values:
      "messaging"  → context/02_narrative/messaging-framework.md
      "strategy"   → context/03_strategy/content-strategy.md
      "voice"      → core/VOICE.md
      "project"    → context/projects/<project_id>/<filename>.md
      "reference"  → context/uploads/<filename>.md  (default)
    """
    raw_bytes = await file.read()
    filename = file.filename or "upload"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    # ── Parse content ─────────────────────────────────────────────
    content = _parse_upload(raw_bytes, ext, filename)

    # ── Determine destination path ─────────────────────────────────
    dest_path = _resolve_destination(destination, filename, project_id)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Append to destination (file watcher picks it up) ─────────
    separator = f"\n\n---\n\n<!-- uploaded: {filename} -->\n\n"
    with dest_path.open("a", encoding="utf-8") as fh:
        fh.write(separator + content)

    return {
        "filename": filename,
        "destination": str(dest_path.relative_to(REPO_ROOT)),
        "chars_written": len(content),
        "preview": content[:300],
    }


def _parse_upload(raw: bytes, ext: str, filename: str) -> str:
    """Extract plain text from uploaded file bytes."""
    if ext in ("md", "txt"):
        return raw.decode("utf-8", errors="replace")

    if ext == "pdf":
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(raw))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages).strip()
        except ImportError:
            return f"[PDF parsing unavailable — install pypdf]\n\nFilename: {filename}"
        except Exception as e:
            return f"[PDF parse error: {e}]\n\nFilename: {filename}"

    if ext == "docx":
        try:
            from docx import Document
            import io
            doc = Document(io.BytesIO(raw))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except ImportError:
            return f"[DOCX parsing unavailable — install python-docx]\n\nFilename: {filename}"
        except Exception as e:
            return f"[DOCX parse error: {e}]\n\nFilename: {filename}"

    # Fallback: try UTF-8
    return raw.decode("utf-8", errors="replace")


def _resolve_destination(destination: str, filename: str, project_id: str | None):
    """Map destination key to absolute Path."""
    mapping = {
        "messaging": REPO_ROOT / "context" / "02_narrative" / "messaging-framework.md",
        "strategy":  REPO_ROOT / "context" / "03_strategy" / "content-strategy.md",
        "voice":     REPO_ROOT / "core" / "VOICE.md",
    }
    if destination in mapping:
        return mapping[destination]
    if destination == "project" and project_id:
        safe_name = filename.replace(" ", "-").lower()
        return REPO_ROOT / "context" / "projects" / project_id / safe_name
    # Default: reference store
    safe_name = filename.replace(" ", "-").lower()
    return REPO_ROOT / "context" / "uploads" / safe_name


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

