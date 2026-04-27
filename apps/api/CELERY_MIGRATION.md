# Migration from APScheduler to Celery

This document guides the migration from APScheduler to Celery for background job processing in ForgeOS.

## Why Migrate?

**APScheduler Limitations:**
- In-process scheduler (doesn't survive app restarts)
- No built-in retry logic
- Limited error handling
- No distributed task processing
- Difficult to monitor and debug
- No task queuing or prioritization

**Celery Benefits:**
- Persistent task queue (survives restarts)
- Automatic retries with exponential backoff
- Comprehensive error handling
- Horizontal scaling with multiple workers
- Built-in monitoring (Flower)
- Task routing and prioritization
- Dead letter queue for failed tasks

## Migration Steps

### Phase 1: Install Dependencies

```bash
cd apps/api
pip install celery[redis] redis flower
```

### Phase 2: Start Redis

```bash
# Using Docker Compose
docker-compose up -d redis

# Or install Redis locally
brew install redis  # macOS
redis-server
```

### Phase 3: Configure Environment

Add to `.env`:
```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Phase 4: Run Celery Services

```bash
# Terminal 1: Start worker
celery -A celery_app worker --loglevel=info -Q intelligence,integrations,notifications,maintenance,reports

# Terminal 2: Start beat scheduler
celery -A celery_app beat --loglevel=info

# Terminal 3 (optional): Start Flower monitoring
celery -A celery_app flower --port=5555
```

### Phase 5: Disable APScheduler (Optional)

Once Celery is running and verified, you can disable APScheduler in `main.py`:

**Option A: Keep Both (Recommended for transition)**
- Run both systems in parallel during testing
- Gradually migrate endpoints to trigger Celery tasks
- Monitor both systems
- Once confident, remove APScheduler

**Option B: Switch to Celery Only**
- Comment out APScheduler code in `main.py`
- All scheduled work handled by Celery Beat
- Background tasks triggered via Celery

### Phase 6: Update API Endpoints

Change from APScheduler background tasks to Celery:

**Before (APScheduler):**
```python
from fastapi import BackgroundTasks

@router.post("/trigger-scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_all_scrapers)
    return {"status": "queued"}
```

**After (Celery):**
```python
from tasks import scrape_intelligence

@router.post("/trigger-scrape")
async def trigger_scrape():
    result = scrape_intelligence.delay()
    return {"status": "queued", "task_id": result.id}
```

## Task Mapping

| APScheduler Job | Celery Task | Schedule |
|----------------|-------------|----------|
| `scheduled_scrape` (8 AM) | `tasks.scrape_intelligence` | 8 AM daily |
| `scheduled_scrape` (6 PM) | `tasks.scrape_intelligence` | 6 PM daily |
| `scheduled_calendar_poll` | `tasks.sync_calendar_events` | Every 5 min |
| `scheduled_trends_poll` | `tasks.poll_trends` | 9 AM daily |
| `scheduled_gsc_pull` | `tasks.pull_gsc_data` | 9:15 AM daily |
| `scheduled_cross_reference` | `tasks.cross_reference_insights` | 9:30 AM daily |
| N/A | `tasks.send_email_digest` | 8 AM daily |
| N/A | `tasks.send_slack_digest` | 8:05 AM daily |
| N/A | `tasks.cleanup_old_data` | 2 AM daily |
| N/A | `tasks.archive_completed_sessions` | 3 AM daily |
| N/A | `tasks.generate_weekly_report` | Monday 7 AM |

## Code Changes

### main.py - Disable APScheduler

```python
# Comment out or remove APScheduler code
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# scheduler = AsyncIOScheduler()

# @app.on_event("startup")
# async def startup():
#     create_db_and_tables()
#     # ... APScheduler job definitions ...
#     # scheduler.start()

# @app.on_event("shutdown")
# async def shutdown():
#     scheduler.shutdown()

# New: Just create DB tables
@app.on_event("startup")
async def startup():
    create_db_and_tables()
```

### routers/intelligence.py - Update Trigger Endpoint

```python
from tasks import scrape_intelligence

@router.post("/trigger-scrape")
async def trigger_scrape():
    """Trigger intelligence scraping via Celery."""
    result = scrape_intelligence.delay()
    return {
        "ok": True,
        "message": "Scrape queued",
        "task_id": result.id
    }

@router.get("/scrape-status/{task_id}")
async def get_scrape_status(task_id: str):
    """Check status of scraping task."""
    from celery.result import AsyncResult
    from celery_app import celery_app
    
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "state": result.state,
        "info": result.info if result.state == "FAILURE" else None,
        "result": result.result if result.state == "SUCCESS" else None
    }
```

## Testing

### Verify Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### Verify Workers Running

```bash
celery -A celery_app inspect active
# Should show active workers
```

### Trigger Test Task

```bash
python manage_jobs.py trigger scrape_intelligence
# Should queue task and show task ID
```

### Check Flower UI

Visit http://localhost:5555 to see:
- Active workers
- Task history
- Success/failure rates
- Queue lengths

### Monitor Logs

```bash
# Worker logs
docker-compose logs -f celery-worker

# Beat scheduler logs
docker-compose logs -f celery-beat
```

## Rollback Plan

If issues arise, you can quickly rollback:

1. **Stop Celery services:**
   ```bash
   docker-compose stop celery-worker celery-beat
   ```

2. **Uncomment APScheduler code in main.py**

3. **Restart FastAPI:**
   ```bash
   # APScheduler will resume scheduling
   ```

4. **Investigate and fix Celery issues**

5. **Retry migration when ready**

## Production Deployment

### Docker Compose

Use the provided `docker-compose.yml`:

```bash
docker-compose up -d
```

This starts:
- Redis (persistent message broker)
- Celery worker (task processor)
- Celery beat (scheduler)
- Flower (monitoring UI)

### Kubernetes

For Kubernetes deployment:

1. **Redis**: Use managed Redis (AWS ElastiCache, GCP Memorystore) or Redis Operator
2. **Workers**: Deploy as Deployment with multiple replicas
3. **Beat**: Deploy as single-replica Deployment (only one scheduler needed)
4. **Flower**: Deploy as Deployment with Service

### Environment Variables

Ensure these are set in production:

```bash
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Scaling

Scale workers based on load:

```bash
# Docker Compose
docker-compose up -d --scale celery-worker=4

# Kubernetes
kubectl scale deployment celery-worker --replicas=4
```

## Monitoring in Production

1. **Flower UI**: Monitor task execution, worker health
2. **Redis monitoring**: Track memory usage, connection count
3. **Application logs**: Celery logs task start/completion/failures
4. **Metrics**: Integrate with Prometheus/Datadog for metrics
5. **Alerts**: Set up alerts for:
   - Worker down
   - High failure rate
   - Queue backlog
   - Redis connection issues

## Common Issues

### Tasks Not Executing

**Symptom**: Tasks queued but not processed

**Fixes**:
1. Verify Redis is running: `redis-cli ping`
2. Verify worker is running: `celery -A celery_app inspect active`
3. Check queue names match in routing config
4. Check worker logs for errors

### Database Errors

**Symptom**: Tasks fail with database errors

**Fixes**:
1. Ensure database connection string is correct
2. Check database permissions
3. Verify DatabaseTask base class is used
4. Check connection pooling settings

### Memory Issues

**Symptom**: Workers consuming excessive memory

**Fixes**:
1. Reduce `worker_prefetch_multiplier` in config
2. Lower `worker_max_tasks_per_child` (restart workers more often)
3. Check for memory leaks in task code
4. Scale horizontally instead of vertically

### Schedule Not Running

**Symptom**: Beat schedule not triggering tasks

**Fixes**:
1. Verify only ONE beat instance is running
2. Check beat logs for schedule loading
3. Verify schedule config in `celery_app.py`
4. Restart beat scheduler

## Additional Resources

- [Celery Documentation](https://docs.celeryq.dev/)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
- ForgeOS `BACKGROUND_JOBS.md` - Complete job queue documentation
