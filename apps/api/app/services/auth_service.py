from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.redis_client import get_redis_client
from app.models.entities import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.oauth_service import OAuthService
from app.services.password_service import hash_password, verify_password
from app.services.token_service import TokenBundle, TokenService


@dataclass(slots=True)
class AuthResult:
    user: User
    tokens: TokenBundle


class AuthService:
    def __init__(self, token_service: TokenService) -> None:
        self.token_service = token_service
        self.redis = get_redis_client()
        self.oauth_service = OAuthService()

    async def register_user(
        self,
        *,
        session: AsyncSession,
        payload: RegisterRequest,
    ) -> User:
        email = payload.email.lower()
        existing_user = await session.scalar(
            select(User).where(func.lower(User.email) == email, User.deleted_at.is_(None))
        )
        if existing_user is not None:
            raise AppError(
                code="EMAIL_ALREADY_EXISTS",
                message="An account with this email already exists.",
                status_code=status.HTTP_409_CONFLICT,
            )

        user = User(
            email=email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name.strip(),
            role="user",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def login_user(
        self,
        *,
        session: AsyncSession,
        payload: LoginRequest,
    ) -> AuthResult:
        email = payload.email.lower()
        await self._enforce_lockout(email)

        user = await session.scalar(
            select(User).where(func.lower(User.email) == email, User.deleted_at.is_(None))
        )
        if user is None or not verify_password(payload.password, user.password_hash):
            await self._register_failed_login(email)
            raise AppError(
                code="INVALID_CREDENTIALS",
                message="Invalid email or password.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            raise AppError(
                code="ACCOUNT_DISABLED",
                message="This account has been deactivated.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        await self._clear_login_failures(email)
        user.last_login_at = datetime.now(UTC)
        await session.commit()

        tokens = await self.token_service.issue_tokens(
            user_id=str(user.id),
            email=user.email,
            name=user.full_name,
            role=user.role,
        )
        return AuthResult(user=user, tokens=tokens)

    async def refresh_tokens(
        self,
        *,
        session: AsyncSession,
        refresh_token: str,
    ) -> AuthResult:
        user_id, tokens = await self.token_service.rotate_refresh_token(refresh_token)
        try:
            user_uuid = UUID(user_id)
        except ValueError as exc:
            raise AppError(
                code="INVALID_REFRESH_TOKEN",
                message="The provided refresh token is invalid or expired.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            ) from exc

        user = await session.scalar(
            select(User).where(User.id == user_uuid, User.deleted_at.is_(None))
        )
        if user is None:
            raise AppError(
                code="INVALID_REFRESH_TOKEN",
                message="The provided refresh token is invalid or expired.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        return AuthResult(user=user, tokens=tokens)

    async def logout_user(
        self,
        *,
        user_id: UUID,
        access_jti: str,
        access_exp: int,
    ) -> None:
        await self.token_service.revoke_access_token_by_claims(access_jti, access_exp)
        await self.token_service.revoke_all_refresh_tokens_for_user(str(user_id))

    async def login_with_google(
        self,
        *,
        session: AsyncSession,
        code: str,
        code_verifier: str,
        redirect_uri: str | None,
    ) -> AuthResult:
        identity, token_data = await self.oauth_service.exchange_google_code(
            code=code,
            code_verifier=code_verifier,
            redirect_uri=redirect_uri,
        )

        user = await session.scalar(
            select(User).where(
                func.lower(User.email) == identity.email.lower(),
                User.deleted_at.is_(None),
            )
        )
        if user is None:
            # Generate a strong random password for OAuth-created local accounts.
            user = User(
                email=identity.email.lower(),
                password_hash=hash_password(f"oauth-{identity.provider_subject}-{datetime.now(UTC).timestamp()}"),
                full_name=identity.full_name,
                role="user",
                is_active=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        elif not user.is_active:
            raise AppError(
                code="ACCOUNT_DISABLED",
                message="This account has been deactivated.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        self.oauth_service.store_google_tokens(user.id, token_data)
        user.last_login_at = datetime.now(UTC)
        await session.commit()

        tokens = await self.token_service.issue_tokens(
            user_id=str(user.id),
            email=user.email,
            name=user.full_name,
            role=user.role,
        )
        return AuthResult(user=user, tokens=tokens)

    async def _enforce_lockout(self, email: str) -> None:
        lock_key = f"auth:login_lock:{email}"
        is_locked = await self.redis.exists(lock_key)
        if is_locked:
            raise AppError(
                code="ACCOUNT_LOCKED",
                message="Too many failed login attempts. Try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

    async def _register_failed_login(self, email: str) -> None:
        fail_key = f"auth:login_fail:{email}"
        attempts = await self.redis.incr(fail_key)
        await self.redis.expire(fail_key, 15 * 60)
        if attempts >= 5:
            await self.redis.setex(f"auth:login_lock:{email}", 30 * 60, "1")

    async def _clear_login_failures(self, email: str) -> None:
        await self.redis.delete(f"auth:login_fail:{email}")
        await self.redis.delete(f"auth:login_lock:{email}")
