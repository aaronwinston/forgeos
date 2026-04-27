# ForgeOS Background Job Queue

This document explains the Celery-based background job queue system used in ForgeOS for reliable asynchronous task processing.

## Architecture

ForgeOS uses **Celery** with **Redis** as the message broker and result backend. This provides:

- **Reliable task queuing**: Tasks are persisted in Redis and won't be lost
- **Automatic retries**: Failed tasks retry with exponential backoff
- **Task monitoring**: Built-in monitoring via Flower UI
- **Distributed processing**: Scale horizontally by adding more workers
- **Scheduled tasks**: Periodic tasks via Celery Beat

## Components

### 1. Redis (Message Broker)
- Stores task queue and results
- Runs on port 6379
- Configured with persistence (AOF) and memory limits

### 2. Celery Workers
- Process tasks from queues
- Multiple queues for different task types:
  - `intelligence`: Data scraping and analysis
  - `integrations`: External API sync (Calendar, GSC, Trends)
  - `notifications`: Email and Slack digests
  - `maintenance`: Data cleanup and archival
  - `reports`: Report generation

### 3. Celery Beat
- Scheduler for periodic tasks
- Runs daily scrapes, syncs, cleanups

### 4. Flower (Optional)
- Web UI for monitoring tasks
- Access at http://localhost:5555
- Shows task status, success/failure rates, worker health

## Running the System

### Local Development

#### Start Redis only:
```bash
docker-compose up -d redis
```

#### Start all services:
```bash
docker-compose up -d
```

#### Run worker locally (without Docker):
```bash
cd apps/api
celery -A celery_app worker --loglevel=info -Q intelligence,integrations,notifications,maintenance,reports
```

#### Run beat scheduler locally:
```bash
cd apps/api
celery -A celery_app beat --loglevel=info
```

### Production

Use Docker Compose with proper environment variables:

```bash
# Start all services
docker-compose up -d

# Scale workers
docker-compose up -d --scale celery-worker=4

# View logs
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat
```

## Scheduled Tasks

Current periodic tasks (defined in `celery_app.py`):

| Task | Schedule | Queue | Description |
|------|----------|-------|-------------|
| `scrape_intelligence` | 8 AM, 6 PM daily | intelligence | Scrape and score intelligence sources |
| `sync_calendar_events` | Every 5 minutes | integrations | Poll Google Calendar for updates |
| `poll_trends` | 9 AM daily | intelligence | Fetch Google Trends data |
| `pull_gsc_data` | 9:15 AM daily | intelligence | Pull Google Search Console data |
| `cross_reference_insights` | 9:30 AM daily | intelligence | Generate insights from cross-referencing |
| `send_email_digest` | 8 AM daily | notifications | Send email digests to organizations |
| `send_slack_digest` | 8:05 AM daily | notifications | Send Slack digests |
| `cleanup_old_data` | 2 AM daily | maintenance | Delete old low-value data |
| `archive_completed_sessions` | 3 AM daily | maintenance | Archive old chat sessions |
| `generate_weekly_report` | Monday 7 AM | reports | Generate weekly analytics reports |

## Adding New Tasks

### 1. Define the Task

Add to `tasks.py`:

```python
@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def my_new_task(self):
    """Task description."""
    try:
        # Your task logic here
        logger.info("Starting my_new_task")
        
        # Access database via self._session (DatabaseTask provides this)
        session = self._session
        
        # Do work...
        
        return {"status": "success", "processed": 42}
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}", exc_info=True)
        raise
```

#### Task Decorator Options:

- `bind=True`: Pass `self` to access task metadata
- `base=DatabaseTask`: Automatic database session handling
- `autoretry_for=(Exception,)`: Auto-retry on these exceptions
- `retry_kwargs`: Control retry behavior
- `retry_backoff=True`: Use exponential backoff
- `retry_backoff_max`: Maximum retry delay (default 3600s)
- `retry_jitter=True`: Add randomness to avoid thundering herd
- `soft_time_limit`: Soft timeout (raises exception)
- `time_limit`: Hard timeout (kills task)

### 2. Add Task Routing

Update `celery_app.py` task routes:

```python
task_routes={
    # ... existing routes ...
    "tasks.my_new_task": {"queue": "maintenance"},
}
```

Choose appropriate queue:
- `intelligence`: Data gathering, analysis
- `integrations`: External API calls
- `notifications`: User communications
- `maintenance`: Cleanup, archival
- `reports`: Analytics, reporting

### 3. Schedule Periodic Execution (Optional)

Add to `beat_schedule` in `celery_app.py`:

```python
beat_schedule={
    # ... existing schedules ...
    "my-new-task-daily": {
        "task": "tasks.my_new_task",
        "schedule": {"hour": 10, "minute": 30},  # 10:30 AM daily
        "options": {"queue": "maintenance"}
    },
}
```

Schedule options:
- **Cron-style**: `{"hour": 8, "minute": 0}` = 8 AM daily
- **Interval**: `300.0` = every 5 minutes (seconds)
- **Day of week**: `{"day_of_week": 1, "hour": 7}` = Monday 7 AM
- **Multiple times**: Create multiple schedule entries

