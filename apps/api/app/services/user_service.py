from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.models.entities import User
from app.schemas.auth import ChangePasswordRequest
from app.schemas.user import UpdateUserProfileRequest
from app.services.password_service import hash_password, verify_password


class UserService:
    async def get_user_by_id(self, *, session: AsyncSession, user_id: UUID) -> User:
        user = await session.scalar(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        if user is None:
            raise AppError(
                code="RESOURCE_NOT_FOUND",
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return user

    async def update_profile(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        payload: UpdateUserProfileRequest,
    ) -> User:
        user = await self.get_user_by_id(session=session, user_id=user_id)
        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url.strip() or None
        await session.commit()
        await session.refresh(user)
        return user

    async def change_password(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        payload: ChangePasswordRequest,
    ) -> None:
        user = await self.get_user_by_id(session=session, user_id=user_id)
        if not verify_password(payload.current_password, user.password_hash):
            raise AppError(
                code="INVALID_CREDENTIALS",
                message="Current password is incorrect.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        user.password_hash = hash_password(payload.new_password)
        await session.commit()

    async def delete_account(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        confirmation: str,
    ) -> datetime:
        if confirmation != "DELETE MY ACCOUNT":
            raise AppError(
                code="VALIDATION_ERROR",
                message="Account deletion confirmation text did not match.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = await self.get_user_by_id(session=session, user_id=user_id)
        user.is_active = False
        user.deleted_at = datetime.now(UTC)
        await session.commit()

        return datetime.now(UTC) + timedelta(days=30)
