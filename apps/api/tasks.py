"""Celery tasks for background job processing."""

from celery import Task
from celery.exceptions import SoftTimeLimitExceeded
from celery_app import celery_app
from sqlmodel import Session, select
from database import engine
from models import Organization, ScrapeItem, CalendarEvent, Session as ChatSession
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session handling."""
    
    def __call__(self, *args, **kwargs):
        with Session(engine) as session:
            self._session = session
            try:
                return super().__call__(*args, **kwargs)
            finally:
                self._session = None


def exponential_backoff(retries):
    """Calculate exponential backoff delay."""
    return 60 * (2 ** retries)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 5},
    retry_backoff=True,
    retry_backoff_max=3600,  # Max 1 hour
    retry_jitter=True,
)
def scrape_intelligence(self):
    """Scrape intelligence sources and score items."""
    try:
        from services.scraping import run_all_scrapers
        from services.scoring import score_items_batch
        
        logger.info("Starting intelligence scraping")
        
        # Run scrapers (sync wrapper for async function)
        items = asyncio.run(run_all_scrapers())
        logger.info(f"Scraped {len(items)} items")
        
        # Score items
        scored = score_items_batch(items)
        logger.info(f"Scored {len(scored)} items")
        
        # Save to database
        session = self._session
        default_org = session.exec(select(Organization).order_by(Organization.created_at)).first()
        
        if not default_org:
            logger.error("No organization found for scraping")
            return {"status": "error", "message": "No organization found"}
        
        saved_count = 0
        for item_data in scored:
            existing = session.exec(
                select(ScrapeItem)
                .where(ScrapeItem.organization_id == default_org.id)
                .where(ScrapeItem.source_url == item_data.get("source_url", ""))
            ).first()
            
            if not existing and item_data.get("source_url"):
                payload = {k: v for k, v in item_data.items() if k in ScrapeItem.__fields__}
                payload.setdefault("organization_id", default_org.id)
                item = ScrapeItem(**payload)
                session.add(item)
                saved_count += 1
        
        session.commit()
        logger.info(f"Saved {saved_count} new items")
        
        return {
            "status": "success",
            "scraped": len(items),
            "scored": len(scored),
            "saved": saved_count
        }
        
    except SoftTimeLimitExceeded:
        logger.error("Intelligence scraping exceeded time limit")
        raise
    except Exception as e:
        logger.error(f"Intelligence scraping failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def sync_calendar_events(self):
    """Poll and sync Google Calendar events."""
    try:
        from services.calendar import poll_from_google
        
        logger.info("Starting calendar sync")
        result = poll_from_google()
        
        if result.get("status") == "success":
            logger.info(f"Calendar synced: {result.get('updated_count')} updated, {result.get('archived_count')} archived")
        else:
            logger.debug(f"Calendar sync: {result.get('status')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Calendar sync failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def poll_trends(self):
    """Poll Google Trends for configured keywords."""
    try:
        from services.trends import poll_trends as do_poll_trends, get_configured_keywords
        
        logger.info("Starting trends polling")
        keywords = asyncio.run(get_configured_keywords())
        result = asyncio.run(do_poll_trends(keywords=keywords))
        
        logger.info(f"Trends poll: {len(result)} keywords processed")
        return {"status": "success", "keywords_processed": len(result)}
        
    except Exception as e:
        logger.error(f"Trends polling failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def pull_gsc_data(self):
    """Pull Google Search Console data."""
    try:
        from services.gsc import pull_gsc_data as do_pull_gsc
        
        logger.info("Starting GSC data pull")
        result = asyncio.run(do_pull_gsc())
        
        logger.info(f"GSC pull: {result.get('status')} - {result.get('rows_fetched', 0)} rows")
        return result
        
    except Exception as e:
        logger.error(f"GSC data pull failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def cross_reference_insights(self):
    """Run cross-reference LM pass for insights."""
    try:
        from services.cross_reference import cross_reference_lm_pass
        
        logger.info("Starting cross-reference pass")
        result = asyncio.run(cross_reference_lm_pass())
        
        logger.info(f"Cross-reference: {result.get('insights_created', 0)} insights created")
        return result
        
    except Exception as e:
        logger.error(f"Cross-reference failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 5},
    retry_backoff=True,
)
def send_email_digest(self):
    """Send daily email digest to organizations that have it enabled."""
    try:
        import json
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        session = self._session
        orgs = session.exec(select(Organization)).all()
        
        sent_count = 0
        for org in orgs:
            try:
                if not org.metadata_json:
                    continue
                
                settings = json.loads(org.metadata_json)
                if not settings.get("email_digest_enabled"):
                    continue
                
                # Get recent items for this org
                cutoff = datetime.utcnow() - timedelta(days=1)
                items = session.exec(
                    select(ScrapeItem)
                    .where(ScrapeItem.organization_id == org.id)
                    .where(ScrapeItem.created_at >= cutoff)
                    .order_by(ScrapeItem.score.desc())
                    .limit(10)
                ).all()
                
                if not items:
                    continue
                
                # Build email content
                html_content = f"""
                <html>
                  <body>
                    <h2>ForgeOS Daily Intelligence Digest</h2>
                    <p>Top intelligence items from the last 24 hours:</p>
                    <ul>
                """
                
                for item in items:
                    html_content += f"""
                      <li>
                        <strong>{item.title}</strong> (Score: {item.score})<br>
                        <a href="{item.source_url}">{item.source_url}</a><br>
                        {item.snippet[:200]}...
                      </li>
                    """
                
                html_content += """
                    </ul>
                  </body>
                </html>
                """
                
                # Send email (placeholder - would need actual SMTP config)
                logger.info(f"Email digest prepared for org {org.id} with {len(items)} items")
                # TODO: Implement actual email sending via SMTP or service
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send digest to org {org.id}: {str(e)}")
                continue
        
        return {"status": "success", "sent": sent_count}
        
    except Exception as e:
        logger.error(f"Email digest task failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 5},
    retry_backoff=True,
)
def send_slack_digest(self):
    """Send daily Slack digest to organizations with webhook configured."""
    try:
        import json
        import httpx
        
        session = self._session
        orgs = session.exec(select(Organization)).all()
        
        sent_count = 0
        for org in orgs:
            try:
                if not org.metadata_json:
                    continue
                
                settings = json.loads(org.metadata_json)
                webhook_url = settings.get("slack_webhook_url")
                if not webhook_url:
                    continue
                
                # Get recent high-scoring items
                cutoff = datetime.utcnow() - timedelta(days=1)
                items = session.exec(
                    select(ScrapeItem)
                    .where(ScrapeItem.organization_id == org.id)
                    .where(ScrapeItem.created_at >= cutoff)
                    .where(ScrapeItem.score >= 70)
                    .order_by(ScrapeItem.score.desc())
                    .limit(5)
                ).all()
                
                if not items:
                    continue
                
                # Build Slack message
                blocks = [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🚀 ForgeOS Intelligence Digest"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Top {len(items)} high-value items from the last 24 hours:*"
                        }
                    }
                ]
                
                for item in items:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{item.title}* (Score: {item.score})\n{item.snippet[:150]}...\n<{item.source_url}|View Source>"
                        }
                    })
                
                # Send to Slack
                response = httpx.post(
                    webhook_url,
                    json={"blocks": blocks},
                    timeout=10.0
                )
                response.raise_for_status()
                
                logger.info(f"Slack digest sent to org {org.id} with {len(items)} items")
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send Slack digest to org {org.id}: {str(e)}")
                continue
        
        return {"status": "success", "sent": sent_count}
        
    except Exception as e:
        logger.error(f"Slack digest task failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2},
    retry_backoff=True,
)
def cleanup_old_data(self):
    """Archive or delete old data to maintain database performance."""
    try:
        session = self._session
        cutoff = datetime.utcnow() - timedelta(days=90)  # 90 days retention
        
        # Delete old scrape items with low scores
        deleted_items = session.exec(
            select(ScrapeItem)
            .where(ScrapeItem.created_at < cutoff)
            .where(ScrapeItem.score < 50)
        ).all()
        
        for item in deleted_items:
            session.delete(item)
        
        session.commit()
        
        logger.info(f"Cleaned up {len(deleted_items)} old scrape items")
        return {"status": "success", "deleted_items": len(deleted_items)}
        
    except Exception as e:
        logger.error(f"Data cleanup failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2},
    retry_backoff=True,
)
def archive_completed_sessions(self):
    """Archive completed chat sessions older than 30 days."""
    try:
        session = self._session
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        # Mark old sessions as archived
        old_sessions = session.exec(
            select(ChatSession)
            .where(ChatSession.updated_at < cutoff)
        ).all()
        
        archived_count = 0
        for chat_session in old_sessions:
            if not hasattr(chat_session, 'archived'):
                continue
            chat_session.archived = True
            session.add(chat_session)
            archived_count += 1
        
        session.commit()
        
        logger.info(f"Archived {archived_count} old sessions")
        return {"status": "success", "archived": archived_count}
        
    except Exception as e:
        logger.error(f"Session archival failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    soft_time_limit=600,  # 10 minutes
)
def generate_weekly_report(self):
    """Generate weekly analytics report for all organizations."""
    try:
        session = self._session
        orgs = session.exec(select(Organization)).all()
        
        reports_generated = 0
        for org in orgs:
            try:
                # Calculate weekly stats
                week_ago = datetime.utcnow() - timedelta(days=7)
                
                items_count = session.exec(
                    select(ScrapeItem)
                    .where(ScrapeItem.organization_id == org.id)
                    .where(ScrapeItem.created_at >= week_ago)
                ).all()
                
                avg_score = sum(item.score for item in items_count) / len(items_count) if items_count else 0
                
                report_data = {
                    "week_ending": datetime.utcnow().isoformat(),
                    "items_collected": len(items_count),
                    "average_score": round(avg_score, 2),
                    "top_sources": {}  # Could add more analytics
                }
                
                logger.info(f"Generated report for org {org.id}: {report_data}")
                reports_generated += 1
                
            except Exception as e:
                logger.error(f"Failed to generate report for org {org.id}: {str(e)}")
                continue
        
        return {"status": "success", "reports": reports_generated}
        
    except Exception as e:
        logger.error(f"Weekly report generation failed: {str(e)}", exc_info=True)
        raise


# Dead Letter Queue handler
@celery_app.task(bind=True)
def handle_failed_task(self, task_id, task_name, args, kwargs, exc, traceback):
    """Handle permanently failed tasks by logging to dead letter queue."""
    logger.error(
        f"Task {task_name} [{task_id}] permanently failed after all retries",
        extra={
            "task_id": task_id,
            "task_name": task_name,
            "args": args,
            "kwargs": kwargs,
            "exception": str(exc),
            "traceback": traceback
        }
    )
    
    # Could also store in database for audit trail
    with Session(engine) as session:
        # Create a FailedTask record if model exists
        # For now, just log
        pass
    
    return {"status": "logged", "task_id": task_id}
