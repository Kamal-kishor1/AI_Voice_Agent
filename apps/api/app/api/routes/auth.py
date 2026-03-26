from datetime import UTC

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.database import get_db_session
from app.core.responses import error_response, success_response
from app.schemas.auth import (
    GoogleExchangeRequest,
    LoginRequest,
    OnboardingTokenExchangeRequest,
    RefreshTokenRequest,
    RegisterRequest,
)
from app.services.auth_service import AuthService
from app.services.token_service import TokenService, get_token_service


router = APIRouter(prefix="/v1/auth", tags=["auth"])
public_router = APIRouter(tags=["auth"])


def _user_summary(user) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
    }


def _auth_service(
    token_service: TokenService = Depends(get_token_service),
) -> AuthService:
    return AuthService(token_service=token_service)


@router.post("/register")
async def register_user(
    request: Request,
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(_auth_service),
):
    user = await auth_service.register_user(session=session, payload=payload)
    return success_response(
        request=request,
        data={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "created_at": user.created_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/login")
async def login_user(
    request: Request,
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(_auth_service),
):
    result = await auth_service.login_user(session=session, payload=payload)
    return success_response(
        request=request,
        data={
            "access_token": result.tokens.access_token,
            "refresh_token": result.tokens.refresh_token,
            "token_type": result.tokens.token_type,
            "expires_in": result.tokens.expires_in,
            "user": _user_summary(result.user),
        },
    )


@router.post("/refresh")
async def refresh_token(
    request: Request,
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(_auth_service),
):
    result = await auth_service.refresh_tokens(
        session=session,
        refresh_token=payload.refresh_token,
    )
    return success_response(
        request=request,
        data={
            "access_token": result.tokens.access_token,
            "refresh_token": result.tokens.refresh_token,
            "token_type": result.tokens.token_type,
            "expires_in": result.tokens.expires_in,
            "user": _user_summary(result.user),
        },
    )


@router.post("/logout")
async def logout_user(
    current_user: AuthenticatedUser = Depends(get_current_user),
    auth_service: AuthService = Depends(_auth_service),
):
    await auth_service.logout_user(
        user_id=current_user.id,
        access_jti=current_user.token.jti,
        access_exp=current_user.token.exp,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/oauth/google/authorize")
async def google_oauth_authorize(
    request: Request,
    code_challenge: str,
    state: str,
    redirect_uri: str | None = None,
    auth_service: AuthService = Depends(_auth_service),
):
    url = auth_service.oauth_service.build_google_authorize_url(
        redirect_uri=redirect_uri,
        code_challenge=code_challenge,
        state=state,
    )
    return success_response(request=request, data={"authorize_url": url})


@router.post("/oauth/google/exchange")
@router.post("/oauth/google/callback")
async def google_oauth_exchange(
    request: Request,
    payload: GoogleExchangeRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(_auth_service),
):
    result = await auth_service.login_with_google(
        session=session,
        code=payload.code,
        code_verifier=payload.code_verifier,
        redirect_uri=payload.redirect_uri,
    )
    return success_response(
        request=request,
        data={
            "access_token": result.tokens.access_token,
            "refresh_token": result.tokens.refresh_token,
            "token_type": result.tokens.token_type,
            "expires_in": result.tokens.expires_in,
            "user": _user_summary(result.user),
        },
    )


@router.post("/onboarding/token-exchange")
async def onboarding_token_exchange(
    request: Request,
    payload: OnboardingTokenExchangeRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(_auth_service),
):
    if payload.provider.lower() != "google":
        return error_response(
            request=request,
            code="PROVIDER_NOT_SUPPORTED",
            message="Only Google OAuth token exchange is supported in phase 2.",
            details={"provider": payload.provider},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    result = await auth_service.login_with_google(
        session=session,
        code=payload.code,
        code_verifier=payload.code_verifier,
        redirect_uri=payload.redirect_uri,
    )
    return success_response(
        request=request,
        data={
            "provider": "google",
            "access_token": result.tokens.access_token,
            "refresh_token": result.tokens.refresh_token,
            "token_type": result.tokens.token_type,
            "expires_in": result.tokens.expires_in,
            "user": _user_summary(result.user),
        },
    )


@router.get("/.well-known/jwks.json")
async def jwks(token_service: TokenService = Depends(get_token_service)) -> dict:
    return token_service.get_jwks()


@public_router.get("/.well-known/jwks.json")
async def public_jwks(token_service: TokenService = Depends(get_token_service)) -> dict:
    return token_service.get_jwks()
