import anthropic
import json
import re
from config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
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

def score_item(title: str, body: str, source: str) -> tuple[float, str]:
    scoring_prompt = load_scoring_prompt()
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=150,
            system=scoring_prompt,
            messages=[{
                "role": "user",
                "content": f"Source: {source}\nTitle: {title}\nBody: {body[:500]}"
            }]
        )
        text = response.content[0].text.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return float(data.get("score", 5)), data.get("reasoning", "")
    except Exception:
        pass
    return 5.0, "Scoring failed"

def score_items_batch(items: list[dict]) -> list[dict]:
    scored = []
    for item in items:
        score, reasoning = score_item(
            title=item.get("title", ""),
            body=item.get("body", ""),
            source=item.get("source", "")
        )
        item["score_relevance"] = score
        item["score_reasoning"] = reasoning
        scored.append(item)
    return scored
