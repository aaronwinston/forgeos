import time
from fastapi import APIRouter, Depends, Query
from cache import briefing_cache
from database import get_session
from models import ScrapeItem
from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/api/briefing", tags=["briefing"])

SOURCE_COLORS = {
    "hackernews": "#FF6600",
    "github": "#24292e",
    "arxiv": "#B31B1B",
    "reddit": "#FF4500",
    "rss": "#F26522",
}
SOURCE_ICONS = {
    "hackernews": "🔶",
    "github": "🐙",
    "arxiv": "📄",
    "reddit": "🔴",
    "rss": "📰",
}

def format_scrape_item_for_response(item: ScrapeItem, idx: int) -> dict:
    """Convert ScrapeItem DB row to Story response format"""
    source_key = (item.source or "").lower()
    return {
        "id": str(item.id),
        "title": item.title,
        "source": item.source,
        "sourceColor": SOURCE_COLORS.get(source_key, "#666"),
        "icon": SOURCE_ICONS.get(source_key, "📰"),
        "why_relevant": item.why_relevant or "",
        "engagement_signal": item.score_reasoning or "",
        "content_angle": item.content_angle or "",
        "url": item.source_url,
        "trending": idx < 3,
    }

def _query_items(db: Session, date: Optional[str] = None):
    """Return scored ScrapeItem rows for a calendar date (default: today)."""
    if date:
        try:
            target = datetime.strptime(date, "%Y-%m-%d")
            start = target.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        except ValueError:
            # Fallback to last 24h on bad date
            end = datetime.utcnow()
            start = end - timedelta(hours=24)
    else:
        end = datetime.utcnow()
        start = end - timedelta(hours=24)

    return db.exec(
        select(ScrapeItem)
        .where(ScrapeItem.score >= 7)
        .where(ScrapeItem.created_at >= start)
        .where(ScrapeItem.created_at < end)
        .where(ScrapeItem.dismissed_at == None)  # noqa: E711
        .order_by(ScrapeItem.score.desc())
        .order_by(ScrapeItem.created_at.desc())
        .limit(8)
    ).all()

@router.get("")
async def get_briefing(
    date: Optional[str] = Query(None, description="Calendar date YYYY-MM-DD; defaults to today"),
    session: Session = Depends(get_session),
):
    """Return top-scored ScrapeItem rows. Pass ?date=YYYY-MM-DD for a specific day."""
    cache_key = f"briefing:{date or 'today'}"
    cached = briefing_cache.get(cache_key)
    if cached:
        return cached

    try:
        items = _query_items(session, date)
        stories = [format_scrape_item_for_response(item, idx) for idx, item in enumerate(items)]
        result = {"stories": stories, "refreshed_at": time.time()}
        briefing_cache.set(cache_key, result, ttl_seconds=1800)
        return result
    except Exception as e:
        return {"stories": [], "error": str(e), "refreshed_at": None}

@router.post("/refresh")
async def refresh_briefing(session: Session = Depends(get_session)):
    """Invalidate cache and re-query today's ScrapeItems."""
    briefing_cache.clear("briefing:today")
    try:
        items = _query_items(session, date=None)
        stories = [format_scrape_item_for_response(item, idx) for idx, item in enumerate(items)]
        result = {"stories": stories, "refreshed_at": time.time()}
        briefing_cache.set("briefing:today", result, ttl_seconds=1800)
        return result
    except Exception as e:
        return {"stories": [], "error": str(e), "refreshed_at": None}

