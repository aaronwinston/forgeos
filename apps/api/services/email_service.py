"""Email service for briefing digest delivery."""

from datetime import datetime, timedelta
from sqlmodel import Session, select
from models import ScrapeItem, Organization
from config import settings
from typing import Optional


class EmailService:
    """Simple email service using Resend API."""
    
    def __init__(self):
        self.resend_api_key = settings.RESEND_API_KEY
        self.enabled = bool(self.resend_api_key)
    
    def send_briefing_digest(self, org_id: str, recipient_email: str, session: Session) -> dict:
        """
        Send top 5 briefing items as plain HTML email.
        Returns: {"success": bool, "reason": str, "message_id": str | None}
        """
        if not self.enabled:
            return {
                "success": False,
                "reason": "resend_key_not_configured",
                "message_id": None
            }
        
        try:
            from resend import Resend
            
            # Fetch top 5 items from today
            end = datetime.utcnow()
            start = end - timedelta(hours=24)
            
            items = session.exec(
                select(ScrapeItem)
                .where(ScrapeItem.organization_id == org_id)
                .where(ScrapeItem.score >= 7)
                .where(ScrapeItem.created_at >= start)
                .where(ScrapeItem.created_at < end)
                .where(ScrapeItem.dismissed_at == None)  # noqa: E711
                .order_by(ScrapeItem.score.desc())
                .limit(5)
            ).all()
            
            if not items:
                return {
                    "success": False,
                    "reason": "no_items_for_today",
                    "message_id": None
                }
            
            # Build HTML email
            html_body = self._build_email_html(items)
            
            # Send via Resend
            client = Resend(api_key=self.resend_api_key)
            result = client.emails.send({
                "from": "ForgeOS <no-reply@forgeos.local>",
                "to": recipient_email,
                "subject": f"Your ForgeOS briefing — {datetime.now().strftime('%B %d, %Y')}",
                "html": html_body,
            })
            
            return {
                "success": True,
                "reason": "sent",
                "message_id": result.get("id") if hasattr(result, "get") else None
            }
        
        except Exception as e:
            return {
                "success": False,
                "reason": "send_error",
                "error": str(e),
                "message_id": None
            }
    
    def _build_email_html(self, items: list) -> str:
        """Build plain HTML email from briefing items."""
        items_html = "".join([
            f"""
            <div style="margin: 16px 0; padding: 12px; border: 1px solid #ddd; border-radius: 4px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 18px;">{self._get_icon(item.source)}</span>
                    <strong style="font-size: 12px; background: {self._get_color(item.source)}; color: white; padding: 2px 6px; border-radius: 3px;">
                        {item.source.upper()}
                    </strong>
                    {f'<span style="font-size: 12px; color: #f59e0b; font-weight: bold;">↑ Trending</span>' if item.score >= 8.5 else ''}
                </div>
                <h3 style="margin: 8px 0; font-size: 14px; line-height: 1.4;">
                    <a href="{item.source_url}" style="color: #0066cc; text-decoration: none;">
                        {item.title}
                    </a>
                </h3>
                <p style="margin: 8px 0; font-size: 12px; color: #666; line-height: 1.4;">
                    {item.why_relevant}
                </p>
                <p style="margin: 8px 0; font-size: 11px; color: #999;">
                    <strong>Content angle:</strong> {item.content_angle}
                </p>
            </div>
            """
            for item in items
        ])
        
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.5; color: #333; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="font-size: 20px; margin: 0 0 16px 0; color: #000;">Your ForgeOS briefing</h1>
                <p style="font-size: 14px; color: #666; margin: 0 0 24px 0;">
                    Top 5 items from today, ranked by relevance to your work.
                </p>
                
                {items_html}
                
                <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #eee; font-size: 12px; color: #999;">
                    <p style="margin: 0;">
                        Sent by ForgeOS at 7:00 AM daily. 
                        <a href="http://localhost:3000/dashboard" style="color: #0066cc; text-decoration: none;">View full briefing</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _get_icon(self, source: str) -> str:
        """Get emoji icon for source."""
        icons = {
            "hackernews": "🔶",
            "github": "🐙",
            "arxiv": "📄",
            "reddit": "🔴",
            "rss": "📰",
        }
        return icons.get(source.lower(), "📰")
    
    def _get_color(self, source: str) -> str:
        """Get brand color for source badge."""
        colors = {
            "hackernews": "#FF6600",
            "github": "#24292e",
            "arxiv": "#B31B1B",
            "reddit": "#FF4500",
            "rss": "#F26522",
        }
        return colors.get(source.lower(), "#999")
