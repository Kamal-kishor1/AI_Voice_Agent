from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import structlog

from app.core.auth import AuthenticatedUser
from app.schemas.task import CreateReminderRequest, CreateTaskRequest, UpdateTaskRequest
from app.services.tasks_service import TasksService

logger = structlog.get_logger(__name__)


@dataclass(slots=True)
class ToolResult:
    step_id: int
    action: str
    success: bool
    result: Any
    message: str
    confirmation_required: bool = False
    confirmation_preview: str | None = None


_TOOL_HANDLERS: dict[str, Any] = {}


def register_tool(action: str):
    def decorator(func):
        _TOOL_HANDLERS[action] = func
        return func

    return decorator


@register_tool("create_task")
async def handle_create_task(params: dict[str, Any], **kwargs) -> ToolResult:
    session, current_user = _execution_context(kwargs)
    tasks_service = _tasks_service(kwargs)

    payload = CreateTaskRequest(
        title=params.get("title") or params.get("message") or "Untitled task",
        description=params.get("description"),
        priority=params.get("priority"),
        due_date=params.get("due_date") or params.get("due_at") or params.get("trigger_at"),
        timezone=kwargs.get("timezone_name"),
    )
    task = await tasks_service.create_task(
        session=session,
        user_id=current_user.id,
        payload=payload,
        timezone_name=kwargs.get("timezone_name"),
        source=params.get("source", "voice"),
    )
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="create_task",
        success=True,
        result={"task": tasks_service.serialize_task(task)},
        message=f"Task added: {task.title}" + (f" due {task.due_date.isoformat()}" if task.due_date else ""),
    )


@register_tool("create_reminder")
async def handle_create_reminder(params: dict[str, Any], **kwargs) -> ToolResult:
    session, current_user = _execution_context(kwargs)
    tasks_service = _tasks_service(kwargs)

    message = (params.get("message") or params.get("title") or "Reminder").strip()
    trigger_at = (
        params.get("trigger_at")
        or params.get("remind_at")
        or params.get("due_at")
        or params.get("due_date")
    )
    task_id = params.get("task_id")
    repeat = params.get("repeat") or params.get("recurrence_rule")

    if task_id:
        payload = CreateReminderRequest(
            message=message,
            remind_at=trigger_at,
            is_recurring=bool(repeat and str(repeat).strip().lower() != "none"),
            recurrence_rule=repeat,
            task_id=task_id,
            timezone=kwargs.get("timezone_name"),
        )
        reminder = await tasks_service.create_reminder(
            session=session,
            user_id=current_user.id,
            payload=payload,
            timezone_name=kwargs.get("timezone_name"),
        )
        result_payload = {"reminder": tasks_service.serialize_reminder(reminder)}
    else:
        task, reminder = await tasks_service.create_task_with_reminder(
            session=session,
            user_id=current_user.id,
            title=message,
            remind_at=trigger_at,
            timezone_name=kwargs.get("timezone_name") or "Asia/Kolkata",
            description=params.get("description"),
            priority=params.get("priority"),
            repeat=repeat,
            source=params.get("source", "voice"),
        )
        result_payload = {
            "task": tasks_service.serialize_task(task),
            "reminder": tasks_service.serialize_reminder(reminder),
        }

    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="create_reminder",
        success=True,
        result=result_payload,
        message=f"Reminder set: {message}" + (f" for {trigger_at}" if trigger_at else ""),
    )


@register_tool("update_task_status")
async def handle_update_task_status(params: dict[str, Any], **kwargs) -> ToolResult:
    session, current_user = _execution_context(kwargs)
    tasks_service = _tasks_service(kwargs)

    target_status = params.get("status", "done")
    task_id = params.get("task_id")
    reference = params.get("reference") or params.get("query") or params.get("title")

    if task_id:
        task = await tasks_service.update_task(
            session=session,
            user_id=current_user.id,
            task_id=task_id,
            payload=UpdateTaskRequest(
                status=target_status,
                timezone=kwargs.get("timezone_name"),
            ),
            timezone_name=kwargs.get("timezone_name"),
        )
    else:
        task = await tasks_service.find_task_by_reference(
            session=session,
            user_id=current_user.id,
            reference=reference,
            allow_done=True,
        )
        task = await tasks_service.update_task(
            session=session,
            user_id=current_user.id,
            task_id=task.id,
            payload=UpdateTaskRequest(
                status=target_status,
                timezone=kwargs.get("timezone_name"),
            ),
            timezone_name=kwargs.get("timezone_name"),
        )

    human_status = "completed" if task.status == "done" else task.status.replace("_", " ")
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="update_task_status",
        success=True,
        result={"task": tasks_service.serialize_task(task)},
        message=f"Task updated: {task.title} is now {human_status}.",
    )


@register_tool("file_search")
async def handle_file_search(params: dict[str, Any], **kwargs) -> ToolResult:
    query = params.get("query", "")
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="file_search",
        success=True,
        result={"query": query, "results": []},
        message=f"Searching for: {query} (file search not yet implemented)",
    )


@register_tool("send_email")
async def handle_send_email(params: dict[str, Any], **kwargs) -> ToolResult:
    recipient = params.get("recipient", "unknown")
    subject = params.get("subject", "")
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="send_email",
        success=False,
        result={"recipient": recipient},
        message=f"Email to {recipient}: email integration not yet connected.",
        confirmation_required=True,
        confirmation_preview=f'Send email to {recipient}' + (f' - "{subject}"' if subject else ""),
    )


