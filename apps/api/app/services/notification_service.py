from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from app.core.config import get_settings
from app.core.redis_client import get_redis_client


class NotificationService:
    HISTORY_LIMIT = 100
    GLOBAL_HISTORY_KEY = "notifications:history"
    REMINDER_RETRY_ZSET = "notifications:reminder:retries"

    def __init__(self) -> None:
        self.redis = get_redis_client()
        self.settings = get_settings()

    async def publish_event(
        self,
        *,
        user_id: UUID | str,
        event_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        user_key = str(user_id)
        event = {
            "id": f"{event_type}:{user_key}:{int(now.timestamp() * 1000)}",
            "user_id": user_key,
            "event_type": event_type,
            "payload": jsonable_encoder(payload),
            "created_at": now.isoformat(),
        }
        encoded = json.dumps(event)
        history_key = self._user_history_key(user_key)
        channel = self._user_channel(user_key)

        pipeline = self.redis.pipeline()
        pipeline.publish(channel, encoded)
        pipeline.lpush(history_key, encoded)
        pipeline.ltrim(history_key, 0, self.HISTORY_LIMIT - 1)
        pipeline.expire(history_key, self.settings.notification_retention_seconds)
        pipeline.lpush(self.GLOBAL_HISTORY_KEY, encoded)
        pipeline.ltrim(self.GLOBAL_HISTORY_KEY, 0, self.HISTORY_LIMIT - 1)
        pipeline.expire(self.GLOBAL_HISTORY_KEY, self.settings.notification_retention_seconds)
        await pipeline.execute()
        return event

    async def set_reminder_delivery_state(
        self,
        reminder_id: UUID | str,
        *,
        attempts: int,
        last_sent_at: datetime,
        retry_at: datetime | None,
        payload: dict[str, Any],
    ) -> None:
        key = self._reminder_delivery_key(reminder_id)
        state = {
            "attempts": attempts,
            "last_sent_at": last_sent_at.isoformat(),
            "retry_at": retry_at.isoformat() if retry_at else None,
            "payload": jsonable_encoder(payload),
        }
        pipeline = self.redis.pipeline()
        pipeline.setex(
            key,
            self.settings.notification_retention_seconds,
            json.dumps(state),
        )
        if retry_at is not None:
            pipeline.zadd(self.REMINDER_RETRY_ZSET, {str(reminder_id): retry_at.timestamp()})
        else:
            pipeline.zrem(self.REMINDER_RETRY_ZSET, str(reminder_id))
        await pipeline.execute()

    async def get_reminder_delivery_state(
        self,
        reminder_id: UUID | str,
    ) -> dict[str, Any] | None:
        raw = await self.redis.get(self._reminder_delivery_key(reminder_id))
        if raw is None:
            return None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None

    async def pop_due_reminder_retries(
        self,
        *,
        now: datetime,
    ) -> list[str]:
        due_ids = await self.redis.zrangebyscore(
            self.REMINDER_RETRY_ZSET,
            min=0,
            max=now.timestamp(),
        )
        if due_ids:
            await self.redis.zrem(self.REMINDER_RETRY_ZSET, *due_ids)
        return list(due_ids)

    async def clear_reminder_delivery_state(self, reminder_id: UUID | str) -> None:
        await self.redis.delete(self._reminder_delivery_key(reminder_id))
        await self.redis.zrem(self.REMINDER_RETRY_ZSET, str(reminder_id))

    async def was_overdue_task_flagged(self, task_id: UUID | str) -> bool:
        return bool(await self.redis.exists(self._overdue_task_key(task_id)))

    async def mark_overdue_task_flagged(
        self,
        task_id: UUID | str,
        *,
        flagged_at: datetime | None = None,
    ) -> None:
        timestamp = (flagged_at or datetime.now(UTC)).isoformat()
        await self.redis.setex(
            self._overdue_task_key(task_id),
            self.settings.notification_retention_seconds,
            timestamp,
        )

    async def clear_overdue_task_flag(self, task_id: UUID | str) -> None:
        await self.redis.delete(self._overdue_task_key(task_id))

    def _user_channel(self, user_id: str) -> str:
        return f"notifications:user:{user_id}"

    def _user_history_key(self, user_id: str) -> str:
        return f"notifications:user:{user_id}:history"

    def _reminder_delivery_key(self, reminder_id: UUID | str) -> str:
        return f"notifications:reminder:{reminder_id}:delivery"

    def _overdue_task_key(self, task_id: UUID | str) -> str:
        return f"notifications:task:{task_id}:overdue"
