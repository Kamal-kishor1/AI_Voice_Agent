"""Session context service — short-term memory in Redis (F054).

Stores the last 5 turns of the active conversation session in Redis
with a 30-minute inactivity TTL, enabling pronoun resolution and
follow-up commands.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from app.core.redis_client import get_redis_client

SESSION_TTL_SECONDS = 1800  # 30 minutes
MAX_TURNS = 5


def _session_key(session_id: str) -> str:
    return f"session:{session_id}:context"


class SessionService:
    """Manages per-session conversational context in Redis."""

    def __init__(self) -> None:
        self.redis = get_redis_client()

    async def get_context(self, session_id: str) -> list[dict[str, Any]]:
        """Retrieve the session context (last N turns)."""
        raw = await self.redis.get(_session_key(session_id))
        if raw is None:
            return []
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []

    async def get_context_string(self, session_id: str) -> str:
        """Return context formatted as a prompt-friendly string."""
        turns = await self.get_context(session_id)
        if not turns:
            return "No prior context in this session."
        parts: list[str] = []
        for turn in turns:
            role = turn.get("role", "user").capitalize()
            content = turn.get("content", "")
            parts.append(f"{role}: {content}")
        return "\n".join(parts)

    async def add_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Append a turn to the session context, keeping last MAX_TURNS."""
        turns = await self.get_context(session_id)
        turns.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now(UTC).isoformat(),
                **({"metadata": metadata} if metadata else {}),
            }
        )
        # Keep only the last MAX_TURNS
        if len(turns) > MAX_TURNS:
            turns = turns[-MAX_TURNS:]

        await self.redis.setex(
            _session_key(session_id),
            SESSION_TTL_SECONDS,
            json.dumps(turns),
        )

    async def clear_context(self, session_id: str) -> None:
        """Manual context clear (user says 'Start over')."""
        await self.redis.delete(_session_key(session_id))

    async def get_ttl(self, session_id: str) -> int:
        """Get remaining TTL in seconds for the session."""
        ttl = await self.redis.ttl(_session_key(session_id))
        return max(ttl, 0)
