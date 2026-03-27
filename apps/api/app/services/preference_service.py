from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.entities import UserPreference


class PreferenceService:
    """User preference lookup helpers."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def resolve_ai_mode(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        mode_override: str | None = None,
    ) -> str:
        override = (mode_override or "").strip().lower()
        if override in {"free", "paid"}:
            return override

        raw_value = await self.get_preference(
            session=session,
            user_id=user_id,
            key="ai_mode",
        )
        resolved = self._extract_mode(raw_value)
        if resolved in {"free", "paid"}:
            return resolved

        default_mode = (self.settings.ai_mode or "free").strip().lower()
        return default_mode if default_mode in {"free", "paid"} else "free"

    async def get_preference(
        self,
        *,
        session: AsyncSession,
        user_id: UUID,
        key: str,
    ) -> Any:
        preference = await session.scalar(
            select(UserPreference)
            .where(
                UserPreference.user_id == user_id,
                UserPreference.key == key,
            )
            .order_by(desc(UserPreference.updated_at))
            .limit(1)
        )
        if preference is None:
            return None
        return preference.value

    def _extract_mode(self, value: Any) -> str | None:
        if isinstance(value, str):
            mode = value.strip().lower()
            return mode if mode in {"free", "paid"} else None

        if isinstance(value, dict):
            for candidate_key in ("mode", "value", "ai_mode"):
                candidate = value.get(candidate_key)
                if isinstance(candidate, str):
                    normalized = candidate.strip().lower()
                    if normalized in {"free", "paid"}:
                        return normalized
        return None
