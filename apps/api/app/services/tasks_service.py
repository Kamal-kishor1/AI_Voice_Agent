from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import status
from sqlalchemy import Select, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_parser import parse_user_datetime
from app.core.exceptions import AppError
from app.models.entities import Reminder, Task
from app.schemas.task import (
    CreateReminderRequest,
    CreateTaskRequest,
    UpdateReminderRequest,
    UpdateTaskRequest,
)
from app.services.notification_service import NotificationService


class TasksService:
    def __init__(self) -> None:
        self.notification_service = NotificationService()

    async def list_tasks(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        status_filter: str | None = None,
        priority: str | None = None,
        sort_by: str = "due_date",
        sort_order: str = "asc",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Task], int]:
        filters = [Task.user_id == user_id]

        if status_filter is not None:
            filters.append(Task.status == self._normalize_task_status(status_filter))
        if priority is not None:
            filters.append(Task.priority == self._normalize_priority(priority))

        order_clause = self._task_order_clause(sort_by=sort_by, sort_order=sort_order)

        items = (
            await session.scalars(
                select(Task)
                .where(*filters)
                .order_by(order_clause)
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
        ).all()
        total = await session.scalar(select(func.count()).select_from(Task).where(*filters))
        return list(items), int(total or 0)

    async def create_task(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        payload: CreateTaskRequest,
        timezone_name: str | None = None,
        source: str = "manual",
    ) -> Task:
        title = payload.title.strip()
        if not title:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Task title cannot be empty.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        due_date = self._parse_optional_datetime(
            payload.due_date,
            timezone_name=payload.timezone or timezone_name or "Asia/Kolkata",
            field_name="due_date",
            prefer_future=True,
        )

        task = Task(
            user_id=user_id,
            title=title,
            description=self._clean_optional_text(payload.description),
            priority=self._normalize_priority(payload.priority),
            status="todo",
            due_date=due_date,
            source=source.strip() or "manual",
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    async def update_task(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        task_id: UUID,
        payload: UpdateTaskRequest,
        timezone_name: str | None = None,
    ) -> Task:
        task = await self.get_task(session=session, user_id=user_id, task_id=task_id)

        if payload.title is not None:
            title = payload.title.strip()
            if not title:
                raise AppError(
                    code="VALIDATION_ERROR",
                    message="Task title cannot be empty.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            task.title = title

        if payload.description is not None:
            task.description = self._clean_optional_text(payload.description)

        if payload.priority is not None:
            task.priority = self._normalize_priority(payload.priority)

        if payload.due_date is not None:
            task.due_date = self._parse_optional_datetime(
                payload.due_date,
                timezone_name=payload.timezone or timezone_name or "Asia/Kolkata",
                field_name="due_date",
                prefer_future=False,
            )

        if payload.status is not None:
            next_status = self._normalize_task_status(payload.status)
            if next_status == "done" and task.status != "done":
                task.completed_at = datetime.now(UTC)
            elif next_status != "done":
                task.completed_at = None
            task.status = next_status

        await session.commit()
        await session.refresh(task)
        await self._sync_task_overdue_flag(task)
        return task

    async def delete_task(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        task_id: UUID,
    ) -> None:
        task = await self.get_task(session=session, user_id=user_id, task_id=task_id)
        await session.delete(task)
        await session.commit()
        await self.notification_service.clear_overdue_task_flag(task_id)

    async def get_task(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        task_id: UUID,
    ) -> Task:
        task = await session.scalar(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        if task is None:
            raise AppError(
                code="RESOURCE_NOT_FOUND",
                message="Task not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return task

    async def find_task_by_reference(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        reference: str | None,
        allow_done: bool = False,
    ) -> Task:
        text = (reference or "").strip()
        if not text:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Task reference is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        filters = [Task.user_id == user_id]
        if not allow_done:
            filters.append(Task.status.notin_(["done", "cancelled"]))

        lowered = text.lower()
        rank = case(
            (func.lower(Task.title) == lowered, 0),
            (func.lower(Task.title).like(f"{lowered}%"), 1),
            else_=2,
        )

        task = await session.scalar(
            select(Task)
            .where(
                *filters,
                or_(
                    func.lower(Task.title).like(f"%{lowered}%"),
                    func.lower(func.coalesce(Task.description, "")).like(f"%{lowered}%"),
                ),
            )
            .order_by(rank, Task.updated_at.desc())
            .limit(1)
        )
        if task is None:
            raise AppError(
                code="RESOURCE_NOT_FOUND",
                message="No matching task was found.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"reference": text},
            )
        return task

    async def mark_task_done_by_reference(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        reference: str,
    ) -> Task:
        task = await self.find_task_by_reference(
            session=session,
            user_id=user_id,
            reference=reference,
        )
        task.status = "done"
        task.completed_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(task)
        return task

    async def list_reminders(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        status_filter: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Reminder], int]:
        filters = [Reminder.user_id == user_id]
        if status_filter is not None:
            filters.append(Reminder.status == self._normalize_reminder_status(status_filter))

        items = (
            await session.scalars(
                select(Reminder)
                .where(*filters)
                .order_by(Reminder.remind_at.asc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
        ).all()
        total = await session.scalar(select(func.count()).select_from(Reminder).where(*filters))
        return list(items), int(total or 0)

    async def create_reminder(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        payload: CreateReminderRequest,
        timezone_name: str | None = None,
    ) -> Reminder:
        reminder = Reminder(
            user_id=user_id,
            task_id=await self._validate_task_id(
                session=session,
                user_id=user_id,
                task_id=payload.task_id,
            ),
            message=payload.message.strip(),
            remind_at=self._parse_required_future_datetime(
                payload.remind_at,
                timezone_name=payload.timezone or timezone_name or "Asia/Kolkata",
                field_name="remind_at",
            ),
            is_recurring=False,
            recurrence_rule=None,
            status="pending",
        )
        reminder.is_recurring, reminder.recurrence_rule = self._normalize_recurrence(
            is_recurring=payload.is_recurring,
            recurrence_rule=payload.recurrence_rule,
            repeat=None,
        )

        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)
        return reminder

    async def create_task_with_reminder(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        title: str,
        remind_at: datetime | str,
        timezone_name: str,
        description: str | None = None,
        priority: str | None = None,
        repeat: str | None = None,
        source: str = "voice",
    ) -> tuple[Task, Reminder]:
        due_date = self._parse_required_future_datetime(
            remind_at,
            timezone_name=timezone_name,
            field_name="trigger_at",
        )

        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=self._clean_optional_text(description),
            priority=self._normalize_priority(priority),
            status="todo",
            due_date=due_date,
            source=source,
        )
        session.add(task)
        await session.flush()

        is_recurring, recurrence_rule = self._normalize_recurrence(
            is_recurring=False,
            recurrence_rule=None,
            repeat=repeat,
        )

        reminder = Reminder(
            user_id=user_id,
            task_id=task.id,
            message=title.strip(),
            remind_at=due_date,
            is_recurring=is_recurring,
            recurrence_rule=recurrence_rule,
            status="pending",
        )
        session.add(reminder)
        await session.commit()
        await session.refresh(task)
        await session.refresh(reminder)
        return task, reminder

    async def update_reminder(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        reminder_id: UUID,
        payload: UpdateReminderRequest,
        timezone_name: str | None = None,
    ) -> Reminder:
        reminder = await self.get_reminder(
            session=session,
            user_id=user_id,
            reminder_id=reminder_id,
        )

        if payload.task_id is not None or (payload.task_id is None and "task_id" in payload.model_fields_set):
            reminder.task_id = await self._validate_task_id(
                session=session,
                user_id=user_id,
                task_id=payload.task_id,
            )

        if payload.remind_at is not None:
            reminder.remind_at = self._parse_required_future_datetime(
                payload.remind_at,
                timezone_name=payload.timezone or timezone_name or "Asia/Kolkata",
                field_name="remind_at",
            )
            reminder.status = "pending"

        if payload.status is not None:
            reminder.status = self._normalize_reminder_status(payload.status)

        if payload.is_recurring is not None or payload.recurrence_rule is not None:
            reminder.is_recurring, reminder.recurrence_rule = self._normalize_recurrence(
                is_recurring=payload.is_recurring,
                recurrence_rule=payload.recurrence_rule,
                repeat=None,
            )

        await session.commit()
        await session.refresh(reminder)
        if payload.remind_at is not None or reminder.status == "dismissed":
            await self.notification_service.clear_reminder_delivery_state(reminder.id)
        return reminder

    async def get_reminder(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        reminder_id: UUID,
    ) -> Reminder:
        reminder = await session.scalar(
            select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
        )
        if reminder is None:
            raise AppError(
                code="RESOURCE_NOT_FOUND",
                message="Reminder not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return reminder

    def serialize_task(self, task: Task) -> dict[str, Any]:
        now = datetime.now(UTC)
        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.due_date,
            "completed_at": task.completed_at,
            "source": task.source,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "is_overdue": self.is_task_overdue(task, now=now),
        }

    def serialize_reminder(
        self,
        reminder: Reminder,
        *,
        updated_at: datetime | None = None,
    ) -> dict[str, Any]:
        return {
            "id": str(reminder.id),
            "message": reminder.message,
            "remind_at": reminder.remind_at,
            "status": reminder.status,
            "is_recurring": reminder.is_recurring,
            "recurrence_rule": reminder.recurrence_rule,
            "task_id": str(reminder.task_id) if reminder.task_id else None,
            "created_at": reminder.created_at,
            "updated_at": updated_at,
        }

    def is_task_overdue(
        self,
        task: Task,
        *,
        now: datetime | None = None,
    ) -> bool:
        effective_now = now or datetime.now(UTC)
        return (
            task.due_date is not None
            and task.due_date < effective_now
            and task.status not in {"done", "cancelled"}
        )

    def next_recurrence_at(
        self,
        *,
        reminder: Reminder,
        base_time: datetime | None = None,
    ) -> datetime | None:
        if not reminder.is_recurring or not reminder.recurrence_rule:
            return None

        anchor = base_time or reminder.remind_at
        rule = reminder.recurrence_rule.strip().lower()
        if rule == "daily":
            return anchor + timedelta(days=1)
        if rule == "weekly":
            return anchor + timedelta(weeks=1)
        raise AppError(
            code="VALIDATION_ERROR",
            message="Unsupported recurrence rule.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"recurrence_rule": reminder.recurrence_rule},
        )

    def _task_order_clause(self, *, sort_by: str, sort_order: str):
        normalized_order = "desc" if sort_order.strip().lower() == "desc" else "asc"
        normalized_sort = sort_by.strip().lower()

        if normalized_sort == "priority":
            priority_rank = case(
                (Task.priority == "urgent", 0),
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                else_=3,
            )
            return priority_rank.desc() if normalized_order == "desc" else priority_rank.asc()

        if normalized_sort not in {"due_date", "created_at", "updated_at"}:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Unsupported task sort field.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"sort_by": sort_by},
            )

        column = getattr(Task, normalized_sort)
        if normalized_order == "desc":
            return column.desc().nulls_last()
        return column.asc().nulls_last()

    def _normalize_priority(self, value: str | None) -> str:
        normalized = (value or "medium").strip().lower()
        aliases = {"normal": "medium"}
        normalized = aliases.get(normalized, normalized)
        if normalized not in {"low", "medium", "high", "urgent"}:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Invalid task priority.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"priority": value},
            )
        return normalized

    def _normalize_task_status(self, value: str) -> str:
        normalized = value.strip().lower()
        aliases = {
            "pending": "todo",
            "completed": "done",
        }
        normalized = aliases.get(normalized, normalized)
        if normalized not in {"todo", "in_progress", "done", "cancelled"}:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Invalid task status.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"status": value},
            )
        return normalized

    def _normalize_reminder_status(self, value: str) -> str:
        normalized = value.strip().lower()
        aliases = {"triggered": "sent", "snoozed": "pending"}
        normalized = aliases.get(normalized, normalized)
        if normalized not in {"pending", "sent", "dismissed"}:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Invalid reminder status.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"status": value},
            )
        return normalized

    def _normalize_recurrence(
        self,
        *,
        is_recurring: bool | None,
        recurrence_rule: str | None,
        repeat: str | None,
    ) -> tuple[bool, str | None]:
        raw_rule = (repeat if repeat is not None else recurrence_rule) or ""
        normalized_rule = raw_rule.strip().lower()

        if not normalized_rule or normalized_rule == "none":
            if is_recurring:
                raise AppError(
                    code="VALIDATION_ERROR",
                    message="Recurring reminders require a recurrence rule.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            return False, None

        if normalized_rule not in {"daily", "weekly"}:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Unsupported recurrence rule.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"recurrence_rule": raw_rule},
            )
        return True, normalized_rule

    def _parse_optional_datetime(
        self,
        value: datetime | str | None,
        *,
        timezone_name: str,
        field_name: str,
        prefer_future: bool,
    ) -> datetime | None:
        if value is None:
            return None
        return parse_user_datetime(
            value,
            timezone_name=timezone_name,
            field_name=field_name,
            prefer_future=prefer_future,
        )

    def _parse_required_future_datetime(
        self,
        value: datetime | str,
        *,
        timezone_name: str,
        field_name: str,
    ) -> datetime:
        parsed = parse_user_datetime(
            value,
            timezone_name=timezone_name,
            field_name=field_name,
            prefer_future=True,
        )
        if parsed <= datetime.now(UTC):
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"{field_name} must be in the future.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"field": field_name, "value": value},
            )
        return parsed

    def _clean_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    async def _validate_task_id(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        task_id: UUID | None,
    ) -> UUID | None:
        if task_id is None:
            return None
        await self.get_task(session=session, user_id=user_id, task_id=task_id)
        return task_id

    async def _sync_task_overdue_flag(self, task: Task) -> None:
        if self.is_task_overdue(task):
            return
        await self.notification_service.clear_overdue_task_flag(task.id)
