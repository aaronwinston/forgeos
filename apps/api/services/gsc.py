"""Google Search Console integration service."""

import logging
from datetime import datetime, timedelta
from typing import Optional
import json
from sqlmodel import Session, select
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from models import GscQuery, CalendarIntegration
from database import engine
from config import settings

logger = logging.getLogger(__name__)

GSC_SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']


class GSCService:
    """Google Search Console API client with automatic token refresh."""
    
    def __init__(self, access_token: str, refresh_token: str, gsc_property: str):
        """
        Initialize GSC service with token refresh capability.
        
        Args:
            access_token: OAuth 2.0 access token
            refresh_token: OAuth 2.0 refresh token (for expired token handling)
            gsc_property: GSC property URL (e.g., "sc-domain:example.com" or "https://example.com/")
        """
        self.gsc_property = gsc_property
        self.refresh_token = refresh_token
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
        )
        # Refresh credentials if expired
        if self.credentials.expired and self.refresh_token:
            request = Request()
            self.credentials.refresh(request)
            logger.info("GSC credentials refreshed")
        
        self.service = build('webmasters', 'v3', credentials=self.credentials)
    
    def get_performance_data(self, days_back: int = 28) -> list[dict]:
        """
        Fetch performance data from GSC for the last N days.
        
        Args:
            days_back: Number of days to fetch (default 28 for free tier)
        
        Returns:
            List of performance rows with query, page, clicks, impressions, ctr, position
        """
        try:
            # Refresh if needed before request
            if self.credentials.expired and self.refresh_token:
                request = Request()
                self.credentials.refresh(request)
            
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days_back)
            
            request_body = {
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat(),
                'dimensions': ['query', 'page'],
                'rowLimit': 25000,  # GSC max per request
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=self.gsc_property,
                body=request_body
            ).execute()
            
            rows = response.get('rows', [])
            logger.info(f"Fetched {len(rows)} GSC rows for {self.gsc_property}")
            
            results = []
            for row in rows:
                results.append({
                    'query': row['keys'][0],
                    'page': row['keys'][1],
                    'clicks': int(row.get('clicks', 0)),
                    'impressions': int(row.get('impressions', 0)),
                    'ctr': float(row.get('ctr', 0)),
                    'position': float(row.get('position', 0)),
                    'date_range_start': start_date.isoformat(),
                    'date_range_end': end_date.isoformat(),
                })
            
            return results
            
        except Exception as e:
            logger.error(f"GSC API error for {self.gsc_property}: {str(e)}")
            return []


async def pull_gsc_data(user_id: str = "aaron", gsc_property: Optional[str] = None) -> dict:
    """
    Pull GSC data and store in database.
    
    Looks up user's OAuth token from CalendarIntegration (reuses OAuth).
    Uses stored GSC property from calendar_id field, or override via parameter.
    
    Returns:
        Status dict with rows_fetched count
    """
    with Session(engine) as session:
        # Get OAuth token (from calendar integration as a stand-in for Google OAuth)
        oauth = session.exec(
            select(CalendarIntegration).where(
                CalendarIntegration.user_id == user_id
            )
        ).first()
        
        if not oauth:
            logger.warning(f"No OAuth token found for user {user_id}; skipping GSC pull")
            return {"status": "skipped", "reason": "No OAuth token"}
        
        access_token = oauth.access_token
        refresh_token = oauth.refresh_token
        
        if not access_token or not refresh_token:
            logger.warning(f"OAuth token incomplete for user {user_id} (missing access or refresh token)")
            return {"status": "skipped", "reason": "Token incomplete"}
    
    try:
        # Use stored GSC property or parameter, or default
        # NOTE: calendar_id field stores GSC property URL when GSC is selected
        property_url = gsc_property or oauth.calendar_id or "sc-domain:arize.com"
        
        logger.info(f"Pulling GSC data for property: {property_url}")
        gsc = GSCService(access_token, refresh_token, property_url)
        rows = gsc.get_performance_data(days_back=28)
        
        if not rows:
            logger.warning(f"No GSC data returned for {property_url}")
            return {"status": "success", "rows_fetched": 0}
        
        # Store in database
        with Session(engine) as session:
            for row_data in rows:
                # Upsert: update if query+page+date combo exists, else insert
                existing = session.exec(
                    select(GscQuery).where(
                        (GscQuery.user_id == user_id) &
                        (GscQuery.query == row_data['query']) &
                        (GscQuery.page == row_data['page']) &
                        (GscQuery.date_range_start == row_data['date_range_start'])
                    )
                ).first()
                
                row_data['user_id'] = user_id
                if existing:
                    # Update existing row
                    for key, value in row_data.items():
                        if key != 'user_id':  # Don't overwrite user_id
                            setattr(existing, key, value)
                    session.add(existing)
                else:
                    # Insert new row
                    gsc_query = GscQuery(**row_data)
                    session.add(gsc_query)
            
            session.commit()
        
        return {"status": "success", "rows_fetched": len(rows)}
        
    except Exception as e:
        logger.error(f"GSC pull failed: {str(e)}")
        return {"status": "error", "error": str(e)}
