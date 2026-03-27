"""Command & Chat routes — Phase 3 Intelligence endpoints.

POST /v1/command  → Intent parse + tool execution
POST /v1/chat     → Streaming chat via SSE
POST /v1/session/clear → Clear session context
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.database import get_db_session
from app.core.responses import success_response
from app.schemas.command import (
    ChatRequest,
    CommandRequest,
    CommandResponse,
    IntentMeta,
    StepResult,
)
from app.services.ai_router import AIRouter
from app.services.intent_parser import IntentParser
from app.services.preference_service import PreferenceService
from app.services.session_service import SessionService
from app.services.tasks_service import TasksService
from app.services.tool_router import ToolRouter

router = APIRouter(prefix="/v1", tags=["intelligence"])


def _ai_router() -> AIRouter:
    return AIRouter()


def _intent_parser(ai_router: AIRouter = Depends(_ai_router)) -> IntentParser:
    return IntentParser(ai_router=ai_router)


def _tool_router() -> ToolRouter:
    return ToolRouter()


def _session_service() -> SessionService:
    return SessionService()


def _preference_service() -> PreferenceService:
    return PreferenceService()


def _tasks_service() -> TasksService:
    return TasksService()


# ---------------------------------------------------------------------------
# POST /v1/command — Parse intent + execute tools
# ---------------------------------------------------------------------------


@router.post("/command")
async def process_command(
    request: Request,
    payload: CommandRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    intent_parser: IntentParser = Depends(_intent_parser),
    tool_router: ToolRouter = Depends(_tool_router),
    preference_service: PreferenceService = Depends(_preference_service),
    session_service: SessionService = Depends(_session_service),
    tasks_service: TasksService = Depends(_tasks_service),
):
    """Process a user command: parse intent → execute tools → respond."""

    resolved_mode = await preference_service.resolve_ai_mode(
        session=session,
        user_id=current_user.id,
        mode_override=payload.mode,
    )

    # 1. Parse intent
    intent = await intent_parser.parse(
        user_input=payload.input,
        session_id=payload.session_id,
        user_timezone=payload.timezone,
        mode=resolved_mode,
    )

    # 2. Store user turn in session context
    await session_service.add_turn(
        session_id=payload.session_id,
        role="user",
        content=payload.input,
    )

    # 3. Extract metadata
    meta_raw = intent.pop("_meta", {})
    meta = IntentMeta(
        provider=meta_raw.get("provider", "unknown"),
        model=meta_raw.get("model", "unknown"),
        mode=meta_raw.get("mode", "unknown"),
        latency_ms=meta_raw.get("latency_ms"),
        tokens_used=meta_raw.get("tokens_used"),
    )

    # 4. If ambiguous, return clarifying question
    if intent.get("ambiguity_score", 0) > 0.4:
        question = intent.get("clarifying_question", "Could you clarify?")

        # Store assistant turn
        await session_service.add_turn(
            session_id=payload.session_id,
            role="assistant",
            content=question,
        )

        return success_response(
            request=request,
            data=CommandResponse(
                intent_type=intent.get("intent_type", "clarification_needed"),
                confidence=intent.get("confidence", 0.0),
                ambiguity_score=intent.get("ambiguity_score", 0.0),
                steps=[],
                entities=intent.get("entities", {}),
                clarifying_question=question,
                session_context_used=intent.get("session_context_used", False),
                tool_results=[],
                assistant_message=question,
                meta=meta,
            ).model_dump(),
        )

    # 5. Execute the plan via Tool Router
    tool_results_raw = await tool_router.execute_plan(
        intent,
        session=session,
        current_user=current_user,
        timezone_name=payload.timezone,
        session_id=payload.session_id,
        tasks_service=tasks_service,
    )
    tool_results = [
        StepResult(
            step_id=r.step_id,
            action=r.action,
            success=r.success,
            result=r.result,
            message=r.message,
            confirmation_required=r.confirmation_required,
            confirmation_preview=r.confirmation_preview,
        )
        for r in tool_results_raw
    ]

    # 6. Build assistant message from tool results
    assistant_message = _build_assistant_message(intent, tool_results_raw)

    # 7. Store assistant turn in session context
    await session_service.add_turn(
        session_id=payload.session_id,
        role="assistant",
        content=assistant_message,
        metadata=_build_session_metadata(intent=intent, results=tool_results_raw),
    )

    return success_response(
        request=request,
        data=CommandResponse(
            intent_type=intent.get("intent_type", "single_action"),
            confidence=intent.get("confidence", 0.0),
            ambiguity_score=intent.get("ambiguity_score", 0.0),
            steps=intent.get("steps", []),
            entities=intent.get("entities", {}),
            clarifying_question=None,
            session_context_used=intent.get("session_context_used", False),
            tool_results=tool_results,
            assistant_message=assistant_message,
            meta=meta,
        ).model_dump(),
    )


# ---------------------------------------------------------------------------
# POST /v1/chat — Streaming chat via SSE
# ---------------------------------------------------------------------------


@router.post("/chat")
@router.post("/chat/stream")
async def chat_stream(
    payload: ChatRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    ai_router: AIRouter = Depends(_ai_router),
    preference_service: PreferenceService = Depends(_preference_service),
    session_service: SessionService = Depends(_session_service),
):
    """Streaming chat endpoint using Server-Sent Events."""

    # Store user message in session
    await session_service.add_turn(
        session_id=payload.session_id,
        role="user",
        content=payload.message,
    )

    # Get session context for the system prompt
    context_str = await session_service.get_context_string(payload.session_id)

    system = payload.system or (
        "You are Alex, a personal AI assistant. You are calm, competent, "
        "and efficient. Keep responses concise. Never start with 'Sure!' "
        "or 'Of course!'. Be direct and helpful.\n\n"
        f"Recent conversation context:\n{context_str}"
    )
    resolved_mode = await preference_service.resolve_ai_mode(
        session=session,
        user_id=current_user.id,
        mode_override=payload.mode,
    )

    async def event_generator():
        full_response: list[str] = []
        try:
            async for token in ai_router.generate_stream(
                prompt=payload.message,
                system=system,
                mode=resolved_mode,
            ):
                full_response.append(token)
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"data: {json.dumps({'type': 'error', 'content': str(exc)})}\n\n"

        # Store assistant response in session
        complete_text = "".join(full_response)
        if complete_text:
            await session_service.add_turn(
                session_id=payload.session_id,
                role="assistant",
                content=complete_text,
            )

        yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# POST /v1/session/clear — Clear session context
# ---------------------------------------------------------------------------


@router.post("/session/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_session(
    request: Request,
    session_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session_service: SessionService = Depends(_session_service),
):
    """Clear session context ('Start over')."""
    await session_service.clear_context(session_id)


# ---------------------------------------------------------------------------
# GET /v1/ai/status — Check AI provider availability
# ---------------------------------------------------------------------------


@router.get("/ai/status")
async def ai_status(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    preference_service: PreferenceService = Depends(_preference_service),
):
    """Return AI provider availability status."""
    import httpx

    settings = AIRouter().settings
    resolved_mode = await preference_service.resolve_ai_mode(
        session=session,
        user_id=current_user.id,
    )

    status_data: dict[str, Any] = {
        "active_mode": resolved_mode,
        "providers": {},
    }

    # Check Ollama
    ollama_url = getattr(settings, "ollama_base_url", "http://localhost:11434")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{ollama_url}/api/tags")
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                status_data["providers"]["ollama"] = {
                    "status": "connected",
                    "url": ollama_url,
                    "models": models,
                }
            else:
                status_data["providers"]["ollama"] = {"status": "error", "url": ollama_url}
    except Exception:  # noqa: BLE001
        status_data["providers"]["ollama"] = {"status": "disconnected", "url": ollama_url}

    # Check paid providers
    status_data["providers"]["anthropic"] = {
        "status": "configured" if getattr(settings, "anthropic_api_key", None) else "not_configured",
    }
    status_data["providers"]["openai"] = {
        "status": "configured" if getattr(settings, "openai_api_key", None) else "not_configured",
    }

    return success_response(request=request, data=status_data)


# ---------------------------------------------------------------------------
# GET /v1/ai/tools — List registered tool actions
# ---------------------------------------------------------------------------


@router.get("/ai/tools")
async def list_tools(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    tool_router: ToolRouter = Depends(_tool_router),
):
    """Return list of registered tool actions."""
    return success_response(
        request=request,
        data={"tools": tool_router.get_registered_tools()},
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_assistant_message(
    intent: dict[str, Any],
    results: list,
) -> str:
    """Build a concise assistant response from tool execution results."""
    if not results:
        return "Done."

    messages: list[str] = []
    for r in results:
        if r.message:
            messages.append(r.message)

    if not messages:
        return "Done."

    return " ".join(messages)


def _build_session_metadata(
    *,
    intent: dict[str, Any],
    results: list,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {"intent_type": intent.get("intent_type")}
    task_refs: list[dict[str, Any]] = []
    reminder_refs: list[dict[str, Any]] = []

    for result in results:
        if not isinstance(result.result, dict):
            continue

        task = result.result.get("task")
        if isinstance(task, dict) and task.get("id"):
            task_refs.append({"id": task.get("id"), "title": task.get("title")})

        reminder = result.result.get("reminder")
        if isinstance(reminder, dict) and reminder.get("id"):
            reminder_refs.append(
                {
                    "id": reminder.get("id"),
                    "message": reminder.get("message"),
                    "task_id": reminder.get("task_id"),
                }
            )

    if task_refs:
        metadata["task_refs"] = task_refs[-3:]
    if reminder_refs:
        metadata["reminder_refs"] = reminder_refs[-3:]
    return metadata
