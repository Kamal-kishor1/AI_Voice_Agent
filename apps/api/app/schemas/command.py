"""Request/response schemas for the command endpoint."""

from __future__ import annotations

from typing import Any
from typing import Literal

from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    """POST /v1/command — process a user command."""

    input: str = Field(min_length=1, max_length=5000, description="The user's command text")
    session_id: str = Field(
        min_length=1,
        max_length=100,
        description="Session UUID for context tracking",
    )
    mode: Literal["free", "paid"] | None = Field(
        default=None,
        description='AI mode override: "free" or "paid". Defaults to user preference.',
    )
    timezone: str = Field(
        default="Asia/Kolkata",
        description="User timezone for date/time parsing",
    )


class ChatRequest(BaseModel):
    """POST /v1/chat — streaming chat conversation."""

    message: str = Field(min_length=1, max_length=5000)
    session_id: str = Field(min_length=1, max_length=100)
    mode: Literal["free", "paid"] | None = Field(default=None)
    system: str | None = Field(
        default=None,
        description="Optional system prompt override",
    )


class StepResult(BaseModel):
    """Result of a single tool execution step."""

    step_id: int
    action: str
    success: bool
    result: Any = None
    message: str
    confirmation_required: bool = False
    confirmation_preview: str | None = None


class IntentMeta(BaseModel):
    """AI provider metadata from intent parsing."""

    provider: str
    model: str
    mode: str
    latency_ms: float | None = None
    tokens_used: int | None = None


class CommandResponse(BaseModel):
    """Response body for the command endpoint."""

    intent_type: str
    confidence: float
    ambiguity_score: float
    steps: list[dict[str, Any]] = Field(default_factory=list)
    entities: dict[str, Any] = Field(default_factory=dict)
    clarifying_question: str | None = None
    session_context_used: bool = False
    tool_results: list[StepResult] = Field(default_factory=list)
    assistant_message: str | None = None
    meta: IntentMeta | None = None
