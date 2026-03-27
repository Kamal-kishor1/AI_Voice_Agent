from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.entities import Reminder, Task
from app.services.notification_service import NotificationService
from app.services.tasks_service import TasksService
from app.worker.celery_app import celery_app


@celery_app.task(name="reminders.scan_due")
def scan_due_reminders() -> dict[str, int]:
    return asyncio.run(_scan_due_reminders())


async def _scan_due_reminders() -> dict[str, int]:
    now = datetime.now(UTC)
    notification_service = NotificationService()
    tasks_service = TasksService()

    async with SessionLocal() as session:
        delivered = 0
        retried = 0
        rescheduled = 0

        reminders = (
            await session.scalars(
                select(Reminder)
                .where(Reminder.status == "pending", Reminder.remind_at <= now)
                .order_by(Reminder.remind_at.asc())
                .limit(200)
            )
        ).all()

        for reminder in reminders:
            task = await _linked_task(session, reminder)
            await _publish_reminder_event(
                notification_service=notification_service,
                tasks_service=tasks_service,
                reminder=reminder,
                task=task,
                attempt=1,
                retry=False,
            )
            await notification_service.set_reminder_delivery_state(
                reminder.id,
                attempts=1,
                last_sent_at=now,
                retry_at=now + timedelta(minutes=5),
                payload={
                    "user_id": str(reminder.user_id),
                    "task_id": str(reminder.task_id) if reminder.task_id else None,
                },
            )

            if reminder.is_recurring and reminder.recurrence_rule:
                next_at = tasks_service.next_recurrence_at(reminder=reminder, base_time=reminder.remind_at)
                if next_at is not None:
                    reminder.remind_at = next_at
                    reminder.status = "pending"
                    rescheduled += 1
            else:
                reminder.status = "sent"

            delivered += 1

        retry_ids = await notification_service.pop_due_reminder_retries(now=now)
        for reminder_id in retry_ids:
            state = await notification_service.get_reminder_delivery_state(reminder_id)
            if state is None:
                continue

            attempts = int(state.get("attempts", 0))
            if attempts >= 2:
                await notification_service.clear_reminder_delivery_state(reminder_id)
                continue

            reminder = await session.scalar(select(Reminder).where(Reminder.id == UUID(reminder_id)))
            if reminder is None or reminder.status == "dismissed":
                await notification_service.clear_reminder_delivery_state(reminder_id)
                continue

            task = await _linked_task(session, reminder)
            await _publish_reminder_event(
                notification_service=notification_service,
                tasks_service=tasks_service,
                reminder=reminder,
                task=task,
                attempt=attempts + 1,
                retry=True,
            )
            await notification_service.set_reminder_delivery_state(
                reminder.id,
                attempts=attempts + 1,
                last_sent_at=now,
                retry_at=None,
                payload={
                    "user_id": str(reminder.user_id),
                    "task_id": str(reminder.task_id) if reminder.task_id else None,
                },
            )
            retried += 1

        await session.commit()
        return {
            "delivered": delivered,
            "retried": retried,
            "rescheduled": rescheduled,
        }


async def _linked_task(session, reminder: Reminder) -> Task | None:
    if reminder.task_id is None:
        return None
    return await session.scalar(select(Task).where(Task.id == reminder.task_id))


async def _publish_reminder_event(
    *,
    notification_service: NotificationService,
    tasks_service: TasksService,
    reminder: Reminder,
    task: Task | None,
    attempt: int,
    retry: bool,
) -> None:
    await notification_service.publish_event(
        user_id=reminder.user_id,
        event_type="reminder.triggered",
        payload={
            "attempt": attempt,
            "retry": retry,
            "reminder": tasks_service.serialize_reminder(reminder),
            "task": tasks_service.serialize_task(task) if task is not None else None,
        },
    )
