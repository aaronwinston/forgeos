from typing import AsyncGenerator
import anthropic
from config import settings
from services.file_engine import (
    load_skill, load_playbook, load_core_doc, load_context_layer,
    REPO_ROOT
)
from instrumentation import get_tracer

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

CONTENT_TYPE_TO_PLAYBOOK = {
    "blog": "blog-production",
    "email": "newsletter",
    "press_release": "product-launch",
    "analyst_briefing": "analyst-response",
    "social_post": "social-distribution",
    "case_study": "case-study",
    "launch_copy": "product-launch",
    "lifecycle_email": "newsletter",
    "newsletter": "newsletter",
    "thought_leadership": "thought-leadership",
    "other": "blog-production",
}

def build_base_system_prompt() -> str:
    parts = []
    for doc_name in ["VOICE", "STYLE_GUIDE", "CLAIMS_POLICY", "CONTEXT"]:
        try:
            doc = load_core_doc(doc_name)
            parts.append(f"## {doc_name}\n\n{doc['content']}")
        except FileNotFoundError:
            pass
    orch_path = REPO_ROOT / "context" / "00_orchestration" / "forgeos-context-orchestrator.md"
    if orch_path.exists():
        parts.append(f"## Context Orchestrator\n\n{orch_path.read_text()}")
    return "\n\n---\n\n".join(parts) if parts else "You are a helpful marketing assistant."

def build_skill_prompt(skill_names: list[str]) -> str:
    parts = []
    for name in skill_names:
        try:
            skill = load_skill(name)
            parts.append(f"## Skill: {name}\n\n{skill['content']}")
        except FileNotFoundError:
            pass
    return "\n\n---\n\n".join(parts)

def build_context_prompt(context_refs: list[str]) -> str:
    parts = []
    for ref in context_refs:
        try:
            ctx = load_context_layer(ref)
            parts.append(f"## Context: {ref}\n\n{ctx['content']}")
        except FileNotFoundError:
            pass
    return "\n\n---\n\n".join(parts)

async def stream_chat(
    messages: list[dict],
    skill_names: list[str] = None,
    context_refs: list[str] = None,
    scrape_items: list[dict] = None,
    toggles: dict = None,
) -> AsyncGenerator[str, None]:
    tracer = get_tracer()
    user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

    span = tracer.start_span("stream_chat") if tracer else None
    if span:
        span.set_attribute("openinference.span.kind", "CHAIN")
        span.set_attribute("input.value", user_message[:2000])
        if toggles:
            span.set_attribute("content_type", toggles.get("content_type", ""))
            span.set_attribute("voice", toggles.get("voice", ""))
        if skill_names:
            span.set_attribute("skills", ", ".join(skill_names))

    try:
        system_parts = [build_base_system_prompt()]

        if skill_names:
            skill_text = build_skill_prompt(skill_names)
            if skill_text:
                system_parts.append(skill_text)

        if context_refs:
            ctx_text = build_context_prompt(context_refs)
            if ctx_text:
                system_parts.append(ctx_text)

        if scrape_items:
            items_text = "\n\n".join([
                f"### {item.get('title', 'Untitled')}\nSource: {item.get('source_url', '')}\n{item.get('body', '')[:500]}"
                for item in scrape_items[:5]
            ])
            system_parts.append(f"## Intelligence Context\n\n{items_text}")

        if toggles:
            toggle_text = f"""## Session Toggles
- audience: {toggles.get('audience', 'AI engineers and developer marketing professionals')}
- voice: {toggles.get('voice', 'thoughtful')}
- content_type: {toggles.get('content_type', 'not specified')}
- brief_first: {toggles.get('brief_first', True)}
"""
            system_parts.append(toggle_text)

        system = "\n\n---\n\n".join(system_parts)
        full_response = ""

        with client.messages.stream(
            model="claude-opus-4-5",
            max_tokens=4096,
            system=system,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                yield text

        if span:
            span.set_attribute("output.value", full_response[:2000])
    except Exception as e:
        if span:
            span.set_status(span.status.__class__.ERROR if hasattr(span, "status") else "ERROR")
        raise
    finally:
        if span:
            span.end()

async def generate_brief(
    user_prompt: str,
    content_type: str,
    toggles: dict = None,
) -> str:
    tracer = get_tracer()
    with (tracer.start_as_current_span("generate_brief") if tracer else _nullcontext()) as span:
        if span and tracer:
            span.set_attribute("openinference.span.kind", "CHAIN")
            span.set_attribute("input.value", user_prompt[:2000])
            span.set_attribute("content_type", content_type)

        system = build_base_system_prompt()
        brief_instruction = f"""
You are generating a content brief. The user wants to create: {content_type}

Generate a structured brief in markdown format with these sections:
- **Objective**: What this content needs to accomplish
- **Audience**: Who specifically this is for
- **Core Message**: The single most important thing to communicate
- **Supporting Points**: 2-4 key points
- **Proof/Evidence Needed**: What facts, examples, or data to include
- **Tone**: Voice guidance for this piece
- **Competitive Context**: Any relevant competitive considerations
- **Distribution**: Where this will live and how it will be shared
- **Success Criteria**: How we'll know this worked
"""
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2048,
            system=system + "\n\n" + brief_instruction,
            messages=[{"role": "user", "content": user_prompt}],
        )
        result = response.content[0].text

        if span and tracer:
            span.set_attribute("output.value", result[:2000])

        return result

async def execute_playbook(
    brief_md: str,
    playbook_name: str,
    toggles: dict = None,
) -> AsyncGenerator[str, None]:
    tracer = get_tracer()
    span = tracer.start_span("execute_playbook") if tracer else None
    if span:
        span.set_attribute("openinference.span.kind", "CHAIN")
        span.set_attribute("input.value", brief_md[:2000])
        span.set_attribute("playbook", playbook_name)

    try:
        try:
            playbook = load_playbook(playbook_name)
        except FileNotFoundError:
            yield f"Error: Playbook '{playbook_name}' not found."
            return

        system = build_base_system_prompt()
        system += f"\n\n---\n\n## Active Playbook: {playbook_name}\n\n{playbook['content']}"

        auto_skills = ["editorial-director", "dev-copywriter", "competitive-intelligence"]
        skill_text = build_skill_prompt(auto_skills)
        if skill_text:
            system += f"\n\n---\n\n{skill_text}"

        prompt = f"""## Content Brief

{brief_md}

## Instructions

Execute this playbook end-to-end. Work through each skill in the chain sequentially.
For each step, briefly note which skill you're applying, then produce the output.
Deliver the final draft as a complete, publish-ready document in markdown.
"""
        messages = [{"role": "user", "content": prompt}]
        full_response = ""

        async for chunk in stream_chat(messages, toggles=toggles):
            full_response += chunk
            yield chunk

        if span:
            span.set_attribute("output.value", full_response[:2000])
    except Exception:
        raise
    finally:
        if span:
            span.end()


# Context manager stub for when tracing is disabled
from contextlib import contextmanager

@contextmanager
def _nullcontext():
    yield None
