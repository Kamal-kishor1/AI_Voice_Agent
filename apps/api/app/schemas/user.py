from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    avatar_url: str | None
    role: str
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime


class UserSummary(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: str


class UpdateUserProfileRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    avatar_url: str | None = None
