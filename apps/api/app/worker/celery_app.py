from celery import Celery

from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "alex",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.worker.jobs",
        "app.worker.reminder_jobs",
        "app.worker.overdue_scan_jobs",
    ],
)

celery_app.conf.update(
    task_default_queue="alex.default",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "scan-due-reminders": {
            "task": "reminders.scan_due",
            "schedule": 30.0,
        },
        "scan-overdue-tasks": {
            "task": "tasks.scan_overdue",
            "schedule": 3600.0,
        },
    },
)
