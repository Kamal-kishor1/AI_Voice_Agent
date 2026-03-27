from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.entities import Task
from app.services.notification_service import NotificationService
from app.services.tasks_service import TasksService
from app.worker.celery_app import celery_app


@celery_app.task(name="tasks.scan_overdue")
def scan_overdue_tasks() -> dict[str, int]:
    return asyncio.run(_scan_overdue_tasks())


async def _scan_overdue_tasks() -> dict[str, int]:
    now = datetime.now(UTC)
    notification_service = NotificationService()
    tasks_service = TasksService()

    async with SessionLocal() as session:
        tasks = (
            await session.scalars(
                select(Task)
                .where(
                    Task.due_date.is_not(None),
                    Task.due_date <= now,
                    Task.status.notin_(["done", "cancelled"]),
                )
                .order_by(Task.due_date.asc())
                .limit(500)
            )
        ).all()

        flagged = 0
        for task in tasks:
            if await notification_service.was_overdue_task_flagged(task.id):
                continue

            await notification_service.publish_event(
                user_id=task.user_id,
                event_type="task.overdue",
                payload={"task": tasks_service.serialize_task(task)},
            )
            await notification_service.mark_overdue_task_flagged(task.id, flagged_at=now)
            flagged += 1

        return {"flagged": flagged}
