from fastapi import APIRouter, Depends, BackgroundTasks
from sqlmodel import Session, select
from database import get_session
from models import ScrapeItem
from services.scraping import run_all_scrapers, DEFAULT_SUBREDDITS, GITHUB_TOPICS, ARXIV_FEEDS, DEFAULT_RSS_FEEDS
from services.scoring import score_items_batch
from datetime import datetime

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

@router.get("/feed")
def get_feed(session: Session = Depends(get_session)):
    items = session.exec(
        select(ScrapeItem)
        .where(ScrapeItem.dismissed_at == None)  # noqa: E711
        .where(ScrapeItem.score_relevance >= 7)
        .order_by(ScrapeItem.score_relevance.desc())
    ).all()
    return items

@router.get("/items")
def list_items(limit: int = 50, session: Session = Depends(get_session)):
    items = session.exec(
        select(ScrapeItem)
        .where(ScrapeItem.dismissed_at == None)  # noqa: E711
        .order_by(ScrapeItem.fetched_at.desc())
        .limit(limit)
    ).all()
    return items

@router.post("/items/{item_id}/dismiss")
def dismiss_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(ScrapeItem, item_id)
    if item:
        item.dismissed_at = datetime.utcnow()
        session.add(item)
        session.commit()
    return {"ok": True}

@router.post("/items/{item_id}/use-as-context")
def use_as_context(item_id: int, session: Session = Depends(get_session)):
    item = session.get(ScrapeItem, item_id)
    if item:
        item.surfaced_to_user_at = datetime.utcnow()
        session.add(item)
        session.commit()
    return {"ok": True, "item_id": item_id}

@router.post("/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    session_bind = session.bind

    async def run():
        items = await run_all_scrapers()
        scored = score_items_batch(items)
        with Session(session_bind) as s:
            for item_data in scored:
                existing = s.exec(
                    select(ScrapeItem).where(ScrapeItem.source_url == item_data.get("source_url", ""))
                ).first()
                if not existing and item_data.get("source_url"):
                    item = ScrapeItem(**{
                        k: v for k, v in item_data.items()
                        if k in ScrapeItem.__fields__
                    })
                    s.add(item)
            s.commit()

    background_tasks.add_task(run)
    return {"ok": True, "message": "Scrape started in background"}

@router.get("/config")
def get_config():
    return {
        "hn_keywords": ["LLM observability", "AI agents", "eval harness", "arize", "phoenix"],
        "hn_min_points": 50,
        "subreddits": ["MachineLearning", "LocalLLaMA", "programming", "LangChain", "AI_Agents"],
        "github_topics": ["ai", "llm", "agents", "observability", "llm-evaluation"],
        "rss_feeds": [
            "https://www.anthropic.com/rss.xml",
            "https://simonwillison.net/atom/everything/",
            "https://www.latent.space/feed",
            "https://arize.com/blog/feed/",
        ],
    }
