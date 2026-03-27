"""AI Model Router — Single abstraction for all AI model calls (F048).

Reads `ai_mode` from user preferences at call time (hot-switchable).
Free mode → Ollama (Mistral 7B primary, LLaMA 3.1 8B fallback).
Paid mode → Anthropic Claude (primary), OpenAI GPT-4o (fallback).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

import httpx
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------

OLLAMA_MODELS = ["mistral:7b-instruct-v0.3-q4_K_M", "llama3.1:8b"]
OLLAMA_FALLBACK_MODELS = ["mistral:latest", "mistral:7b", "llama3.1:latest"]

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
OPENAI_MODEL = "gpt-4o"


@dataclass(slots=True)
class AIResponse:
    """Unified response from the AI Model Router."""

    content: str
    model: str
    provider: str  # "ollama" | "anthropic" | "openai"
    mode: str  # "free" | "paid"
    tokens_used: int | None = None
    latency_ms: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


class AIRouter:
    """The single abstraction layer through which ALL AI model calls flow."""

    def __init__(self) -> None:
        self.settings = get_settings()

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    async def generate(
        self,
        *,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_format: str = "json",
        mode: str | None = None,
    ) -> AIResponse:
        """Generate a response from the active AI provider.

        Args:
            prompt: The user-role message content.
            system: The system-role message content.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.
            response_format: "json" | "text" — hint for structured output.
            mode: Explicit mode override ("free" | "paid"). If None, uses
                  the value from Settings (default "free").

        Returns:
            AIResponse with content, model metadata, and timing.
        """
        active_mode = mode or getattr(self.settings, "ai_mode", "free")

        if active_mode == "paid":
            return await self._generate_paid(
                prompt=prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
            )
        return await self._generate_free(
            prompt=prompt,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

    async def generate_stream(
        self,
        *,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        mode: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream tokens from the active AI provider (for SSE chat)."""
        active_mode = mode or getattr(self.settings, "ai_mode", "free")

        if active_mode == "paid":
            async for chunk in self._stream_paid(
                prompt=prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                yield chunk
        else:
            async for chunk in self._stream_free(
                prompt=prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                yield chunk

    # -----------------------------------------------------------------------
    # Free mode — Ollama
    # -----------------------------------------------------------------------

    async def _generate_free(
        self,
        *,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
        response_format: str,
    ) -> AIResponse:
        ollama_url = getattr(self.settings, "ollama_base_url", "http://localhost:11434")
        all_models = OLLAMA_MODELS + OLLAMA_FALLBACK_MODELS
        last_error: Exception | None = None

        for model in all_models:
            started = time.perf_counter()
            try:
                payload: dict[str, Any] = {
                    "model": model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                }
                if response_format == "json":
                    payload["format"] = "json"

                async with httpx.AsyncClient(timeout=120) as client:
                    resp = await client.post(f"{ollama_url}/api/generate", json=payload)

                if resp.status_code >= 400:
                    logger.warning(
                        "ollama_model_failed",
                        model=model,
                        status=resp.status_code,
                        body=resp.text[:300],
                    )
                    last_error = RuntimeError(f"Ollama {model}: HTTP {resp.status_code}")
                    continue

                data = resp.json()
                latency = round((time.perf_counter() - started) * 1000, 2)
                content = data.get("response", "").strip()
                tokens = data.get("eval_count")

                logger.info(
                    "ai_generate_success",
                    provider="ollama",
                    model=model,
                    latency_ms=latency,
                    tokens=tokens,
                )
                return AIResponse(
                    content=content,
                    model=model,
                    provider="ollama",
                    mode="free",
                    tokens_used=tokens,
                    latency_ms=latency,
                    raw=data,
                )

            except Exception as exc:  # noqa: BLE001
                logger.warning("ollama_model_error", model=model, error=str(exc))
                last_error = exc
                continue

        logger.error("all_free_models_failed")
        raise RuntimeError(
            f"All free-mode models failed. Last error: {last_error}"
        )

    async def _stream_free(
        self,
        *,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        ollama_url = getattr(self.settings, "ollama_base_url", "http://localhost:11434")
        all_models = OLLAMA_MODELS + OLLAMA_FALLBACK_MODELS

        for model in all_models:
            try:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "system": system,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                }
                async with httpx.AsyncClient(timeout=120) as client:
                    async with client.stream(
                        "POST", f"{ollama_url}/api/generate", json=payload
                    ) as resp:
                        if resp.status_code >= 400:
                            continue
                        async for line in resp.aiter_lines():
                            if not line.strip():
                                continue
                            try:
                                chunk = json.loads(line)
                                token = chunk.get("response", "")
                                if token:
                                    yield token
                                if chunk.get("done"):
                                    return
                            except json.JSONDecodeError:
                                continue
                return
            except Exception:  # noqa: BLE001
                continue

        yield "[Error: All free-mode models unavailable]"

    # -----------------------------------------------------------------------
    # Paid mode — Anthropic → OpenAI fallback
    # -----------------------------------------------------------------------

    async def _generate_paid(
        self,
        *,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
        response_format: str,
    ) -> AIResponse:
        # Try Anthropic first
        anthropic_key = getattr(self.settings, "anthropic_api_key", None)
        if anthropic_key:
            try:
                result = await self._call_anthropic(
                    prompt=prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return result
            except Exception as exc:  # noqa: BLE001
                logger.warning("anthropic_failed", error=str(exc))

        # Fallback to OpenAI
        openai_key = getattr(self.settings, "openai_api_key", None)
        if openai_key:
            try:
                result = await self._call_openai(
                    prompt=prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                )
                return result
            except Exception as exc:  # noqa: BLE001
                logger.warning("openai_failed", error=str(exc))

        # Both paid failed → fall back to free mode
        logger.warning("paid_mode_fallback_to_free")
        return await self._generate_free(
            prompt=prompt,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

    async def _call_anthropic(
        self,
        *,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
    ) -> AIResponse:
        started = time.perf_counter()
        headers = {
            "x-api-key": self.settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": ANTHROPIC_MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )

        if resp.status_code >= 400:
            raise RuntimeError(f"Anthropic API error: {resp.status_code} {resp.text[:300]}")

        data = resp.json()
        latency = round((time.perf_counter() - started) * 1000, 2)
        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block["text"]

        tokens = data.get("usage", {}).get("output_tokens")
        logger.info(
            "ai_generate_success",
            provider="anthropic",
            model=ANTHROPIC_MODEL,
            latency_ms=latency,
            tokens=tokens,
        )
        return AIResponse(
            content=content.strip(),
            model=ANTHROPIC_MODEL,
            provider="anthropic",
            mode="paid",
            tokens_used=tokens,
            latency_ms=latency,
            raw=data,
        )

    async def _call_openai(
        self,
        *,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
        response_format: str,
    ) -> AIResponse:
        started = time.perf_counter()
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )

        if resp.status_code >= 400:
            raise RuntimeError(f"OpenAI API error: {resp.status_code} {resp.text[:300]}")

        data = resp.json()
        latency = round((time.perf_counter() - started) * 1000, 2)
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("completion_tokens")
        logger.info(
            "ai_generate_success",
            provider="openai",
            model=OPENAI_MODEL,
            latency_ms=latency,
            tokens=tokens,
        )
        return AIResponse(
            content=content.strip(),
            model=OPENAI_MODEL,
            provider="openai",
            mode="paid",
            tokens_used=tokens,
            latency_ms=latency,
            raw=data,
        )

    async def _stream_paid(
        self,
        *,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        """Stream from Anthropic, fallback to OpenAI, then free mode."""
        anthropic_key = getattr(self.settings, "anthropic_api_key", None)
        if anthropic_key:
            try:
                async for chunk in self._stream_anthropic(
                    prompt=prompt, system=system, temperature=temperature, max_tokens=max_tokens
                ):
                    yield chunk
                return
            except Exception:  # noqa: BLE001
                pass

        openai_key = getattr(self.settings, "openai_api_key", None)
        if openai_key:
            try:
                async for chunk in self._stream_openai(
                    prompt=prompt, system=system, temperature=temperature, max_tokens=max_tokens
                ):
                    yield chunk
                return
            except Exception:  # noqa: BLE001
                pass

        # Fallback to free mode stream
        async for chunk in self._stream_free(
            prompt=prompt, system=system, temperature=temperature, max_tokens=max_tokens
        ):
            yield chunk

    async def _stream_anthropic(
        self,
        *,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        headers = {
            "x-api-key": self.settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": ANTHROPIC_MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST", "https://api.anthropic.com/v1/messages",
                headers=headers, json=payload,
            ) as resp:
                if resp.status_code >= 400:
                    raise RuntimeError(f"Anthropic stream error: {resp.status_code}")
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        return
                    try:
                        event = json.loads(data_str)
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {})
                            text = delta.get("text", "")
                            if text:
                                yield text
                    except json.JSONDecodeError:
                        continue

    async def _stream_openai(
        self,
        *,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST", "https://api.openai.com/v1/chat/completions",
                headers=headers, json=payload,
            ) as resp:
                if resp.status_code >= 400:
                    raise RuntimeError(f"OpenAI stream error: {resp.status_code}")
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        return
                    try:
                        event = json.loads(data_str)
                        delta = event["choices"][0].get("delta", {})
                        text = delta.get("content", "")
                        if text:
                            yield text
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
