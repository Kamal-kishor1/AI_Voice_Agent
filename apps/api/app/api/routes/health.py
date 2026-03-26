from fastapi import APIRouter, Depends, Request

from app.core.auth import AuthenticatedUser, require_admin
from app.core.responses import success_response
from app.schemas.health import HealthCheckResponse
from app.services.health_service import get_admin_health_payload, get_public_health


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    return await get_public_health()


@router.get("/v1/admin/health")
async def admin_health_check(
    request: Request,
    _: AuthenticatedUser = Depends(require_admin),
):
    payload = await get_admin_health_payload()
    return success_response(request=request, data=payload)
