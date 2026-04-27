# instrumentation must be imported and called before any Anthropic clients are created
import instrumentation
instrumentation.setup_tracing()

from logging_config import configure_logging

configure_logging()

# Setup Sentry error tracking (P4.2) before importing routers
def setup_sentry():
    """Initialize Sentry error tracking and performance monitoring."""
    from config import settings
    
    if not settings.SENTRY_DSN:
        return None
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                CeleryIntegration(),
            ],
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=settings.SENTRY_PROFILE_SAMPLE_RATE,
            attach_stacktrace=True,
        )
        
        import logging
        logging.getLogger(__name__).info(
            f"Sentry initialized — environment: {settings.SENTRY_ENVIRONMENT}, "
            f"traces sampling: {settings.SENTRY_TRACES_SAMPLE_RATE * 100:.0f}%"
        )
        return sentry_sdk
    
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Sentry setup failed (non-fatal): {e}")
        return None

setup_sentry()

# Register audit listeners (SQLAlchemy session hooks)
import audit as audit_trail  # noqa: F401

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import create_db_and_tables, get_session
from middleware.request_logging import RequestLoggingMiddleware
from middleware.csrf import CSRFMiddleware
from personal_mode import is_personal
from services.briefing_aggregation import run_weekly_aggregation
from middleware.request_logging import RequestLoggingMiddleware
from middleware.csrf import CSRFMiddleware
from personal_mode import is_personal
from routers import (
    projects,
    chat,
    intelligence,
    settings as settings_router,
    files,
    sessions,
    briefing,
    integrations,
    calendar,
    search,
    orgs,
    runtimes,
    billing,
    usage,
    onboarding,
    doctrine,
    mission_control,
    skills,
    trust,
    auth,
    audit as audit_router,
    jobs,
    benchmark,
)
from config import settings
from middleware.rate_limit import limiter, setup_rate_limiting

def is_personal_mode() -> bool:
    """Check if running in personal mode."""
    from personal_mode import is_personal
    return is_personal()

app = FastAPI(title="ForgeOS API", version="1.0.0")

setup_rate_limiting(app)

# Request/response logging (method, path, status, latency, sizes, auth context)
# This is always useful, even in personal mode
app.add_middleware(RequestLoggingMiddleware)

# In multi-tenant mode, add CSRF and rate limiting
if not is_personal_mode():
    # CSRF protection middleware (before CORS to validate before cross-origin handling)
    app.add_middleware(CSRFMiddleware)
    
    # Apply rate limiting in multi-tenant mode
    settings.RATE_LIMIT_ENABLED = True
else:
    # In personal mode, disable rate limiting
    settings.RATE_LIMIT_ENABLED = False


