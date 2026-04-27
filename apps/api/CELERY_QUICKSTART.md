# Celery Quick Start Guide

Get the ForgeOS background job queue running in 5 minutes.

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended) OR Redis installed locally

## Quick Start with Docker

1. **Start Redis and Celery services:**
   ```bash
   cd /path/to/forgeos
   docker-compose up -d
   ```

2. **Verify services are running:**
   ```bash
   docker-compose ps
   ```
   
   You should see:
   - `forgeos-redis` (healthy)
   - `forgeos-celery-worker` (up)
   - `forgeos-celery-beat` (up)
   - `forgeos-celery-flower` (up)

3. **Access Flower monitoring UI:**
   
   Open http://localhost:5555 in your browser

4. **Test a task:**
   ```bash
   cd apps/api
   python manage_jobs.py trigger scrape_intelligence
   ```

5. **View logs:**
   ```bash
   docker-compose logs -f celery-worker
   ```

That's it! Background jobs are now running.

## Quick Start without Docker

1. **Install Redis:**
   ```bash
   # macOS
   brew install redis
   brew services start redis
   
   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis
   
   # Verify
   redis-cli ping  # Should return PONG
   ```

2. **Install Python dependencies:**
   ```bash
   cd apps/api
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and set:
   # CELERY_BROKER_URL=redis://localhost:6379/0
   # CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

4. **Start Celery worker (Terminal 1):**
   ```bash
   cd apps/api
   celery -A celery_app worker --loglevel=info
   ```

5. **Start Celery beat scheduler (Terminal 2):**
   ```bash
   cd apps/api
   celery -A celery_app beat --loglevel=info
   ```

6. **Start Flower monitoring (Terminal 3, optional):**
   ```bash
   cd apps/api
   celery -A celery_app flower --port=5555
   ```

7. **Test a task:**
   ```bash
   cd apps/api
   python manage_jobs.py trigger scrape_intelligence
   ```

## What's Running?

After starting the services, these scheduled tasks run automatically:

| Task | Schedule | What it does |
|------|----------|--------------|
| Intelligence Scraping | 8 AM & 6 PM daily | Scrapes and scores intelligence sources |
| Calendar Sync | Every 5 minutes | Syncs Google Calendar events |
| Trends Polling | 9 AM daily | Fetches Google Trends data |
| GSC Data Pull | 9:15 AM daily | Pulls Search Console data |
| Email Digest | 8 AM daily | Sends daily email digests |
| Slack Digest | 8:05 AM daily | Sends Slack notifications |
| Data Cleanup | 2 AM daily | Removes old low-value data |
| Weekly Report | Monday 7 AM | Generates weekly analytics |

## Common Commands

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f celery-worker

# Stop all services
docker-compose down

# Restart worker
docker-compose restart celery-worker

# Scale workers
docker-compose up -d --scale celery-worker=4
```

### Job Management

```bash
cd apps/api

# Check system status
python manage_jobs.py status

# Trigger a task manually
python manage_jobs.py trigger scrape_intelligence

# Inspect active tasks
python manage_jobs.py inspect

# Clear all queues (WARNING: deletes queued tasks)
python manage_jobs.py purge
```

### Celery CLI

```bash
cd apps/api

# Check active workers
celery -A celery_app inspect active

# Worker stats
celery -A celery_app inspect stats

# Registered tasks
celery -A celery_app inspect registered

# Purge queue
celery -A celery_app purge
```

## Monitoring

### Flower UI

**URL**: http://localhost:5555

Features:
- Real-time task monitoring
- Worker status and stats
- Task history and results
- Queue lengths
- Success/failure rates

### API Endpoints

Check job system health:
```bash
curl http://localhost:8000/api/jobs/health
```

Get task status:
```bash
curl http://localhost:8000/api/jobs/task/{task_id}
```

Trigger task via API:
```bash
curl -X POST http://localhost:8000/api/jobs/trigger/scrape_intelligence
```

## Troubleshooting

### "No active workers" error

**Problem**: Worker not running

**Fix**:
```bash
# Docker
docker-compose up -d celery-worker

# Local
celery -A celery_app worker --loglevel=info
```

### "Connection refused" error

**Problem**: Redis not running

**Fix**:
```bash
# Docker
docker-compose up -d redis

# Local (macOS)
brew services start redis

# Verify
redis-cli ping
```

### Tasks not executing

**Problem**: Worker running but tasks stuck

**Fix**:
1. Check worker logs: `docker-compose logs celery-worker`
2. Verify queue names in task routing
3. Restart worker: `docker-compose restart celery-worker`

### Import errors

**Problem**: Worker can't import tasks

**Fix**:
```bash
cd apps/api
pip install -r requirements.txt
```

## Next Steps

- Read [BACKGROUND_JOBS.md](./BACKGROUND_JOBS.md) for complete documentation
- Read [CELERY_MIGRATION.md](./CELERY_MIGRATION.md) for migration details
- Customize task schedules in `celery_app.py`
- Add new tasks following examples in `tasks.py`
- Configure email/Slack webhooks for notifications
- Set up production monitoring and alerts

## Getting Help

- Check logs: `docker-compose logs celery-worker`
- Use Flower UI: http://localhost:5555
- Run diagnostics: `python manage_jobs.py status`
- Review task code in `tasks.py`
- Check Celery config in `celery_app.py`
