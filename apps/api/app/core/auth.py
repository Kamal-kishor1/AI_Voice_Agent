from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import AppError
from app.models.entities import User
from app.services.token_service import TokenPayload, TokenService, get_token_service


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(slots=True)
class AuthenticatedUser:
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    token: TokenPayload


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
    token_service: TokenService = Depends(get_token_service),
) -> AuthenticatedUser:
    if credentials is None:
        raise AppError(
            code="AUTH_TOKEN_MISSING",
            message="Authentication token is missing.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token_payload = await token_service.decode_access_token(credentials.credentials)
    try:
        user_id = UUID(token_payload.sub)
    except ValueError as exc:
        raise AppError(
            code="AUTH_TOKEN_INVALID",
            message="The provided authentication token is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from exc

    user = await session.scalar(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    if user is None:
        raise AppError(
            code="AUTH_TOKEN_INVALID",
            message="The provided authentication token is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    if not user.is_active:
        raise AppError(
            code="ACCOUNT_DISABLED",
            message="This account has been deactivated.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        token=token_payload,
    )


async def require_admin(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    if current_user.role != "admin":
        raise AppError(
            code="FORBIDDEN",
            message="Administrator access is required.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return current_user
