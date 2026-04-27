#!/usr/bin/env python3
"""
Celery job queue management CLI.

Usage:
    python manage_jobs.py status          # Show worker and queue status
    python manage_jobs.py purge           # Clear all queues
    python manage_jobs.py trigger TASK    # Manually trigger a task
    python manage_jobs.py retry TASK_ID   # Retry a failed task
    python manage_jobs.py inspect         # Inspect active/scheduled tasks
"""

import sys
import argparse
from celery_app import celery_app
from celery.result import AsyncResult


def show_status():
    """Show worker and queue status."""
    print("=== Celery Status ===\n")
    
    # Active workers
    inspect = celery_app.control.inspect()
    
    print("Active Workers:")
    stats = inspect.stats()
    if stats:
        for worker, info in stats.items():
            print(f"  {worker}")
            print(f"    Pool: {info.get('pool', {}).get('implementation', 'N/A')}")
            print(f"    Max concurrency: {info.get('pool', {}).get('max-concurrency', 'N/A')}")
    else:
        print("  No active workers")
    
    print("\nActive Tasks:")
    active = inspect.active()
    if active:
        for worker, tasks in active.items():
            if tasks:
                print(f"  {worker}: {len(tasks)} task(s)")
                for task in tasks:
                    print(f"    - {task['name']} [{task['id'][:8]}...]")
    else:
        print("  No active tasks")
    
    print("\nScheduled Tasks:")
    scheduled = inspect.scheduled()
    if scheduled:
        for worker, tasks in scheduled.items():
            if tasks:
                print(f"  {worker}: {len(tasks)} task(s)")
    else:
        print("  No scheduled tasks")
    
    print("\nRegistered Tasks:")
    registered = inspect.registered()
    if registered:
        for worker, tasks in registered.items():
            print(f"  {worker}:")
            for task in sorted(tasks):
                if task.startswith("tasks."):
                    print(f"    - {task}")
            break  # Just show one worker's tasks
    
    print("\nBeat Schedule:")
    from celery_app import celery_app
    for name, schedule in celery_app.conf.beat_schedule.items():
        print(f"  {name}")
        print(f"    Task: {schedule['task']}")
        print(f"    Schedule: {schedule['schedule']}")


def purge_queues():
    """Purge all task queues."""
    confirm = input("This will delete all queued tasks. Are you sure? (yes/no): ")
    if confirm.lower() != "yes":
        print("Cancelled.")
        return
    
    inspect = celery_app.control.inspect()
    active_queues = inspect.active_queues()
    
    if not active_queues:
        print("No active queues found.")
        return
    
    queue_names = set()
    for worker, queues in active_queues.items():
        for queue in queues:
            queue_names.add(queue['name'])
    
    for queue_name in queue_names:
        purged = celery_app.control.purge()
        print(f"Purged {purged} task(s) from {queue_name}")


def trigger_task(task_name):
    """Manually trigger a task."""
    full_task_name = f"tasks.{task_name}" if not task_name.startswith("tasks.") else task_name
    
    try:
        task = celery_app.tasks.get(full_task_name)
        if not task:
            print(f"Task '{full_task_name}' not found.")
            print("\nAvailable tasks:")
            for name in sorted(celery_app.tasks.keys()):
                if name.startswith("tasks."):
                    print(f"  {name}")
            return
        
        result = task.delay()
        print(f"Task queued: {full_task_name}")
        print(f"Task ID: {result.id}")
        print(f"State: {result.state}")
        
    except Exception as e:
        print(f"Error triggering task: {str(e)}")


def retry_task(task_id):
    """Retry a failed task."""
    result = AsyncResult(task_id, app=celery_app)
    
    print(f"Task ID: {task_id}")
    print(f"State: {result.state}")
    
    if result.state == 'FAILURE':
        print(f"Error: {result.info}")
        confirm = input("Retry this task? (yes/no): ")
        if confirm.lower() == "yes":
            # Get task name and retry
            print("Note: Manual retry requires knowing task name and arguments.")
            print("Consider using task.apply_async() with original args instead.")
    else:
        print("Task is not in FAILURE state.")


def inspect_tasks():
    """Inspect detailed task information."""
    print("=== Task Inspection ===\n")
    
    inspect = celery_app.control.inspect()
    
    print("Reserved Tasks:")
    reserved = inspect.reserved()
    if reserved:
        for worker, tasks in reserved.items():
            if tasks:
                print(f"  {worker}:")
                for task in tasks:
                    print(f"    {task['name']} [{task['id'][:8]}...]")
    else:
        print("  None")
    
    print("\nRevoked Tasks:")
    revoked = inspect.revoked()
    if revoked:
        for worker, tasks in revoked.items():
            if tasks:
                print(f"  {worker}: {len(tasks)} task(s)")
    else:
        print("  None")
    
    print("\nWorker Configuration:")
    conf = inspect.conf()
    if conf:
        for worker, config in conf.items():
            print(f"  {worker}:")
            print(f"    Timezone: {config.get('timezone', 'N/A')}")
            print(f"    Broker URL: {config.get('broker_url', 'N/A')}")
            print(f"    Result Backend: {config.get('result_backend', 'N/A')}")
            break  # Just show one


def main():
    parser = argparse.ArgumentParser(description="Celery job queue management CLI")
    parser.add_argument("command", choices=["status", "purge", "trigger", "retry", "inspect"],
                       help="Command to execute")
    parser.add_argument("arg", nargs="?", help="Additional argument (task name or ID)")
    
    args = parser.parse_args()
    
    if args.command == "status":
        show_status()
    elif args.command == "purge":
        purge_queues()
    elif args.command == "trigger":
        if not args.arg:
            print("Error: Task name required")
            print("Example: python manage_jobs.py trigger scrape_intelligence")
            sys.exit(1)
        trigger_task(args.arg)
    elif args.command == "retry":
        if not args.arg:
            print("Error: Task ID required")
            sys.exit(1)
        retry_task(args.arg)
    elif args.command == "inspect":
        inspect_tasks()


if __name__ == "__main__":
    main()
