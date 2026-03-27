from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


TaskStatus = Literal["todo", "in_progress", "done", "cancelled"]
ReminderStatus = Literal["pending", "sent", "dismissed"]


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    priority: str | None = Field(default="medium")
    due_date: datetime | str | None = None
    timezone: str | None = None


class UpdateTaskRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    priority: str | None = None
    status: str | None = None
    due_date: datetime | str | None = None
    timezone: str | None = None


class CreateReminderRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    remind_at: datetime | str
    is_recurring: bool = False
    recurrence_rule: str | None = None
    task_id: UUID | None = None
    timezone: str | None = None


class UpdateReminderRequest(BaseModel):
    status: str | None = None
    remind_at: datetime | str | None = None
    is_recurring: bool | None = None
    recurrence_rule: str | None = None
    task_id: UUID | None = None
    timezone: str | None = None
