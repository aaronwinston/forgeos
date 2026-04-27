import json
import re
from config import settings
from services.llm import get_provider
from instrumentation import get_tracer
REPO_ROOT = settings.REPO_ROOT

def load_scoring_prompt() -> str:
    scoring_file = REPO_ROOT / "context" / "07_research" / "intelligence-scoring-prompt.md"
    if scoring_file.exists():
        return scoring_file.read_text()
    return """
You are scoring intelligence items for Aaron Winston, head of content, comms, and AR at Arize AI.

Score each item 1-10 on relevance to Aaron's interests:
- How developers and companies are building with AI agents
- Agent harnesses, self-improving agents, eval frameworks
- Production AI observability and reliability
- Arize AX and Phoenix (Arize's products)
- Competitor moves in AI observability and LLM evaluation
- Industry tensions, debates, and takes worth reacting to
- Research that would change how developers build AI systems

10 = must read, directly actionable
7-9 = highly relevant, surface to user
4-6 = somewhat relevant, borderline
1-3 = not relevant

Return ONLY a JSON object: {"score": <number>, "reasoning": "<one sentence>"}
"""

def load_synthesis_prompt() -> str:
    """Load synthesis prompt for generating why_relevant and content_angle"""
    return """You are the editorial director for an AI company's marketing team (Arize AI).
Your audience is Aaron Winston, head of content, comms, and AR.
Generate two concise lines for this intelligence item:

1. why_relevant: 1-2 sentences explaining why this matters to Aaron's interests in AI observability, agents, and developer tools
2. content_angle: 1-2 sentences suggesting how to use this as content (blog post, email, social media, etc.)

Return ONLY a JSON object: {"why_relevant": "<text>", "content_angle": "<text>"}
"""

async def score_item(title: str, body: str, source: str) -> tuple[float, str]:
    scoring_prompt = load_scoring_prompt()
    try:
        provider = get_provider(settings.LLM_PROVIDER)
        response = await provider.create_message(
            system=scoring_prompt,
            messages=[{
                "role": "user",
                "content": f"Source: {source}\nTitle: {title}\nBody: {body[:500]}"
            }],
            model=settings.MODEL_SCORING,
            max_tokens=150,
        )
        text = response.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return float(data.get("score", 5)), data.get("reasoning", "")
    except Exception:
        pass
    return 5.0, "Scoring failed"

async def synthesize_item(title: str, body: str, source: str) -> tuple[str, str]:
    """Generate why_relevant and content_angle for high-scoring items"""
    synthesis_prompt = load_synthesis_prompt()
    try:
        provider = get_provider(settings.LLM_PROVIDER)
        response = await provider.create_message(
            system=synthesis_prompt,
            messages=[{
                "role": "user",
                "content": f"Source: {source}\nTitle: {title}\nBody: {body[:500]}"
            }],
            model=settings.MODEL_GENERATION,
            max_tokens=300,
        )
        text = response.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return data.get("why_relevant", ""), data.get("content_angle", "")
    except Exception:
        pass
    return "", ""

async def score_items_batch(items: list[dict]) -> list[dict]:
    tracer = get_tracer()
    with (tracer.start_as_current_span("score_items_batch") if tracer else _nullcontext()) as span:
        if span and tracer:
            span.set_attribute("openinference.span.kind", "CHAIN")
            span.set_attribute("input.value", f"Scoring {len(items)} items")

        scored = []
        for item in items:
            score, reasoning = await score_item(
                title=item.get("title", ""),
                body=item.get("body", ""),
                source=item.get("source", "")
            )
            item["score_relevance"] = score
            item["score_reasoning"] = reasoning
            item["score"] = score
            scored.append(item)

        if span and tracer:
            high_signal = sum(1 for i in scored if (i.get("score_relevance") or 0) >= 7)
            span.set_attribute("output.value", f"Scored {len(scored)} items, {high_signal} above threshold")

        return scored

async def synthesize_items_batch(items: list[dict]) -> list[dict]:
    """Post-scrape synthesis pass: generate why_relevant and content_angle for scored items >= 7"""
    tracer = get_tracer()
    with (tracer.start_as_current_span("synthesize_items_batch") if tracer else _nullcontext()) as span:
        if span and tracer:
            span.set_attribute("openinference.span.kind", "CHAIN")
            high_score_count = sum(1 for i in items if (i.get("score") or 0) >= 7)
            span.set_attribute("input.value", f"Synthesizing {high_score_count} high-score items")

        synthesized = []
        for item in items:
            if (item.get("score") or 0) >= 7:
                why_relevant, content_angle = await synthesize_item(
                    title=item.get("title", ""),
                    body=item.get("body", ""),
                    source=item.get("source", "")
                )
                item["why_relevant"] = why_relevant
                item["content_angle"] = content_angle
            synthesized.append(item)

        if span and tracer:
            span.set_attribute("output.value", f"Synthesized {len(synthesized)} items")

        return synthesized


from contextlib import contextmanager

@contextmanager
def _nullcontext():
    yield None

