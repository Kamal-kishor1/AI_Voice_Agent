from fastapi import APIRouter

from app.api.routes.auth import public_router as auth_public_router
from app.api.routes.auth import router as auth_router
from app.api.routes.command import router as command_router
from app.api.routes.health import router as health_router
from app.api.routes.reminders import router as reminders_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.users import router as users_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_public_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(command_router)
api_router.include_router(tasks_router)
api_router.include_router(reminders_router)
