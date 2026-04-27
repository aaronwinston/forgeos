"""Google Trends polling service using pytrends."""

import json
import logging
from datetime import datetime
from typing import Optional
import asyncio
from sqlmodel import Session, select
from pytrends.request import TrendReq
from models import TrendsData, KeywordCluster
from database import engine

logger = logging.getLogger(__name__)

# Default keyword clusters if none configured
DEFAULT_KEYWORDS = [
    "agent observability",
    "LLM evaluation",
    "AI tracing",
    "agent harness",
    "Phoenix Arize",
    "production AI agents"
]


async def poll_trends(keywords: Optional[list[str]] = None, region: str = "US"):
    """
    Poll Google Trends for keyword clusters.
    
    Args:
        keywords: List of keywords to poll (uses defaults if None)
        region: Geographic region (default: "US")
    
    Returns:
        List of TrendsData records created/updated
    """
    if keywords is None:
        keywords = DEFAULT_KEYWORDS
    
    results = []
    pytrends = TrendReq(hl='en-US', tz=360)
    
    for keyword in keywords:
        try:
            logger.info(f"Polling trends for: {keyword}")
            
            # Fetch interest over time and related queries
            pytrends.build_payload(
                [keyword],
                timeframe='today 1-m',  # last 30 days
                geo=''  # global
            )
            
            interest_over_time = pytrends.interest_over_time()
            related_queries = pytrends.related_queries()
            
            # Convert to JSON-serializable format
            interest_json = interest_over_time.to_json() if interest_over_time is not None and len(interest_over_time) > 0 else "{}"
            related_json = json.dumps(related_queries) if related_queries else "{}"
            
            with Session(engine) as session:
                existing = session.exec(
                    select(TrendsData).where(
                        (TrendsData.keyword == keyword) &
                        (TrendsData.region == region)
                    )
                ).first()
                
                if existing:
                    existing.interest_over_time_json = interest_json
                    existing.related_queries_json = related_json
                    existing.fetched_at = datetime.utcnow()
                    session.add(existing)
                else:
                    trends_data = TrendsData(
                        keyword=keyword,
                        region=region,
                        interest_over_time_json=interest_json,
                        related_queries_json=related_json
                    )
                    session.add(trends_data)
                
                session.commit()
                results.append(keyword)
            
            # Rate limit: small delay between requests
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to poll trends for '{keyword}': {str(e)}")
            # Continue with next keyword on error
    
    logger.info(f"Trends poll complete: {len(results)} keywords processed")
    return results


async def get_configured_keywords(user_id: str = "aaron") -> list[str]:
    """Fetch configured keywords from KeywordCluster table."""
    with Session(engine) as session:
        clusters = session.exec(
            select(KeywordCluster).where(
                (KeywordCluster.user_id == user_id) &
                (KeywordCluster.active == True)
            )
        ).all()
        return [c.keyword for c in clusters] if clusters else DEFAULT_KEYWORDS
