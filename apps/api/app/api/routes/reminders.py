from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.database import get_db_session
from app.core.responses import paginated_response, success_response
from app.schemas.task import CreateReminderRequest, UpdateReminderRequest
from app.services.tasks_service import TasksService


router = APIRouter(prefix="/v1/reminders", tags=["reminders"])


def _tasks_service() -> TasksService:
    return TasksService()


@router.get("")
async def list_reminders(
    request: Request,
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    tasks_service: TasksService = Depends(_tasks_service),
):
    reminders, total = await tasks_service.list_reminders(
        session=session,
        user_id=current_user.id,
        status_filter=status_filter,
        page=page,
        per_page=per_page,
    )
    return paginated_response(
        request=request,
        data=[tasks_service.serialize_reminder(reminder) for reminder in reminders],
        page=page,
        per_page=per_page,
        total_items=total,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_reminder(
    request: Request,
    payload: CreateReminderRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    tasks_service: TasksService = Depends(_tasks_service),
):
    reminder = await tasks_service.create_reminder(
        session=session,
        user_id=current_user.id,
        payload=payload,
        timezone_name=payload.timezone,
    )
    return success_response(
        request=request,
        data=tasks_service.serialize_reminder(reminder),
        status_code=status.HTTP_201_CREATED,
    )


@router.patch("/{reminder_id}")
async def update_reminder(
    request: Request,
    reminder_id: UUID,
    payload: UpdateReminderRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    tasks_service: TasksService = Depends(_tasks_service),
):
    reminder = await tasks_service.update_reminder(
        session=session,
        user_id=current_user.id,
        reminder_id=reminder_id,
        payload=payload,
        timezone_name=payload.timezone,
    )
    return success_response(
        request=request,
        data=tasks_service.serialize_reminder(
            reminder,
            updated_at=datetime.now(UTC),
        ),
    )
