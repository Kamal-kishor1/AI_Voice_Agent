from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import dateparser

from app.core.exceptions import AppError


_WEEKDAY_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def parse_user_datetime(
    value: Any,
    *,
    timezone_name: str,
    field_name: str,
    prefer_future: bool = True,
) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"{field_name} cannot be empty.",
                status_code=400,
            )

        parsed = _parse_weekday_phrase(
            text,
            timezone_name=timezone_name,
            prefer_future=prefer_future,
        )
        if parsed is None:
            parsed = dateparser.parse(
                text,
                settings={
                    "TIMEZONE": timezone_name,
                    "TO_TIMEZONE": "UTC",
                    "RETURN_AS_TIMEZONE_AWARE": True,
                    "PREFER_DATES_FROM": "future" if prefer_future else "current_period",
                    "RELATIVE_BASE": datetime.now(_safe_zoneinfo(timezone_name)),
                },
            )
        if parsed is None:
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"Unable to parse {field_name}.",
                status_code=400,
                details={"field": field_name, "value": value},
            )
    else:
        raise AppError(
            code="VALIDATION_ERROR",
            message=f"{field_name} must be a datetime or string.",
            status_code=400,
        )

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_safe_zoneinfo(timezone_name))
    return parsed.astimezone(UTC)


def _safe_zoneinfo(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except Exception:  # noqa: BLE001
        return ZoneInfo("UTC")


def _parse_weekday_phrase(
    text: str,
    *,
    timezone_name: str,
    prefer_future: bool,
) -> datetime | None:
    match = re.fullmatch(
        (
            r"(?:(this|next)\s+)?"
            r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
            r"(?:\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm))?"
        ),
        text,
        re.IGNORECASE,
    )
    if match is None:
        return None

    qualifier = (match.group(1) or "").lower()
    weekday_name = match.group(2).lower()
    hour_text = match.group(3)
    minute_text = match.group(4)
    meridiem = (match.group(5) or "").lower()
    if hour_text is None:
        return None

    hour = int(hour_text) % 12
    minute = int(minute_text or "0")
    if meridiem == "pm":
        hour += 12

    tz = _safe_zoneinfo(timezone_name)
    now_local = datetime.now(tz)
    days_ahead = (_WEEKDAY_INDEX[weekday_name] - now_local.weekday()) % 7
    if qualifier == "next":
        days_ahead = 7 if days_ahead == 0 else days_ahead + 7
    elif prefer_future and days_ahead == 0 and (hour, minute) <= (now_local.hour, now_local.minute):
        days_ahead = 7

    target_date = (now_local + timedelta(days=days_ahead)).date()
    return datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        hour,
        minute,
        tzinfo=tz,
    )