### 4. Call Manually (Optional)

Trigger from API endpoint:

```python
from tasks import my_new_task

@router.post("/api/trigger-my-task")
async def trigger_task(auth: AuthContext = Depends(get_current_user)):
    # Queue task asynchronously
    result = my_new_task.delay()
    
    return {"task_id": result.id, "status": "queued"}
```

Or with arguments:

```python
result = my_new_task.apply_async(
    args=[arg1, arg2],
    kwargs={"key": "value"},
    queue="maintenance",
    countdown=60  # Delay 60 seconds
)
```

## Error Handling

### Retry Configuration

Tasks automatically retry with exponential backoff:

- **Retry delay**: `60 * (2 ** retries)` seconds
  - 1st retry: 60s (1 min)
  - 2nd retry: 120s (2 min)
  - 3rd retry: 240s (4 min)
  - 4th retry: 480s (8 min)
  - 5th retry: 960s (16 min)

- **Max retries**: Configurable per task (default 3)
- **Jitter**: Random offset to prevent retry storms

### Custom Retry Logic

```python
@celery_app.task(bind=True, max_retries=5)
def my_task(self):
    try:
        # Task logic
        pass
    except TemporaryError as exc:
        # Retry after custom delay
        raise self.retry(exc=exc, countdown=120)
    except PermanentError as exc:
        # Don't retry, log to dead letter queue
        handle_failed_task.delay(
            task_id=self.request.id,
            task_name=self.name,
            args=self.request.args,
            kwargs=self.request.kwargs,
            exc=str(exc),
            traceback=traceback.format_exc()
        )
```

### Dead Letter Queue

Permanently failed tasks (after all retries) are handled by `handle_failed_task()`:

- Logs full error details
- Could store in database for audit
- Could trigger alerts

## Monitoring

### Flower UI

Access at http://localhost:5555 when running:

- Task history and status
- Worker health and stats
- Queue lengths
- Success/failure rates
- Task execution times

### Logs

All tasks log to application logger:

- **INFO**: Task start/completion
- **WARNING**: Task retries
- **ERROR**: Task failures

View logs:
```bash
# Docker
docker-compose logs -f celery-worker

# Local
# Logs output to stdout/stderr
```

### Metrics

Task execution triggers signals:
- `task_success`: Successful completion
- `task_failure`: Failed execution
- `task_retry`: Retry attempt

These are logged with structured data for monitoring systems.

### Health Checks

Redis health check:
```bash
docker-compose ps redis
# Should show "healthy"

redis-cli ping
# Should return "PONG"
```

Worker health:
```bash
celery -A celery_app inspect active
celery -A celery_app inspect stats
```

## Configuration

### Environment Variables

Set in `.env`:

```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Celery Settings

Customize in `celery_app.py`:

```python
celery_app.conf.update(
    task_serializer="json",          # Serialization format
    result_expires=3600 * 24 * 7,    # Keep results 7 days
    task_soft_time_limit=300,         # 5 min soft timeout
    task_time_limit=600,              # 10 min hard timeout
    worker_prefetch_multiplier=4,     # Tasks to prefetch
    worker_max_tasks_per_child=1000,  # Restart worker after N tasks
)
```

## Best Practices

1. **Idempotency**: Design tasks to be safely retried
   - Check if work already done before starting
   - Use upsert instead of insert
   - Handle duplicate processing gracefully

2. **Timeouts**: Set appropriate time limits
   - `soft_time_limit`: Raises exception for graceful cleanup
   - `time_limit`: Hard kill if soft limit exceeded
   - Critical for preventing hung tasks

3. **Database Sessions**: Use `DatabaseTask` base class
   - Automatic session management
   - Proper cleanup on success/failure
   - Access via `self._session`

4. **Logging**: Log liberally
   - Log task start with context
   - Log progress for long tasks
   - Log errors with full context

5. **Error Handling**: Be specific
   - Catch specific exceptions
   - Different retry logic per error type
   - Log context for debugging

6. **Resource Cleanup**: Always clean up
   - Close file handles
   - Release locks
   - Clean temporary data

7. **Task Size**: Keep tasks focused
   - One responsibility per task
   - Break large jobs into smaller tasks
   - Chain tasks if needed

## Troubleshooting

### Task Not Executing

1. Check Redis is running:
   ```bash
   redis-cli ping
   ```

2. Check worker is running:
   ```bash
   docker-compose ps celery-worker
   ```

3. Check worker logs:
   ```bash
   docker-compose logs celery-worker
   ```

4. Verify queue name matches task routing

### Task Keeps Failing

1. Check error logs for exception details
2. Verify database connectivity
3. Check external API availability
4. Verify credentials/permissions
5. Test task logic in isolation

### High Memory Usage

1. Check `worker_max_tasks_per_child` setting
2. Monitor for memory leaks in task code
3. Scale workers instead of increasing concurrency
4. Check Redis memory usage and `maxmemory` setting

### Tasks Delayed

1. Check queue backlog in Flower
2. Scale up workers if needed
3. Optimize slow tasks
4. Consider task priorities

## References

- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices)
