"""Health checks and monitoring for background jobs."""

from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from celery_app import celery_app
from pydantic import BaseModel
from typing import Optional, Dict, Any
import redis

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class TaskStatus(BaseModel):
    task_id: str
    state: str
    result: Optional[Any] = None
    error: Optional[str] = None


class SystemHealth(BaseModel):
    status: str
    redis_connected: bool
    active_workers: int
    registered_tasks: int
    queues: Dict[str, int]


@router.get("/health", response_model=SystemHealth)
async def health_check():
    """Check health of job queue system."""
    try:
        # Check Redis connection
        from config import settings
        r = redis.from_url(settings.CELERY_BROKER_URL)
        redis_connected = r.ping()
    except Exception:
        redis_connected = False
    
    # Check workers
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    active_workers = len(stats) if stats else 0
    
    # Get registered tasks
    registered = inspect.registered()
    task_count = 0
    if registered:
        for worker, tasks in registered.items():
            task_count = len([t for t in tasks if t.startswith("tasks.")])
            break
    
    # Get queue info
    queues = {}
    active_queues = inspect.active_queues()
    if active_queues:
        for worker, worker_queues in active_queues.items():
            for queue_info in worker_queues:
                queue_name = queue_info['name']
                queues[queue_name] = queues.get(queue_name, 0) + 1
    
    status = "healthy" if redis_connected and active_workers > 0 else "degraded"
    
    return SystemHealth(
        status=status,
        redis_connected=redis_connected,
        active_workers=active_workers,
        registered_tasks=task_count,
        queues=queues
    )


@router.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get status of a specific task."""
    result = AsyncResult(task_id, app=celery_app)
    
    return TaskStatus(
        task_id=task_id,
        state=result.state,
        result=result.result if result.state == "SUCCESS" else None,
        error=str(result.info) if result.state == "FAILURE" else None
    )


@router.post("/trigger/{task_name}")
async def trigger_task(task_name: str):
    """Manually trigger a task."""
    full_task_name = f"tasks.{task_name}" if not task_name.startswith("tasks.") else task_name
    
    task = celery_app.tasks.get(full_task_name)
    if not task:
        available_tasks = [name for name in celery_app.tasks.keys() if name.startswith("tasks.")]
        raise HTTPException(
            status_code=404,
            detail=f"Task '{full_task_name}' not found. Available: {', '.join(available_tasks)}"
        )
    
    result = task.delay()
    return {
        "task_id": result.id,
        "task_name": full_task_name,
        "status": "queued"
    }


@router.get("/workers")
async def get_workers():
    """Get information about active workers."""
    inspect = celery_app.control.inspect()
    
    stats = inspect.stats()
    active = inspect.active()
    
    workers = []
    if stats:
        for worker_name, worker_stats in stats.items():
            worker_active = active.get(worker_name, []) if active else []
            workers.append({
                "name": worker_name,
                "pool": worker_stats.get("pool", {}).get("implementation", "N/A"),
                "max_concurrency": worker_stats.get("pool", {}).get("max-concurrency", 0),
                "active_tasks": len(worker_active),
                "tasks": [{"name": t["name"], "id": t["id"][:8]} for t in worker_active]
            })
    
    return {"workers": workers}


@router.get("/schedule")
async def get_schedule():
    """Get beat schedule information."""
    schedule = []
    for name, config in celery_app.conf.beat_schedule.items():
        schedule.append({
            "name": name,
            "task": config["task"],
            "schedule": str(config["schedule"]),
            "queue": config.get("options", {}).get("queue", "default")
        })
    
    return {"schedule": schedule}
