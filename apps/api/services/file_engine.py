from pathlib import Path
import frontmatter
from config import settings

REPO_ROOT = settings.REPO_ROOT

CANONICAL_DIRS = [
    "skills", "playbooks", "context", "core", "briefs",
    "rubrics", "prompts", "examples", "tests", "workflows"
]

def _resolve_safe_path(rel_path: str) -> Path:
    p = (REPO_ROOT / rel_path).resolve()
    allowed = [REPO_ROOT / d for d in CANONICAL_DIRS]
    if not any(str(p).startswith(str(d)) for d in allowed):
        raise ValueError(f"Path {rel_path} is outside canonical directories")
    return p

def load_markdown_file(rel_path: str) -> dict:
    p = _resolve_safe_path(rel_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {rel_path}")
    post = frontmatter.load(str(p))
    return {
        "path": rel_path,
        "metadata": dict(post.metadata),
        "content": post.content,
        "raw": p.read_text()
    }

def write_markdown_file(rel_path: str, content: str) -> dict:
    p = _resolve_safe_path(rel_path)
    p.write_text(content)
    result = {"path": rel_path, "success": True, "lint_warnings": []}
    if "skills/" in rel_path and rel_path.endswith("SKILL.md"):
        import subprocess
        lint_script = REPO_ROOT / "apps" / "api" / "scripts" / "lint_skill_files.py"
        r = subprocess.run(["python3", str(lint_script)], capture_output=True, text=True, cwd=str(REPO_ROOT))
        if r.returncode != 0:
            result["lint_warnings"] = r.stdout.splitlines() + r.stderr.splitlines()
    return result

def list_skills() -> list[dict]:
    skills_dir = REPO_ROOT / "skills"
    results = []
    for skill_file in skills_dir.rglob("SKILL.md"):
        try:
            post = frontmatter.load(str(skill_file))
            rel = str(skill_file.relative_to(REPO_ROOT))
            category = skill_file.parent.parent.name
            name = skill_file.parent.name
            results.append({
                "name": name,
                "category": category,
                "path": rel,
                "description": post.metadata.get("description", ""),
            })
        except Exception:
            pass
    return sorted(results, key=lambda x: x["name"])

def list_playbooks() -> list[dict]:
    pb_dir = REPO_ROOT / "playbooks"
    results = []
    if not pb_dir.exists():
        return results
    for f in pb_dir.glob("*.md"):
        if f.name == "README.md":
            continue
        post = frontmatter.load(str(f))
        results.append({
            "name": f.stem,
            "path": str(f.relative_to(REPO_ROOT)),
            "title": post.content.split("\n")[0].lstrip("# ").strip() if post.content else f.stem,
        })
    return sorted(results, key=lambda x: x["name"])

def list_context_layers() -> list[dict]:
    ctx_dir = REPO_ROOT / "context"
    results = []
    if not ctx_dir.exists():
        return results
    for f in sorted(ctx_dir.rglob("*.md")):
        if f.name == "README.md":
            continue
        layer = f.parent.name
        results.append({
            "layer": layer,
            "name": f.stem,
            "path": str(f.relative_to(REPO_ROOT)),
        })
    return results

def list_core_docs() -> list[dict]:
    core_dir = REPO_ROOT / "core"
    if not core_dir.exists():
        return []
    return [
        {"name": f.stem, "path": str(f.relative_to(REPO_ROOT))}
        for f in sorted(core_dir.glob("*.md"))
    ]

def load_skill(name: str) -> dict:
    skills_dir = REPO_ROOT / "skills"
    for skill_file in skills_dir.rglob("SKILL.md"):
        if skill_file.parent.name == name:
            return load_markdown_file(str(skill_file.relative_to(REPO_ROOT)))
    raise FileNotFoundError(f"Skill not found: {name}")

def load_playbook(name: str) -> dict:
    p = REPO_ROOT / "playbooks" / f"{name}.md"
    if not p.exists():
        raise FileNotFoundError(f"Playbook not found: {name}")
    return load_markdown_file(str(p.relative_to(REPO_ROOT)))

def load_context_layer(name: str) -> dict:
    ctx_dir = REPO_ROOT / "context"
    for f in ctx_dir.rglob("*.md"):
        if f.stem == name:
            return load_markdown_file(str(f.relative_to(REPO_ROOT)))
    raise FileNotFoundError(f"Context layer not found: {name}")

def load_core_doc(name: str) -> dict:
    core_dir = REPO_ROOT / "core"
    for f in core_dir.glob("*.md"):
        if f.stem.upper() == name.upper():
            return load_markdown_file(str(f.relative_to(REPO_ROOT)))
    raise FileNotFoundError(f"Core doc not found: {name}")

def get_file_tree() -> dict:
    tree = {}
    for d in CANONICAL_DIRS:
        dir_path = REPO_ROOT / d
        if not dir_path.exists():
            continue
        files = []
        for f in sorted(dir_path.rglob("*.md")):
            files.append(str(f.relative_to(REPO_ROOT)))
        tree[d] = files
    return tree
