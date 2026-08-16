from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request, Response, Query
from sqlmodel import Session, select
from database import get_session
from models import ScrapeItem, SearchInsight, KeywordCluster
from middleware.auth import get_current_user, AuthContext
from services.scraping import run_all_scrapers, DEFAULT_SUBREDDITS, GITHUB_TOPICS, ARXIV_FEEDS, DEFAULT_RSS_FEEDS
from services.scoring import score_items_batch, synthesize_items_batch
from services.seo_recommendations import (
    SeoRecommendation,
    BriefSeedPayload,
    build_actionable_recommendations,
    build_brief_seed_from_recommendation,
)
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from middleware.rate_limit import limiter, global_rate_limit_key
from config import settings
from monitoring import time_operation, trace_operation
from services.query_optimization import PaginationParams, add_pagination

class KeywordClusterInput(BaseModel):
    keyword: str
    region: str = "US"

class KeywordClusterUpdate(BaseModel):
    active: Optional[bool] = None
    keyword: Optional[str] = None

class PlanningLinkage(BaseModel):
    suggested_content_type: str
    suggested_playbook: str
    suggested_lifecycle_state: str
    owner_placeholder: str


class PlanningQueueItem(BaseModel):
    item_id: int
    title: str
    source: str
    source_url: str
    score: float
    score_signal: float
    recency_signal: float
    strategic_fit_signal: float
    rank_score: float
    strategic_fit_reasons: list[str]
    linkage: PlanningLinkage


class SeoRecommendationsResponse(BaseModel):
    recommendations: list[SeoRecommendation]
    total_count: int


def _compute_recency_signal(item: ScrapeItem, now: datetime) -> float:
    reference_time = item.published_at or item.created_at
    if reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)
    age_days = max((now - reference_time).total_seconds() / 86400.0, 0)
    return round(max(0.0, 10.0 - age_days), 3)


def _compute_strategic_fit_signal(
    item: ScrapeItem,
    keyword_terms: list[str],
    rising_topics: list[str],
) -> tuple[float, list[str]]:
    searchable_text = " ".join(
        part for part in [item.title, item.body, item.why_relevant, item.content_angle] if part
    ).lower()
    matched_keywords = sorted({term for term in keyword_terms if term and term in searchable_text})
    matched_topics = sorted({topic for topic in rising_topics if topic and topic in searchable_text})
    fit_signal = min(10.0, (len(matched_keywords) * 2.0) + (len(matched_topics) * 3.0))
    reasons = [f"keyword:{term}" for term in matched_keywords] + [f"rising_topic:{topic}" for topic in matched_topics]
    return round(fit_signal, 3), reasons


def _build_linkage(score_signal: float, strategic_fit_signal: float, source: str) -> PlanningLinkage:
    normalized_source = source.lower()
    if strategic_fit_signal >= 6.0:
        content_type = "thought_leadership"
    elif score_signal >= 8.0 or normalized_source in {"github", "arxiv"}:
        content_type = "blog"
    else:
        content_type = "newsletter"

    playbook_by_type = {
        "blog": "playbooks/blog-production.md",
        "thought_leadership": "playbooks/thought-leadership.md",
        "newsletter": "playbooks/newsletter.md",
    }

    lifecycle_state = "active" if score_signal >= 8.0 and strategic_fit_signal >= 4.0 else "draft"
    return PlanningLinkage(
        suggested_content_type=content_type,
        suggested_playbook=playbook_by_type[content_type],
        suggested_lifecycle_state=lifecycle_state,
        owner_placeholder="unassigned-content-owner",
    )


def _build_planning_queue(
    items: list[ScrapeItem],
    keyword_terms: list[str],
    rising_topics: list[str],
) -> list[PlanningQueueItem]:
    now = datetime.now(timezone.utc)
    queue: list[PlanningQueueItem] = []
    for item in items:
        if item.id is None:
            continue
        score_signal = round(item.score or 0.0, 3)
        recency_signal = _compute_recency_signal(item, now)
        strategic_fit_signal, strategic_fit_reasons = _compute_strategic_fit_signal(
            item=item,
            keyword_terms=keyword_terms,
            rising_topics=rising_topics,
        )
        rank_score = round(
            (score_signal * 0.5) + (recency_signal * 0.3) + (strategic_fit_signal * 0.2),
            3,
        )
        queue.append(
            PlanningQueueItem(
                item_id=item.id,
                title=item.title,
                source=item.source,
                source_url=item.source_url,
                score=score_signal,
                score_signal=score_signal,
                recency_signal=recency_signal,
                strategic_fit_signal=strategic_fit_signal,
                rank_score=rank_score,
                strategic_fit_reasons=strategic_fit_reasons,
                linkage=_build_linkage(score_signal, strategic_fit_signal, item.source),
            )
        )

    return sorted(queue, key=lambda q: (-q.rank_score, -q.score_signal, q.item_id))

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

