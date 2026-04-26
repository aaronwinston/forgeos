import asyncio
import re
import json
import time
from fastapi import APIRouter, Depends
import httpx
import feedparser
from bs4 import BeautifulSoup
from anthropic import Anthropic
from cache import briefing_cache
from config import settings
from database import get_session
from models import ScrapeItem
from sqlmodel import Session, select
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/briefing", tags=["briefing"])
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

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

@router.get("")
async def get_briefing(session: Session = Depends(get_session)):
    """Read from scored ScrapeItem rows (score >= 7, last 24h) instead of running ad-hoc scrapers"""
    cached = briefing_cache.get("briefing")
    if cached:
        return cached
    
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        items = session.exec(
            select(ScrapeItem)
            .where(ScrapeItem.score >= 7)
            .where(ScrapeItem.created_at >= cutoff_time)
            .where(ScrapeItem.dismissed_at == None)  # noqa: E711
            .order_by(ScrapeItem.score.desc())
            .order_by(ScrapeItem.created_at.desc())
        ).all()
        
        stories = [format_scrape_item_for_response(item, idx) for idx, item in enumerate(items)]
        result = {"stories": stories, "refreshed_at": time.time()}
        briefing_cache.set("briefing", result, ttl_seconds=1800)
        return result
    except Exception as e:
        return {"stories": [], "error": str(e), "refreshed_at": None}

@router.post("/refresh")
async def refresh_briefing(session: Session = Depends(get_session)):
    """Refresh briefing cache by re-querying ScrapeItem"""
    briefing_cache.clear("briefing")
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        items = session.exec(
            select(ScrapeItem)
            .where(ScrapeItem.score >= 7)
            .where(ScrapeItem.created_at >= cutoff_time)
            .where(ScrapeItem.dismissed_at == None)  # noqa: E711
            .order_by(ScrapeItem.score.desc())
            .order_by(ScrapeItem.created_at.desc())
        ).all()
        
        stories = [format_scrape_item_for_response(item, idx) for idx, item in enumerate(items)]
        result = {"stories": stories, "refreshed_at": time.time()}
        briefing_cache.set("briefing", result, ttl_seconds=1800)
        return result
    except Exception as e:
        return {"stories": [], "error": str(e), "refreshed_at": None}

