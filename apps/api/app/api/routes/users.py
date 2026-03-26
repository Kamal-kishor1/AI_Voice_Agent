from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.database import get_db_session
from app.core.responses import success_response
from app.schemas.auth import ChangePasswordRequest, DeleteAccountRequest
from app.schemas.user import UpdateUserProfileRequest
from app.services.token_service import TokenService, get_token_service
from app.services.user_service import UserService


router = APIRouter(prefix="/v1/users", tags=["users"])


def _user_service() -> UserService:
    return UserService()


def _profile_payload(user) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "is_active": user.is_active,
        "last_login_at": user.last_login_at,
        "created_at": user.created_at,
    }


@router.get("/me")
async def get_current_user_profile(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(_user_service),
):
    user = await user_service.get_user_by_id(session=session, user_id=current_user.id)
    return success_response(request=request, data=_profile_payload(user))


@router.patch("/me")
async def update_current_user_profile(
    request: Request,
    payload: UpdateUserProfileRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(_user_service),
):
    user = await user_service.update_profile(
        session=session,
        user_id=current_user.id,
        payload=payload,
    )
    return success_response(
        request=request,
        data={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "updated_at": user.updated_at,
        },
    )


@router.put("/me/password")
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    token_service: TokenService = Depends(get_token_service),
    user_service: UserService = Depends(_user_service),
):
    await user_service.change_password(
        session=session,
        user_id=current_user.id,
        payload=payload,
    )
    await token_service.revoke_all_refresh_tokens_for_user(str(current_user.id))
    return success_response(
        request=request,
        data={"message": "Password updated successfully."},
    )


@router.delete("/me")
async def delete_account(
    request: Request,
    payload: DeleteAccountRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    token_service: TokenService = Depends(get_token_service),
    user_service: UserService = Depends(_user_service),
):
    deletion_date = await user_service.delete_account(
        session=session,
        user_id=current_user.id,
        confirmation=payload.confirmation,
    )
    await token_service.revoke_all_refresh_tokens_for_user(str(current_user.id))
    await token_service.revoke_access_token(current_user.token)
    return success_response(
        request=request,
        data={
            "message": "Account scheduled for deletion. You have 30 days to recover.",
            "deletion_date": deletion_date,
        },
    )
