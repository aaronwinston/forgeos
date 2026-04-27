# instrumentation must be imported and called before any Anthropic clients are created
import instrumentation
instrumentation.setup_tracing()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import create_db_and_tables
from routers import projects, chat, intelligence, settings, files, sessions, briefing, integrations, calendar, search, orgs, runtimes, billing, usage, onboarding, doctrine, mission_control, skills, trust

app = FastAPI(title="ForgeOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(chat.router)
app.include_router(intelligence.router)
app.include_router(settings.router)
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
            for item_data in scored:
                existing = session.exec(
                    select(ScrapeItem).where(ScrapeItem.source_url == item_data.get("source_url", ""))
                ).first()
                if not existing and item_data.get("source_url"):
                    item = ScrapeItem(**{k: v for k, v in item_data.items() if k in ScrapeItem.__fields__})
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

    scheduler.add_job(scheduled_scrape, 'cron', hour=8, minute=0, id='scrape_morning', replace_existing=True)
    scheduler.add_job(scheduled_scrape, 'cron', hour=18, minute=0, id='scrape_evening', replace_existing=True)
    scheduler.add_job(scheduled_calendar_poll, 'interval', minutes=5, id='calendar_poll', replace_existing=True)
    scheduler.add_job(scheduled_trends_poll, 'cron', hour=9, minute=0, id='trends_poll', replace_existing=True)  # Daily at 9 AM
    scheduler.add_job(scheduled_gsc_pull, 'cron', hour=9, minute=15, id='gsc_pull', replace_existing=True)  # 15 min after trends
    scheduler.add_job(scheduled_cross_reference, 'cron', hour=9, minute=30, id='cross_ref_pass', replace_existing=True)  # 30 min after trends
    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
