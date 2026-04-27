"""Cross-reference LLM pass: extract keywords from top scrape items and join with GSC/Trends data."""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select
from anthropic import Anthropic
from models import ScrapeItem, GscQuery, TrendsData, SearchInsight
from database import engine
from config import settings

logger = logging.getLogger(__name__)

client = Anthropic()


async def cross_reference_lm_pass(user_id: str = "aaron") -> dict:
    """
    Daily job (runs after morning scrape):
    1. Pull top 30 ScrapeItem rows from last 24h (scored >= 7)
    2. For each, extract 1-3 keyword phrases via Claude
    3. Join against GSC data: "do we rank for this? what position?"
    4. Join against Trends: "is interest rising/steady/falling?"
    5. Produce search_insight row per opportunity
    
    Returns:
        Status dict with insights_created count
    """
    try:
        with Session(engine) as session:
            # Step 1: Get top 30 scored items from last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            top_items = session.exec(
                select(ScrapeItem)
                .where(
                    (ScrapeItem.score >= 7) &
                    (ScrapeItem.fetched_at >= cutoff_time)
                )
                .order_by(ScrapeItem.score.desc())
                .limit(30)
            ).all()
            
            if not top_items:
                logger.info("No high-scored items in last 24h for cross-reference pass")
                return {"status": "success", "insights_created": 0}
            
            logger.info(f"Cross-referencing {len(top_items)} high-scored items")
            
            insights_created = 0
            errors = []
            
            # Step 2-5: Process each item
            for item in top_items:
                try:
                    # Extract keywords via Claude
                    keywords = _extract_keywords(item)
                    if not keywords:
                        continue
                    
                    # For each keyword, check GSC and Trends data
                    for keyword in keywords:
                        try:
                            insight = _build_insight(
                                item=item,
                                keyword=keyword,
                                session=session,
                                user_id=user_id
                            )
                            
                            if insight:
                                session.add(insight)
                                insights_created += 1
                        except Exception as keyword_err:
                            logger.warning(f"Failed to build insight for item {item.id}, keyword '{keyword}': {str(keyword_err)}")
                            errors.append((item.id, keyword, str(keyword_err)))
                    
                except Exception as e:
                    logger.error(f"Failed to process item {item.id}: {str(e)}", exc_info=True)
                    errors.append((item.id, None, str(e)))
                    continue
            
            session.commit()
            logger.info(f"Cross-reference pass complete: {insights_created} insights created, {len(errors)} errors")
            if errors:
                logger.warning(f"Cross-reference errors: {errors}")
            return {"status": "success", "insights_created": insights_created, "errors": len(errors)}
            
    except Exception as e:
        logger.error(f"Cross-reference pass failed: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}


def _extract_keywords(item: ScrapeItem) -> list[str]:
    """
    Use Claude to extract 1-3 keyword phrases from item title/body.
    """
    try:
        text = f"{item.title}\n\n{item.body[:500] if item.body else ''}"
        
        response = client.messages.create(
            model=settings.MODEL_GENERATION,
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f"""Extract 1-3 key search phrases from this content that could be used in Google Search or Trends queries. 
Return as a JSON array of strings, e.g. ["phrase1", "phrase2"]. 
Be concise and specific. Phrases should be 2-5 words.

Content:
{text}"""
                }
            ]
        )
        
        result_text = response.content[0].text
        # Parse JSON from response
        import re
        match = re.search(r'\[.*?\]', result_text, re.DOTALL)
        if match:
            keywords = json.loads(match.group())
            return keywords[:3]  # Max 3
    except Exception as e:
        logger.warning(f"Keyword extraction failed: {str(e)}")
    
    return []


def _build_insight(item: ScrapeItem, keyword: str, session: Session, user_id: str) -> Optional[SearchInsight]:
    """
    Build a SearchInsight by joining GSC and Trends data.
    """
    try:
        # Check GSC: do we rank for this keyword?
        gsc_row = session.exec(
            select(GscQuery)
            .where(
                (GscQuery.user_id == user_id) &
                (GscQuery.query.ilike(f"%{keyword}%"))
            )
            .order_by(GscQuery.position)
            .limit(1)
        ).first()
        
        our_position = gsc_row.position if gsc_row else None
        our_clicks = gsc_row.clicks if gsc_row else None
        
        # Check Trends: is interest rising/falling?
        trends_row = session.exec(
            select(TrendsData)
            .where(
                (TrendsData.user_id == user_id) &
                (TrendsData.keyword.ilike(keyword))
            )
            .order_by(TrendsData.fetched_at.desc())
            .limit(1)
        ).first()
        
        trends_momentum = _assess_trends_momentum(trends_row) if trends_row else "no_data"
        
        # Build insight text
        insight_text = _build_insight_text(
            item=item,
            keyword=keyword,
            our_position=our_position,
            our_clicks=our_clicks,
            trends_momentum=trends_momentum
        )
        
        # Create SearchInsight row
        insight = SearchInsight(
            user_id=user_id,
            topic=keyword,
            source_item_ids=str(item.id),
            our_gsc_position=our_position,
            our_gsc_clicks=our_clicks,
            trends_momentum=trends_momentum,
            insight_text=insight_text
        )
        
        return insight
        
    except Exception as e:
        logger.warning(f"Failed to build insight for {keyword}: {str(e)}")
        return None


def _assess_trends_momentum(trends_row: TrendsData) -> str:
    """
    Assess if trends data shows rising/steady/falling interest.
    Handles pytrends JSON format: {"keyword": {timestamp: value, ...}, "isPartial": {...}}
    """
    try:
        if not trends_row or not trends_row.interest_over_time_json:
            return "no_data"
        
        data = json.loads(trends_row.interest_over_time_json)
        if not data:
            return "no_data"
        
        # pytrends returns {keyword: {timestamp: value}, "isPartial": {...}}
        # Extract the keyword's data (first key that's not "isPartial")
        values = None
        for key, val in data.items():
            if key != "isPartial" and isinstance(val, dict):
                values = list(val.values())
                break
        
        if not values or len(values) < 2:
            return "steady"
        
        # Simple heuristic: compare last 1/3 to first 1/3 of data
        # Convert to float in case they're integers
        values = [float(v) for v in values if isinstance(v, (int, float))]
        if len(values) < 2:
            return "steady"
        
        third_size = max(1, len(values) // 3)
        first_third = sum(values[:third_size]) / third_size
        last_third = sum(values[-third_size:]) / third_size
        
        # Assess momentum
        if last_third > first_third * 1.1:
            return "rising"
        elif last_third < first_third * 0.9:
            return "falling"
        else:
            return "steady"
    except Exception as e:
        logger.warning(f"Trends momentum assessment failed: {str(e)}")
        return "no_data"


def _build_insight_text(
    item: ScrapeItem,
    keyword: str,
    our_position: Optional[float],
    our_clicks: Optional[int],
    trends_momentum: str
) -> str:
    """Generate natural language insight text."""
    parts = []
    
    parts.append(f"Content about '{keyword}' from {item.source}.")
    
    if our_position:
        parts.append(f"We rank at position {int(our_position)} for related queries.")
        if our_clicks:
            parts.append(f"Getting ~{our_clicks} clicks/month.")
    else:
        parts.append(f"We don't currently rank for this keyword.")
    
    if trends_momentum == "rising":
        parts.append(f"Interest in '{keyword}' is rising.")
    elif trends_momentum == "falling":
        parts.append(f"Interest in '{keyword}' is declining.")
    elif trends_momentum == "steady":
        parts.append(f"Interest in '{keyword}' is stable.")
    
    return " ".join(parts)
