from __future__ import annotations

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.database import get_db_session
from app.core.responses import paginated_response, success_response
from app.schemas.task import CreateTaskRequest, UpdateTaskRequest
from app.services.tasks_service import TasksService


router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


def _tasks_service() -> TasksService:
    return TasksService()


@router.get("")
async def list_tasks(
    request: Request,
    status_filter: str | None = Query(default=None, alias="status"),
    priority: str | None = Query(default=None),
    sort_by: Literal["due_date", "created_at", "updated_at", "priority"] = "due_date",
    sort_order: Literal["asc", "desc"] = "asc",
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    tasks_service: TasksService = Depends(_tasks_service),
):
    tasks, total = await tasks_service.list_tasks(
        session=session,
        user_id=current_user.id,
        status_filter=status_filter,
        priority=priority,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page,
    )
    return paginated_response(
        request=request,
        data=[tasks_service.serialize_task(task) for task in tasks],
        page=page,
        per_page=per_page,
        total_items=total,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    request: Request,
    payload: CreateTaskRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    tasks_service: TasksService = Depends(_tasks_service),
):
    task = await tasks_service.create_task(
        session=session,
        user_id=current_user.id,
        payload=payload,
        timezone_name=payload.timezone,
    )
    return success_response(
        request=request,
        data=tasks_service.serialize_task(task),
        status_code=status.HTTP_201_CREATED,
    )


@router.patch("/{task_id}")
async def update_task(
    request: Request,
    task_id: UUID,
    payload: UpdateTaskRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    tasks_service: TasksService = Depends(_tasks_service),
):
    task = await tasks_service.update_task(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
        payload=payload,
        timezone_name=payload.timezone,
    )
    return success_response(
        request=request,
        data=tasks_service.serialize_task(task),
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    tasks_service: TasksService = Depends(_tasks_service),
):
    await tasks_service.delete_task(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
