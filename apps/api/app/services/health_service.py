from time import monotonic

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.database import ping_database


STARTED_AT = monotonic()


async def get_public_health() -> dict[str, str]:
    database_ok = await ping_database()
    return {
        "status": "healthy" if database_ok else "degraded",
        "db": "connected" if database_ok else "disconnected",
    }


async def get_admin_health_payload() -> dict[str, object]:
    settings = get_settings()
    database_ok = await ping_database()
    redis_ok = await _ping_redis(settings.redis_url)

    return {
        "status": "healthy" if database_ok and redis_ok else "degraded",
        "uptime_seconds": int(monotonic() - STARTED_AT),
        "services": {
            "database": "ok" if database_ok else "down",
            "redis": "ok" if redis_ok else "down",
            "api": "ok",
            "worker": "unknown",
            "beat": "unknown",
        },
        "version": settings.app_version,
    }


async def _ping_redis(redis_url: str) -> bool:
    client = Redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    try:
        return bool(await client.ping())
    except Exception:
        return False
    finally:
        await client.aclose()