@router.get("/feed")
@trace_operation("get_intelligence_feed")
def get_feed(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Get filtered intelligence feed with pagination."""
    with time_operation("db_query", attributes={"table": "scrape_item", "operation": "feed"}):
        pagination = PaginationParams(skip=skip, limit=limit)
        query = select(ScrapeItem).where(
            (ScrapeItem.dismissed_at == None) &  # noqa: E711
            (ScrapeItem.score >= 7) &
            (ScrapeItem.organization_id == auth.org_id)
        ).order_by(ScrapeItem.score.desc())
        query = add_pagination(query, pagination)
        return session.exec(query).all()

@router.get("/items")
@trace_operation("list_intelligence_items")
def list_items(
    limit: int = Query(50, ge=1, le=200),
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
):
    """List intelligence items with pagination."""
    with time_operation("db_query", attributes={"table": "scrape_item", "operation": "list"}):
        pagination = PaginationParams(skip=skip, limit=limit)
        query = select(ScrapeItem).where(
            (ScrapeItem.dismissed_at == None) &  # noqa: E711
            (ScrapeItem.organization_id == auth.org_id)
        ).order_by(ScrapeItem.created_at.desc())
        query = add_pagination(query, pagination)
        return session.exec(query).all()


@router.get("/planning/queue", response_model=list[PlanningQueueItem])
@trace_operation("get_intelligence_planning_queue")
def get_planning_queue(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
):
    """Return ranked weekly publishing queue from intelligence items."""
    with time_operation("db_query", attributes={"table": "scrape_item", "operation": "planning_queue"}):
        items = session.exec(
            select(ScrapeItem)
            .where(
                (ScrapeItem.dismissed_at == None) &  # noqa: E711
                (ScrapeItem.organization_id == auth.org_id)
            )
            .order_by(ScrapeItem.created_at.desc())
        ).all()

        keyword_terms = [
            cluster.keyword.lower().strip()
            for cluster in session.exec(
                select(KeywordCluster).where(
                    (KeywordCluster.organization_id == auth.org_id)
                    & (KeywordCluster.active == True)  # noqa: E712
                )
            ).all()
            if cluster.keyword
        ]

        rising_topics = [
            insight.topic.lower().strip()
            for insight in session.exec(
                select(SearchInsight).where(
                    (SearchInsight.organization_id == auth.org_id)
                    & (SearchInsight.trends_momentum == "rising")
                )
            ).all()
            if insight.topic
        ]

        queue = _build_planning_queue(items, keyword_terms, rising_topics)
        return queue[:limit]

@router.post("/items/{item_id}/dismiss")
@trace_operation("dismiss_item")
def dismiss_item(
    item_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    with time_operation("db_query", attributes={"table": "scrape_item", "operation": "update"}):
        item = session.exec(
            select(ScrapeItem).where(
                (ScrapeItem.id == item_id) & (ScrapeItem.organization_id == auth.org_id)
            )
        ).first()
        if item:
            if item.user_id != auth.user_id:
                raise HTTPException(status_code=403, detail="Not authorized to modify this item")
            item.dismissed_at = datetime.now(timezone.utc)
            session.add(item)
            session.commit()
        return {"ok": True}

@router.post("/items/{item_id}/use-as-context")
@trace_operation("use_item_as_context")
def use_as_context(
    item_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    with time_operation("db_query", attributes={"table": "scrape_item", "operation": "update"}):
        item = session.exec(
            select(ScrapeItem).where(
                (ScrapeItem.id == item_id) & (ScrapeItem.organization_id == auth.org_id)
            )
        ).first()
        if item:
            if item.user_id != auth.user_id:
                raise HTTPException(status_code=403, detail="Not authorized to modify this item")
            item.surfaced_to_user_at = datetime.now(timezone.utc)
            session.add(item)
            session.commit()
        return {"ok": True, "item_id": item_id}

@router.post("/scrape")
@limiter.limit(
    settings.RATE_LIMIT_EXPENSIVE_GLOBAL,
    key_func=global_rate_limit_key,
    override_defaults=False,
)
async def trigger_scrape(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    session_bind = session.bind

    async def run():
        with time_operation("celery_scrape", attributes={"type": "all_scrapers"}):
            items = await run_all_scrapers()
            scored = score_items_batch(items)
            synthesized = synthesize_items_batch(scored)
            with Session(session_bind) as s:
                from models import Organization

                default_org = s.exec(select(Organization).order_by(Organization.created_at)).first()
                for item_data in synthesized:
                    existing = s.exec(
                        select(ScrapeItem)
                        .where(ScrapeItem.organization_id == default_org.id)
                        .where(ScrapeItem.source_url == item_data.get("source_url", ""))
                    ).first()
                    if not existing and item_data.get("source_url"):
                        payload = {k: v for k, v in item_data.items() if k in ScrapeItem.__fields__}
                        payload.setdefault("organization_id", default_org.id)
                        item = ScrapeItem(**payload)
                        s.add(item)
                s.commit()

    background_tasks.add_task(run)
    return {"ok": True, "message": "Scrape started in background"}

@router.get("/config")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
def get_config(request: Request, response: Response):
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
@trace_operation("get_search_insights")
def get_search_insights(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """Get all search insights with pagination."""
    with time_operation("db_query", attributes={"table": "search_insight", "operation": "list"}):
        pagination = PaginationParams(skip=skip, limit=limit)
        query = select(SearchInsight).where(
            SearchInsight.organization_id == auth.org_id
        ).order_by(SearchInsight.generated_at.desc())
        query = add_pagination(query, pagination)
        return session.exec(query).all()


def _get_org_search_recommendations(
    session: Session,
    org_id: str,
    limit: int,
) -> list[SeoRecommendation]:
    insights = session.exec(
        select(SearchInsight)
        .where(SearchInsight.organization_id == org_id)
        .order_by(SearchInsight.generated_at.desc())
    ).all()

    active_keyword_clusters = session.exec(
        select(KeywordCluster).where(
            (KeywordCluster.organization_id == org_id)
            & (KeywordCluster.active == True)  # noqa: E712
        )
    ).all()

    return build_actionable_recommendations(
        search_insights=insights,
        keyword_clusters=active_keyword_clusters,
        limit=limit,
    )


@router.get("/search/recommendations", response_model=SeoRecommendationsResponse)
@trace_operation("get_search_recommendations")
def get_search_recommendations(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = Query(25, ge=1, le=100),
):
    """Return actionable SEO recommendations derived from insights + keyword clusters."""
    with time_operation("db_query", attributes={"table": "search_insight", "operation": "recommendations"}):
        recommendations = _get_org_search_recommendations(
            session=session,
            org_id=auth.org_id,
            limit=limit,
        )
        return SeoRecommendationsResponse(
            recommendations=recommendations,
            total_count=len(recommendations),
        )


@router.post("/search/recommendations/{recommendation_id}/brief-seed", response_model=BriefSeedPayload)
@trace_operation("seed_brief_from_search_recommendation")
def seed_brief_from_search_recommendation(
    recommendation_id: str,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a deterministic brief draft payload from a recommendation."""
    recommendations = _get_org_search_recommendations(
        session=session,
        org_id=auth.org_id,
        limit=100,
    )
    selected = next(
        (recommendation for recommendation in recommendations if recommendation.recommendation_id == recommendation_id),
        None,
    )
    if selected is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    return build_brief_seed_from_recommendation(selected)

@router.get("/search/keywords")
def get_keyword_clusters(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Get all active keyword clusters with pagination."""
    with time_operation("db_query", attributes={"table": "keyword_cluster", "operation": "list"}):
        pagination = PaginationParams(skip=skip, limit=limit)
        query = select(KeywordCluster).where(
            (KeywordCluster.active == True) &  # noqa: E712
            (KeywordCluster.organization_id == auth.org_id)
        ).order_by(KeywordCluster.created_at.desc())
        query = add_pagination(query, pagination)
        return session.exec(query).all()

@router.post("/search/keywords")
@trace_operation("add_keyword_cluster")
def add_keyword_cluster(
    data: KeywordClusterInput,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Add a new keyword cluster."""
    with time_operation("db_query", attributes={"table": "keyword_cluster", "operation": "insert"}):
        existing = session.exec(
            select(KeywordCluster)
            .where(KeywordCluster.keyword == data.keyword)
            .where(KeywordCluster.region == data.region)
            .where(KeywordCluster.organization_id == auth.org_id)
        ).first()
        if existing:
            return {"error": f"Keyword '{data.keyword}' already exists for region {data.region}"}
        
        cluster = KeywordCluster(
            keyword=data.keyword,
            region=data.region,
            organization_id=auth.org_id,
            active=True
        )
        session.add(cluster)
        session.commit()
        session.refresh(cluster)
        return cluster

@router.put("/search/keywords/{cluster_id}")
@trace_operation("update_keyword_cluster")
def update_keyword_cluster(
    cluster_id: int,
    data: KeywordClusterUpdate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a keyword cluster."""
    with time_operation("db_query", attributes={"table": "keyword_cluster", "operation": "update"}):
        cluster = session.exec(
            select(KeywordCluster).where(
                (KeywordCluster.id == cluster_id) & (KeywordCluster.organization_id == auth.org_id)
            )
        ).first()
        if not cluster:
            raise HTTPException(status_code=404, detail="Cluster not found")
        
        if data.active is not None:
            cluster.active = data.active
        if data.keyword is not None:
            cluster.keyword = data.keyword
        cluster.updated_at = datetime.now(timezone.utc)
        
        session.add(cluster)
        session.commit()
        session.refresh(cluster)
        return cluster

@router.delete("/search/keywords/{cluster_id}")
@trace_operation("delete_keyword_cluster")
def delete_keyword_cluster(
    cluster_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a keyword cluster."""
    with time_operation("db_query", attributes={"table": "keyword_cluster", "operation": "delete"}):
        cluster = session.exec(
            select(KeywordCluster).where(
                (KeywordCluster.id == cluster_id) & (KeywordCluster.organization_id == auth.org_id)
            )
        ).first()
        if not cluster:
            raise HTTPException(status_code=404, detail="Cluster not found")
        
        session.delete(cluster)
        session.commit()
        return {"ok": True}