@register_tool("send_whatsapp")
async def handle_send_whatsapp(params: dict[str, Any], **kwargs) -> ToolResult:
    recipient = params.get("recipient", "unknown")
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="send_whatsapp",
        success=False,
        result={"recipient": recipient},
        message=f"WhatsApp to {recipient}: WhatsApp integration not yet connected.",
        confirmation_required=True,
    )


@register_tool("read_calendar")
async def handle_read_calendar(params: dict[str, Any], **kwargs) -> ToolResult:
    date = params.get("date", "today")
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="read_calendar",
        success=True,
        result={"date": date, "events": []},
        message=f"Calendar for {date}: calendar integration not yet connected.",
    )


@register_tool("create_calendar_event")
async def handle_create_calendar_event(params: dict[str, Any], **kwargs) -> ToolResult:
    title = params.get("title", "Meeting")
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="create_calendar_event",
        success=False,
        result={"title": title},
        message=f"Calendar event '{title}': calendar integration not yet connected.",
        confirmation_required=True,
    )


@register_tool("check_availability")
async def handle_check_availability(params: dict[str, Any], **kwargs) -> ToolResult:
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="check_availability",
        success=True,
        result={"available_slots": []},
        message="Availability check: calendar integration not yet connected.",
    )


@register_tool("search_contacts")
async def handle_search_contacts(params: dict[str, Any], **kwargs) -> ToolResult:
    query = params.get("query", params.get("name", ""))
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="search_contacts",
        success=True,
        result={"query": query, "contacts": []},
        message=f"Contact search for '{query}': contacts module not yet ready.",
    )


@register_tool("summarise_text")
async def handle_summarise_text(params: dict[str, Any], **kwargs) -> ToolResult:
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="summarise_text",
        success=True,
        result={"summary": "Summarisation pending implementation."},
        message="Text summarisation will be available in a later phase.",
    )


@register_tool("generate_briefing")
async def handle_generate_briefing(params: dict[str, Any], **kwargs) -> ToolResult:
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="generate_briefing",
        success=True,
        result={"briefing": "Briefing generation pending implementation."},
        message="Morning briefing will be available in a later phase.",
    )


@register_tool("general_chat")
async def handle_general_chat(params: dict[str, Any], **kwargs) -> ToolResult:
    return ToolResult(
        step_id=kwargs.get("step_id", 1),
        action="general_chat",
        success=True,
        result={"type": "chat"},
        message="",
    )


class ToolRouter:
    async def execute_plan(
        self,
        intent: dict[str, Any],
        **context: Any,
    ) -> list[ToolResult]:
        steps = intent.get("steps", [])
        if not steps:
            return []

        results: list[ToolResult] = []
        step_results: dict[int, ToolResult] = {}
        sorted_steps = sorted(steps, key=lambda step: step.get("step_id", 0))

        for step in sorted_steps:
            step_id = step.get("step_id", len(results) + 1)
            action = step.get("action", "unknown")
            params = step.get("params", {})
            depends_on = step.get("depends_on", [])
            confirmation_required = step.get("confirmation_required", False)

            blocked_by_dependency = False
            for dep_id in depends_on:
                dep_result = step_results.get(dep_id)
                if dep_result is None or not dep_result.success:
                    blocked_result = ToolResult(
                        step_id=step_id,
                        action=action,
                        success=False,
                        result=None,
                        message=f"Skipped: dependency step {dep_id} failed or missing.",
                    )
                    results.append(blocked_result)
                    step_results[step_id] = blocked_result
                    blocked_by_dependency = True
                    break

            if blocked_by_dependency:
                continue

            resolved_params = self._resolve_params(params, step_results)
            handler = _TOOL_HANDLERS.get(action)
            if handler is None:
                result = ToolResult(
                    step_id=step_id,
                    action=action,
                    success=False,
                    result=None,
                    message=f"Unknown action: {action}",
                )
            else:
                try:
                    result = await handler(
                        resolved_params,
                        step_id=step_id,
                        **context,
                    )
                    result.confirmation_required = (
                        result.confirmation_required or confirmation_required
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.error(
                        "tool_execution_failed",
                        action=action,
                        step_id=step_id,
                        error=str(exc),
                    )
                    result = ToolResult(
                        step_id=step_id,
                        action=action,
                        success=False,
                        result=None,
                        message=f"Step {step_id} failed: {exc}",
                    )

            results.append(result)
            step_results[step_id] = result

        return results

    def _resolve_params(
        self,
        params: dict[str, Any],
        step_results: dict[int, ToolResult],
    ) -> dict[str, Any]:
        resolved: dict[str, Any] = {}
        for key, value in params.items():
            if isinstance(value, str) and "{{step_" in value:
                import re

                match = re.search(r"\{\{step_(\d+)_result\}\}", value)
                if match:
                    ref_id = int(match.group(1))
                    ref_result = step_results.get(ref_id)
                    if ref_result and ref_result.success:
                        resolved[key] = ref_result.result
                    else:
                        resolved[key] = value
                else:
                    resolved[key] = value
            else:
                resolved[key] = value
        return resolved

    def get_registered_tools(self) -> list[str]:
        return list(_TOOL_HANDLERS.keys())


def _execution_context(
    kwargs: dict[str, Any],
) -> tuple[Any, AuthenticatedUser]:
    session = kwargs.get("session")
    current_user = kwargs.get("current_user")
    if session is None or current_user is None:
        raise RuntimeError("Tool execution requires database session and authenticated user.")
    return session, current_user


def _tasks_service(kwargs: dict[str, Any]) -> TasksService:
    service = kwargs.get("tasks_service")
    if isinstance(service, TasksService):
        return service
    return TasksService()
