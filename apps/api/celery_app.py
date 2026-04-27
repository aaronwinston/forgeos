"""Celery application configuration for background tasks."""

from celery import Celery
from celery.signals import task_failure, task_success, task_retry
from config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "forgeos",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Task execution settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "tasks.send_email_digest": {"queue": "notifications"},
        "tasks.send_slack_digest": {"queue": "notifications"},
        "tasks.sync_calendar_events": {"queue": "integrations"},
        "tasks.scrape_intelligence": {"queue": "intelligence"},
        "tasks.poll_trends": {"queue": "intelligence"},
        "tasks.pull_gsc_data": {"queue": "intelligence"},
        "tasks.cross_reference_insights": {"queue": "intelligence"},
        "tasks.cleanup_old_data": {"queue": "maintenance"},
        "tasks.generate_weekly_report": {"queue": "reports"},
        "tasks.archive_completed_sessions": {"queue": "maintenance"},
    },
    
    # Result backend settings
    result_expires=3600 * 24 * 7,  # Keep results for 7 days
    result_extended=True,
    
    # Task retry settings (defaults, can be overridden per task)
    task_default_max_retries=3,
    task_default_retry_delay=60,  # 60 seconds
    
    # Task timeout settings
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,  # 10 minutes hard limit
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Beat schedule (periodic tasks)
    beat_schedule={
        "scrape-intelligence-morning": {
            "task": "tasks.scrape_intelligence",
            "schedule": {"hour": 8, "minute": 0},
            "options": {"queue": "intelligence"}
        },
        "scrape-intelligence-evening": {
            "task": "tasks.scrape_intelligence",
            "schedule": {"hour": 18, "minute": 0},
            "options": {"queue": "intelligence"}
        },
        "sync-calendar-events": {
            "task": "tasks.sync_calendar_events",
            "schedule": 300.0,  # Every 5 minutes
            "options": {"queue": "integrations"}
        },
        "poll-trends-daily": {
            "task": "tasks.poll_trends",
            "schedule": {"hour": 9, "minute": 0},
            "options": {"queue": "intelligence"}
        },
        "pull-gsc-data-daily": {
            "task": "tasks.pull_gsc_data",
            "schedule": {"hour": 9, "minute": 15},
            "options": {"queue": "intelligence"}
        },
        "cross-reference-insights": {
            "task": "tasks.cross_reference_insights",
            "schedule": {"hour": 9, "minute": 30},
            "options": {"queue": "intelligence"}
        },
        "cleanup-old-data": {
            "task": "tasks.cleanup_old_data",
            "schedule": {"hour": 2, "minute": 0},  # 2 AM daily
            "options": {"queue": "maintenance"}
        },
        "send-email-digest": {
            "task": "tasks.send_email_digest",
            "schedule": {"hour": 8, "minute": 0},
            "options": {"queue": "notifications"}
        },
        "send-slack-digest": {
            "task": "tasks.send_slack_digest",
            "schedule": {"hour": 8, "minute": 5},
            "options": {"queue": "notifications"}
        },
        "generate-weekly-report": {
            "task": "tasks.generate_weekly_report",
            "schedule": {"day_of_week": 1, "hour": 7, "minute": 0},  # Monday 7 AM
            "options": {"queue": "reports"}
        },
        "archive-completed-sessions": {
            "task": "tasks.archive_completed_sessions",
            "schedule": {"hour": 3, "minute": 0},  # 3 AM daily
            "options": {"queue": "maintenance"}
        },
    },
)


# Signal handlers for monitoring
@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **kw):
    """Log task failures for monitoring."""
    logger.error(
        f"Task {sender.name} [{task_id}] failed",
        extra={
            "task_name": sender.name,
            "task_id": task_id,
            "exception": str(exception),
            "args": args,
            "kwargs": kwargs,
        },
        exc_info=einfo
    )


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """Log successful task completion."""
    logger.info(
        f"Task {sender.name} completed successfully",
        extra={
            "task_name": sender.name,
            "result": result if isinstance(result, (str, int, float, bool)) else str(result)[:200]
        }
    )


@task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, einfo=None, **kwargs):
    """Log task retries."""
    logger.warning(
        f"Task {sender.name} [{task_id}] retrying",
        extra={
            "task_name": sender.name,
            "task_id": task_id,
            "reason": str(reason),
        }
    )