# Parse CORS allowed origins from comma-separated env var
allowed_origins = [origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

# Add CORS after rate limiting so CORS headers are present even on 429 responses.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(chat.router)
app.include_router(intelligence.router)
app.include_router(settings_router.router)
app.include_router(files.router)
app.include_router(sessions.router)
app.include_router(briefing.router)
app.include_router(integrations.router)
app.include_router(calendar.router)
app.include_router(search.router)
app.include_router(orgs.router)
app.include_router(runtimes.router)
app.include_router(billing.router)
app.include_router(usage.router)
app.include_router(onboarding.router)
app.include_router(doctrine.router)
app.include_router(mission_control.router)
app.include_router(skills.router)
app.include_router(trust.router)
app.include_router(audit_router.router)
app.include_router(jobs.router)
app.include_router(benchmark.router)

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup():
    create_db_and_tables()

    from services.scraping import run_all_scrapers
    from services.scoring import score_items_batch
    from services.calendar import poll_from_google
    from services.trends import poll_trends, get_configured_keywords
    from services.gsc import pull_gsc_data
    from services.cross_reference import cross_reference_lm_pass
    from models import ScrapeItem
    from sqlmodel import Session, select
    from database import engine
    import logging

    logger = logging.getLogger(__name__)

    async def scheduled_scrape():
        items = await run_all_scrapers()
        scored = score_items_batch(items)
        with Session(engine) as session:
            from models import Organization

            default_org = session.exec(select(Organization).order_by(Organization.created_at)).first()
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
            session.commit()

    def scheduled_calendar_poll():
        try:
            result = poll_from_google()
            if result.get("status") == "success":
                logger.info(f"Calendar poll: {result.get('updated_count')} updated, {result.get('archived_count')} archived")
            else:
                logger.debug(f"Calendar poll: {result.get('status')}")
        except Exception as e:
            logger.error(f"Calendar poll failed: {str(e)}")

    async def scheduled_trends_poll():
        try:
            keywords = await get_configured_keywords()
            result = await poll_trends(keywords=keywords)
            logger.info(f"Trends poll: {len(result)} keywords processed")
        except Exception as e:
            logger.error(f"Trends poll failed: {str(e)}")

    async def scheduled_gsc_pull():
        try:
            result = await pull_gsc_data()
            logger.info(f"GSC pull: {result.get('status')} - {result.get('rows_fetched', 0)} rows")
        except Exception as e:
            logger.error(f"GSC pull failed: {str(e)}")

    async def scheduled_cross_reference():
        try:
            result = await cross_reference_lm_pass()
            logger.info(f"Cross-reference pass: {result.get('insights_created', 0)} insights created")
        except Exception as e:
            logger.error(f"Cross-reference pass failed: {str(e)}")

    async def scheduled_briefing_aggregation():
        """Weekly aggregation of briefing feedback and scoring prompt calibration."""
        try:
            from sqlalchemy import create_engine
            from sqlmodel import Session as SQLSession
            
            # Get database URL
            engine = create_engine(settings.DATABASE_URL)
            with SQLSession(engine) as session:
                result = run_weekly_aggregation(session)
                logger.info(f"Briefing aggregation: {result.get('status')} - {result.get('thumbs_up', 0)} 👍, {result.get('thumbs_down', 0)} 👎")
        except Exception as e:
            logger.error(f"Briefing aggregation failed: {str(e)}")
    
    async def scheduled_briefing_email():
        """Daily 7am email digest of top briefing items."""
        try:
            if not settings.RESEND_API_KEY:
                logger.debug("Briefing email: Resend API key not configured, skipping")
                return
            
            from sqlalchemy import create_engine
            from sqlmodel import Session as SQLSession
            from services.email_service import EmailService
            
            # In personal mode, send to hardcoded aaron email
            if is_personal():
                recipient = "aaron@forgeos.local"
                org_id = "personal"
            else:
                # In multi-tenant, would need to iterate over orgs with email settings
                logger.debug("Briefing email: Skipping in multi-tenant mode (not yet implemented)")
                return
            
            engine = create_engine(settings.DATABASE_URL)
            with SQLSession(engine) as session:
                email_service = EmailService()
                result = email_service.send_briefing_digest(org_id, recipient, session)
                if result["success"]:
                    logger.info(f"Briefing email sent to {recipient}")
                else:
                    logger.debug(f"Briefing email skipped: {result['reason']}")
        except Exception as e:
            logger.error(f"Briefing email failed: {str(e)}")

    scheduler.add_job(scheduled_scrape, 'cron', hour=8, minute=0, id='scrape_morning', replace_existing=True)
    scheduler.add_job(scheduled_scrape, 'cron', hour=18, minute=0, id='scrape_evening', replace_existing=True)
    scheduler.add_job(scheduled_calendar_poll, 'interval', minutes=5, id='calendar_poll', replace_existing=True)
    scheduler.add_job(scheduled_trends_poll, 'cron', hour=9, minute=0, id='trends_poll', replace_existing=True)  # Daily at 9 AM
    scheduler.add_job(scheduled_gsc_pull, 'cron', hour=9, minute=15, id='gsc_pull', replace_existing=True)  # 15 min after trends
    scheduler.add_job(scheduled_cross_reference, 'cron', hour=9, minute=30, id='cross_ref_pass', replace_existing=True)  # 30 min after trends
    scheduler.add_job(scheduled_briefing_aggregation, 'cron', day_of_week='6', hour=23, minute=59, id='briefing_aggregation', replace_existing=True)  # Sunday 23:59
    scheduler.add_job(scheduled_briefing_email, 'cron', hour=7, minute=0, id='briefing_email', replace_existing=True)  # Daily at 7 AM
    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()

@app.get("/api/health")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
def health(request: Request, response: Response):
    """
    Health check endpoint with database and service connectivity checks.
    Provides observability into system state for monitoring/alerting.
    """
    from database import get_session
    
    health_status = {
        "status": "ok",
        "version": "1.0.0",
        "checks": {
            "database": "unknown",
            "redis": "unknown",
        }
    }
    
    # Check database connectivity
    try:
        session = next(get_session())
        from sqlmodel import select
        from models import Organization
        session.exec(select(Organization).limit(1)).first()
        session.close()
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis connectivity (for caching and Celery)
    try:
        import redis
        client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        client.ping()
        health_status["checks"]["redis"] = "ok"
    except Exception as e:
        health_status["checks"]["redis"] = f"warning: {str(e)}"
        # Don't mark as degraded if Redis is down (it's optional for caching)
    
    # Check Celery (scheduler)
    if scheduler and scheduler.running:
        health_status["checks"]["scheduler"] = "ok"
    else:
        health_status["checks"]["scheduler"] = "warning: not running"
    
    return health_status
