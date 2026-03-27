"""Intent Parser — Converts user text into structured intent objects (F047).

Uses the AI Model Router to classify user input via the prompt templates
defined in AI_INSTRUCTIONS.md §4.2–4.4.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import structlog

from app.core.datetime_parser import parse_user_datetime
from app.services.ai_router import AIRouter
from app.services.session_service import SessionService

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates (from AI_INSTRUCTIONS.md §4.2–4.4)
# ---------------------------------------------------------------------------

SINGLE_INTENT_SYSTEM = """You are Alex's Intent Parser. Your job is to convert a user command
into a structured JSON intent object. You must return ONLY valid JSON
matching the schema below. No explanation. No preamble. No markdown.

Schema:
{
  "intent_type": "single_action",
  "confidence": float (0.0–1.0),
  "ambiguity_score": float (0.0–1.0),
  "steps": [
    {
      "step_id": 1,
      "action": string (one of: file_search, send_email, send_whatsapp,
                create_task, create_reminder, read_calendar,
                create_calendar_event, check_availability,
                summarise_text, generate_briefing, search_contacts,
                general_chat),
      "params": object,
      "depends_on": [],
      "confirmation_required": boolean
    }
  ],
  "entities": {
    "contacts": array of strings,
    "files": array of strings,
    "dates": array of ISO8601 strings,
    "times": array of strings,
    "tone": string or null,
    "duration_minutes": integer or null
  },
  "session_context_used": boolean,
  "clarifying_question": null
}

Rules:
- confirmation_required is true for: send_email, send_whatsapp,
  create_calendar_event, and any step that sends data externally.
- confirmation_required is false for: create_task, create_reminder,
  file_search, read_calendar, search_contacts, general_chat.
- ambiguity_score > 0.4 means the command is unclear. Set
  clarifying_question to the single most important question.
  Do not populate steps if ambiguity_score > 0.4.
- Use session_context to resolve pronouns and references.
- If the user input is conversational or general (e.g. "hello", "how are you"),
  use action "general_chat" with intent_type "single_action"."""


MULTI_INTENT_SYSTEM = """You are Alex's Multi-Intent Parser. Parse the user's compound command
into an ordered sequence of steps with dependency declarations.
Return ONLY valid JSON. No explanation. No markdown.

