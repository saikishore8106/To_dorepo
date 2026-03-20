"""
scheduler.py — Background Jobs with APScheduler

Concepts covered:
- Background/automated jobs (like cron jobs) using APScheduler
- Python automation: running tasks on a schedule
- Database interaction from a background context
- Use case: Mark overdue tasks automatically
"""

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models


def mark_overdue_tasks():
    """
    Automated Background Job — runs every 60 minutes.
    
    Finds all TODO/IN_PROGRESS tasks past their due_date and logs them.
    In a real system, you might: send email notifications, change status, 
    trigger alerts, etc.
    
    This demonstrates Python-based automation (scripts, schedulers, background jobs).
    """
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        overdue = db.query(models.Task).filter(
            models.Task.due_date < now,
            models.Task.status != models.TaskStatus.DONE
        ).all()

        for task in overdue:
            print(f"[SCHEDULER] ⚠️  Overdue task: '{task.title}' (due: {task.due_date})")

        print(f"[SCHEDULER] ✅ Checked for overdue tasks at {now.isoformat()} — Found: {len(overdue)}")
    except Exception as e:
        print(f"[SCHEDULER] ❌ Error: {e}")
    finally:
        db.close()


def start_scheduler():
    """Initialize and start the background scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=mark_overdue_tasks,
        trigger=IntervalTrigger(minutes=60),
        id="overdue_task_checker",
        name="Check for overdue tasks",
        replace_existing=True,
    )
    scheduler.start()
    print("[SCHEDULER] 🚀 Background scheduler started — checking overdue tasks every 60 min")
    return scheduler
