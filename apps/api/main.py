from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import create_db_and_tables
from routers import projects, chat, intelligence, settings, files

app = FastAPI(title="ForgeOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(chat.router)
app.include_router(intelligence.router)
app.include_router(settings.router)
app.include_router(files.router)

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup():
    create_db_and_tables()

    from services.scraping import run_all_scrapers
    from services.scoring import score_items_batch
    from models import ScrapeItem
    from sqlmodel import Session, select
    from database import engine

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

    scheduler.add_job(scheduled_scrape, 'cron', hour=8, minute=0)
    scheduler.add_job(scheduled_scrape, 'cron', hour=18, minute=0)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