Schema:
{
  "intent_type": "multi_step",
  "confidence": float,
  "ambiguity_score": float,
  "steps": [
    {
      "step_id": integer,
      "action": string,
      "params": object,
      "depends_on": array of step_ids,
      "confirmation_required": boolean,
      "output_key": string (snake_case label for this step's result)
    }
  ],
  "entities": {
    "contacts": array of strings,
    "files": array of strings,
    "dates": array of ISO8601 strings,
    "times": array of strings,
    "tone": string or null,
    "duration_minutes": integer or null
  },
  "session_context_used": boolean,
  "clarifying_question": string or null
}

Template variable syntax:
- Use "{{step_N_result}}" to reference a prior step's output.

Rules:
- Maximum 5 steps in a single plan.
- Identify which steps are truly sequential vs. which could run
  independently. Mark independent steps with depends_on: [].
- confirmation_required: true on any plan containing an external action.
- If ambiguity_score > 0.4, return clarifying_question only."""


CLARIFICATION_SYSTEM = """You are Alex's Clarification Engine. The user's command is ambiguous.
Identify the single most important piece of missing information.
Generate exactly one short question (maximum 20 words) that, if answered,
would allow full intent resolution.

Rules:
- Ask about the MOST CRITICAL unknown only.
- Never ask compound questions ("Who and when?").
- Never ask for information available in session context.
- Phrase as a natural spoken question, not a form label.
- Prefer binary or short-answer questions over open-ended ones.

Return only the question text. No JSON. No preamble."""


# Multi-action keywords for routing to multi-intent prompt
_MULTI_INDICATORS = re.compile(
    r"\b(and then|then|also|after that|next|finally|first|second)\b",
    re.IGNORECASE,
)

_WEEKDAY_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


class IntentParser:
    """Transforms raw user text into structured intent objects."""

    def __init__(self, ai_router: AIRouter | None = None) -> None:
        self.ai_router = ai_router or AIRouter()
        self.session_service = SessionService()

    async def parse(
        self,
        *,
        user_input: str,
        session_id: str,
        user_timezone: str = "Asia/Kolkata",
        mode: str | None = None,
    ) -> dict[str, Any]:
        """Parse user input into an intent object.

        Returns the intent object dict. If ambiguity_score > 0.4,
        clarifying_question is populated and steps is empty.
        """
        context_turns = await self.session_service.get_context(session_id)
        context_str = self._context_string_from_turns(context_turns)
        now = datetime.now(UTC).isoformat()
        prioritized_heuristic = self._prioritized_heuristic_intent(
            user_input=user_input,
            context_str=context_str,
            context_turns=context_turns,
            user_timezone=user_timezone,
        )
        if prioritized_heuristic is not None:
            prioritized_heuristic["_meta"] = {
                "provider": "heuristic",
                "model": "local",
                "mode": mode or "free",
            }
            return prioritized_heuristic

        # Determine which system prompt to use
        is_multi = bool(_MULTI_INDICATORS.search(user_input))
        system_prompt = MULTI_INTENT_SYSTEM if is_multi else SINGLE_INTENT_SYSTEM

        # Build the user prompt
        user_prompt = (
            f'Command: "{user_input}"\n'
            f"Session context (last 5 turns): {context_str}\n"
            f"Current datetime: {now}\n"
            f"User timezone: {user_timezone}"
        )

        # Call the AI Model Router
        try:
            response = await self.ai_router.generate(
                prompt=user_prompt,
                system=system_prompt,
                temperature=0.2,
                max_tokens=1500,
                response_format="json",
                mode=mode,
            )
        except RuntimeError as exc:
            logger.error("intent_parse_ai_call_failed", error=str(exc))
            heuristic = self._heuristic_parse(
                user_input=user_input,
                context_str=context_str,
                context_turns=context_turns,
                user_timezone=user_timezone,
            )
            heuristic["_meta"] = {"provider": "heuristic", "model": "local", "mode": mode or "free"}
            return heuristic

        # Parse the JSON response
        intent = self._extract_json(response.content)
        if intent is None:
            logger.warning(
                "intent_parse_json_failed",
                raw=response.content[:500],
            )
            # Retry once with a stricter prompt
            try:
                response = await self.ai_router.generate(
                    prompt=user_prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No other text.",
                    system=system_prompt,
                    temperature=0.1,
                    max_tokens=1500,
                    response_format="json",
                    mode=mode,
                )
                intent = self._extract_json(response.content)
            except RuntimeError:
                pass

        if intent is None:
            heuristic = self._heuristic_parse(
                user_input=user_input,
                context_str=context_str,
                context_turns=context_turns,
                user_timezone=user_timezone,
            )
            heuristic["_meta"] = {
                "provider": "heuristic",
                "model": "local",
                "mode": mode or "free",
            }
            return heuristic

        intent = self._normalize_intent(intent)
        # Enrich with provider metadata
        intent["_meta"] = {
            "provider": response.provider,
            "model": response.model,
            "mode": response.mode,
            "latency_ms": response.latency_ms,
            "tokens_used": response.tokens_used,
        }

        # Handle ambiguity — generate clarifying question if needed
        if intent.get("ambiguity_score", 0) > 0.4 and not intent.get("clarifying_question"):
            question = await self._generate_clarifying_question(
                user_input=user_input,
                context_str=context_str,
                intent=intent,
                mode=mode,
            )
            intent["clarifying_question"] = question
            intent["steps"] = []
            intent["intent_type"] = "clarification_needed"

        return intent

    async def _generate_clarifying_question(
        self,
        *,
        user_input: str,
        context_str: str,
        intent: dict[str, Any],
        mode: str | None,
    ) -> str:
        """Use the clarification prompt to generate a targeted question."""
        entities = intent.get("entities", {})
        known = {k: v for k, v in entities.items() if v}
        unknown_hint = "Unable to determine from context"

        user_prompt = (
            f'Ambiguous command: "{user_input}"\n'
            f"Session context: {context_str}\n"
            f"Known entities: {json.dumps(known)}\n"
            f"Unknown entities causing ambiguity: {unknown_hint}"
        )

        try:
            response = await self.ai_router.generate(
                prompt=user_prompt,
                system=CLARIFICATION_SYSTEM,
                temperature=0.3,
                max_tokens=100,
                response_format="text",
                mode=mode,
            )
            return response.content.strip().strip('"')
        except RuntimeError:
            return "Could you give me a bit more detail?"

    def _extract_json(self, text: str) -> dict[str, Any] | None:
        """Extract a JSON object from the AI response text."""
        # Try direct parse first
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON in markdown code block
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find first { ... } block
        start = text.find("{")
        if start != -1:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start : i + 1])
                        except json.JSONDecodeError:
                            break
        return None

    def _fallback_error_intent(self, user_input: str) -> dict[str, Any]:
        """Return a safe fallback intent when parsing fails."""
        return {
            "intent_type": "clarification_needed",
            "confidence": 0.5,
            "ambiguity_score": 0.6,
            "steps": [],
            "entities": {
                "contacts": [],
                "files": [],
                "dates": [],
                "times": [],
                "tone": None,
                "duration_minutes": None,
            },
            "session_context_used": False,
            "clarifying_question": "I didn't quite catch that. Could you rephrase?",
            "_meta": {"provider": "fallback", "model": "none", "mode": "error"},
        }

    def _heuristic_parse(
        self,
        *,
        user_input: str,
        context_str: str,
        context_turns: list[dict[str, Any]],
        user_timezone: str,
    ) -> dict[str, Any]:
        lowered = user_input.strip().lower()

        task_status_intent = self._heuristic_task_status_intent(
            user_input=user_input,
            context_str=context_str,
            context_turns=context_turns,
        )
        if task_status_intent is not None:
            return task_status_intent

        if self._is_ambiguous_pronoun_command(lowered, context_str):
            return {
                "intent_type": "clarification_needed",
                "confidence": 0.88,
                "ambiguity_score": 0.82,
                "steps": [],
                "entities": self._empty_entities(),
                "session_context_used": not self._is_context_empty(context_str),
                "clarifying_question": "Who should I send it to?",
            }

        if "remind me" in lowered:
            reminder_intent = self._heuristic_reminder_intent(
                user_input=user_input,
                user_timezone=user_timezone,
                context_str=context_str,
            )
            if reminder_intent is not None:
                return reminder_intent

        return self._fallback_error_intent(user_input)

    def _prioritized_heuristic_intent(
        self,
        *,
        user_input: str,
        context_str: str,
        context_turns: list[dict[str, Any]],
        user_timezone: str,
    ) -> dict[str, Any] | None:
        task_status_intent = self._heuristic_task_status_intent(
            user_input=user_input,
            context_str=context_str,
            context_turns=context_turns,
        )
        if task_status_intent is not None:
            return task_status_intent

        if user_input.strip().lower().startswith("remind me"):
            return self._heuristic_reminder_intent(
                user_input=user_input,
                user_timezone=user_timezone,
                context_str=context_str,
            )

        return None

    def _heuristic_task_status_intent(
        self,
        *,
        user_input: str,
        context_str: str,
        context_turns: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        explicit_match = re.search(
            r"\b(?:mark|complete|finish)\s+(?:the\s+)?(.+?)\s+task\s+(?:as\s+)?(done|completed)\b",
            user_input,
            re.IGNORECASE,
        )
        pronoun_match = re.search(
            r"\b(?:mark|complete|finish)\s+(?:it|that)\s+(?:as\s+)?(done|completed)\b",
            user_input,
            re.IGNORECASE,
        )
        if explicit_match is None and pronoun_match is None:
            return None

        reference = explicit_match.group(1).strip(" .,!") if explicit_match else None
        if reference is None:
            reference = self._latest_task_reference(context_turns)

        if not reference:
            return {
                "intent_type": "clarification_needed",
                "confidence": 0.81,
                "ambiguity_score": 0.63,
                "steps": [],
                "entities": self._empty_entities(),
                "session_context_used": not self._is_context_empty(context_str),
                "clarifying_question": "Which task should I mark as done?",
            }

        return {
            "intent_type": "single_action",
            "confidence": 0.93 if explicit_match else 0.88,
            "ambiguity_score": 0.09 if explicit_match else 0.18,
            "steps": [
                {
                    "step_id": 1,
                    "action": "update_task_status",
                    "params": {
                        "reference": reference,
                        "status": "done",
                    },
                    "depends_on": [],
                    "confirmation_required": False,
                }
            ],
            "entities": self._empty_entities(),
            "session_context_used": not self._is_context_empty(context_str),
            "clarifying_question": None,
        }

    def _heuristic_reminder_intent(
        self,
        *,
        user_input: str,
        user_timezone: str,
        context_str: str,
    ) -> dict[str, Any] | None:
        reminder_match = re.search(r"remind me to\s+(.+)", user_input, re.IGNORECASE)
        if not reminder_match:
            return None

        full_tail = reminder_match.group(1).strip()
        temporal_match = self._extract_temporal_phrase(full_tail)
        if temporal_match is None:
            return {
                "intent_type": "clarification_needed",
                "confidence": 0.75,
                "ambiguity_score": 0.68,
                "steps": [],
                "entities": self._empty_entities(),
                "session_context_used": not self._is_context_empty(context_str),
                "clarifying_question": "What time should I set the reminder for?",
            }

        temporal_phrase = temporal_match.group(0).strip(" ,.")
        try:
            trigger_local = self._parse_heuristic_trigger(
                temporal_phrase=temporal_phrase,
                user_timezone=user_timezone,
            )
        except ValueError:
            return {
                "intent_type": "clarification_needed",
                "confidence": 0.75,
                "ambiguity_score": 0.68,
                "steps": [],
                "entities": self._empty_entities(),
                "session_context_used": not self._is_context_empty(context_str),
                "clarifying_question": "What time should I set the reminder for?",
            }

        trigger_at = trigger_local.isoformat()

        message = full_tail[: temporal_match.start()].strip(" ,.")
        if not message:
            message = re.sub(
                rf"{re.escape(temporal_phrase)}$",
                "",
                full_tail,
                flags=re.IGNORECASE,
            ).strip(" ,.") or full_tail

        contact_match = re.search(r"\bcall\s+([A-Za-z][A-Za-z'.-]*)\b", message, re.IGNORECASE)
        contacts = [contact_match.group(1)] if contact_match else []

        return {
            "intent_type": "single_action",
            "confidence": 0.96,
            "ambiguity_score": 0.08,
            "steps": [
                {
                    "step_id": 1,
                    "action": "create_reminder",
                    "params": {
                        "message": message,
                        "trigger_at": trigger_at,
                        "repeat": "none",
                    },
                    "depends_on": [],
                    "confirmation_required": False,
                }
            ],
            "entities": {
                "contacts": contacts,
                "files": [],
                "dates": [trigger_local.date().isoformat()],
                "times": [trigger_local.strftime("%H:%M")],
                "tone": None,
                "duration_minutes": None,
            },
            "session_context_used": not self._is_context_empty(context_str),
            "clarifying_question": None,
        }

    def _extract_temporal_phrase(self, text: str) -> re.Match[str] | None:
        return re.search(
            (
                r"\b("
                r"today|tomorrow|tonight|"
                r"this\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
                r"next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
                r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
                r"in\s+\d+\s+(?:minute|minutes|hour|hours|day|days|week|weeks)|"
                r"at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)"
                r")\b.*$"
            ),
            text,
            re.IGNORECASE,
        )

    def _parse_heuristic_trigger(
        self,
        *,
        temporal_phrase: str,
        user_timezone: str,
    ) -> datetime:
        tz = self._resolve_timezone(user_timezone)
        now_local = datetime.now(tz)
        weekday_match = re.search(
            r"\b(?:(this|next)\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            temporal_phrase,
            re.IGNORECASE,
        )
        if weekday_match is None:
            return parse_user_datetime(
                temporal_phrase,
                timezone_name=user_timezone,
                field_name="trigger_at",
                prefer_future=True,
            ).astimezone(tz)

        qualifier = (weekday_match.group(1) or "").lower()
        weekday_name = weekday_match.group(2).lower()
        time_match = re.search(
            r"\b(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b",
            temporal_phrase,
            re.IGNORECASE,
        )
        if time_match is None:
            raise ValueError("Reminder weekday phrases require a time.")

        hour = int(time_match.group(1)) % 12
        minute = int(time_match.group(2) or "0")
        if time_match.group(3).lower() == "pm":
            hour += 12

        days_ahead = (self._weekday_index(weekday_name) - now_local.weekday()) % 7
        if qualifier == "next":
            days_ahead = 7 if days_ahead == 0 else days_ahead + 7
        elif days_ahead == 0 and (hour, minute) <= (now_local.hour, now_local.minute):
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

    def _normalize_intent(self, raw_intent: Any) -> dict[str, Any]:
        if not isinstance(raw_intent, dict):
            return self._fallback_error_intent("")

        entities = raw_intent.get("entities")
        if not isinstance(entities, dict):
            entities = {}

        normalized = {
            "intent_type": str(raw_intent.get("intent_type", "single_action")),
            "confidence": self._safe_float(raw_intent.get("confidence"), default=0.5),
            "ambiguity_score": self._safe_float(raw_intent.get("ambiguity_score"), default=0.5),
            "steps": raw_intent.get("steps") if isinstance(raw_intent.get("steps"), list) else [],
            "entities": {
                "contacts": entities.get("contacts") if isinstance(entities.get("contacts"), list) else [],
                "files": entities.get("files") if isinstance(entities.get("files"), list) else [],
                "dates": entities.get("dates") if isinstance(entities.get("dates"), list) else [],
                "times": entities.get("times") if isinstance(entities.get("times"), list) else [],
                "tone": entities.get("tone"),
                "duration_minutes": entities.get("duration_minutes"),
            },
            "session_context_used": bool(raw_intent.get("session_context_used", False)),
            "clarifying_question": raw_intent.get("clarifying_question"),
        }

        if normalized["ambiguity_score"] > 0.4:
            normalized["intent_type"] = "clarification_needed"
            normalized["steps"] = []
            if not isinstance(normalized["clarifying_question"], str):
                normalized["clarifying_question"] = "Could you clarify what you want me to do?"
        else:
            normalized["clarifying_question"] = None

        return normalized

    def _safe_float(self, value: Any, *, default: float) -> float:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return default
        return max(0.0, min(1.0, parsed))

    def _resolve_timezone(self, user_timezone: str) -> ZoneInfo:
        try:
            return ZoneInfo(user_timezone)
        except Exception:  # noqa: BLE001
            return ZoneInfo("UTC")

    def _empty_entities(self) -> dict[str, Any]:
        return {
            "contacts": [],
            "files": [],
            "dates": [],
            "times": [],
            "tone": None,
            "duration_minutes": None,
        }

    def _context_string_from_turns(self, turns: list[dict[str, Any]]) -> str:
        if not turns:
            return "No prior context in this session."
        parts: list[str] = []
        for turn in turns:
            role = str(turn.get("role", "user")).capitalize()
            content = str(turn.get("content", ""))
            parts.append(f"{role}: {content}")
        return "\n".join(parts)

    def _is_context_empty(self, context_str: str) -> bool:
        return context_str.strip() == "No prior context in this session."

    def _latest_task_reference(self, context_turns: list[dict[str, Any]]) -> str | None:
        for turn in reversed(context_turns):
            metadata = turn.get("metadata")
            if not isinstance(metadata, dict):
                continue
            task_refs = metadata.get("task_refs")
            if not isinstance(task_refs, list):
                continue
            for task_ref in reversed(task_refs):
                if isinstance(task_ref, dict) and isinstance(task_ref.get("title"), str):
                    title = task_ref["title"].strip()
                    if title:
                        return title
        return None

    def _weekday_index(self, weekday_name: str) -> int:
        return _WEEKDAY_INDEX[weekday_name.lower()]

    def _is_ambiguous_pronoun_command(self, lowered_input: str, context_str: str) -> bool:
        if not self._is_context_empty(context_str):
            return False
        has_pronoun = re.search(r"\b(it|him|her|them|that|this)\b", lowered_input) is not None
        has_send_verb = re.search(r"\b(send|share|forward)\b", lowered_input) is not None
        return has_pronoun and has_send_verb
