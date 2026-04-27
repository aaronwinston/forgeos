from fastapi import APIRouter, Depends, BackgroundTasks
from sqlmodel import Session, select
from database import get_session
from models import ScrapeItem, SearchInsight, KeywordCluster
from services.scraping import run_all_scrapers, DEFAULT_SUBREDDITS, GITHUB_TOPICS, ARXIV_FEEDS, DEFAULT_RSS_FEEDS
from services.scoring import score_items_batch, synthesize_items_batch
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

@router.get("/feed")
def get_feed(session: Session = Depends(get_session)):
    items = session.exec(
        select(ScrapeItem)
        .where(ScrapeItem.dismissed_at == None)  # noqa: E711
        .where(ScrapeItem.score >= 7)
        .order_by(ScrapeItem.score.desc())
    ).all()
    return items

@router.get("/items")
def list_items(limit: int = 50, session: Session = Depends(get_session)):
    items = session.exec(
        select(ScrapeItem)
        .where(ScrapeItem.dismissed_at == None)  # noqa: E711
        .order_by(ScrapeItem.created_at.desc())
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
        synthesized = synthesize_items_batch(scored)
        with Session(session_bind) as s:
            for item_data in synthesized:
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

@router.get("/search/insights")
def get_search_insights(session: Session = Depends(get_session)):
    """Get all search insights."""
    insights = session.exec(
        select(SearchInsight)
        .order_by(SearchInsight.generated_at.desc())
        .limit(100)
    ).all()
    return insights

@router.get("/search/keywords")
def get_keyword_clusters(session: Session = Depends(get_session)):
    """Get all active keyword clusters."""
    clusters = session.exec(
        select(KeywordCluster)
        .where(KeywordCluster.active == True)  # noqa: E712
        .order_by(KeywordCluster.created_at.desc())
    ).all()
    return clusters

@router.post("/search/keywords")
def add_keyword_cluster(keyword: str, region: str = "US", session: Session = Depends(get_session)):
    """Add a new keyword cluster."""
    existing = session.exec(
        select(KeywordCluster)
        .where(KeywordCluster.keyword == keyword)
        .where(KeywordCluster.region == region)
    ).first()
    if existing:
        return {"error": f"Keyword '{keyword}' already exists for region {region}"}
    
    cluster = KeywordCluster(keyword=keyword, region=region, active=True)
    session.add(cluster)
    session.commit()
    session.refresh(cluster)
    return cluster

@router.put("/search/keywords/{cluster_id}")
def update_keyword_cluster(cluster_id: int, active: Optional[bool] = None, keyword: Optional[str] = None, session: Session = Depends(get_session)):
    """Update a keyword cluster."""
    cluster = session.get(KeywordCluster, cluster_id)
    if not cluster:
        return {"error": f"Cluster {cluster_id} not found"}
    
    if active is not None:
        cluster.active = active
    if keyword is not None:
        cluster.keyword = keyword
    cluster.updated_at = datetime.utcnow()
    
    session.add(cluster)
    session.commit()
    session.refresh(cluster)
    return cluster

@router.delete("/search/keywords/{cluster_id}")
def delete_keyword_cluster(cluster_id: int, session: Session = Depends(get_session)):
    """Delete a keyword cluster."""
    cluster = session.get(KeywordCluster, cluster_id)
    if not cluster:
        return {"error": f"Cluster {cluster_id} not found"}
    
    session.delete(cluster)
    session.commit()
    return {"ok": True}

