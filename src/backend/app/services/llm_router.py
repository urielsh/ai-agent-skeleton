"""Multi-provider LLM abstraction layer with retry logic."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

from app.config import get_settings
from app.deps import get_http_client

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS_CODES = {429, 502, 503, 529}


class LLMError(Exception):
    """Raised when an LLM call fails after retries."""

    def __init__(self, message: str, *, provider: str = "", retryable: bool = False):
        super().__init__(message)
        self.provider = provider
        self.retryable = retryable


def _is_retryable(status_code: int, body: str) -> bool:
    if status_code in _RETRYABLE_STATUS_CODES:
        return True
    if status_code == 400 and "overloaded" in body.lower():
        return True
    return False


def _parse_retry_after(headers: dict) -> float | None:
    val = headers.get("retry-after")
    if val:
        try:
            return float(val)
        except ValueError:
            pass
    return None


class LLMRouter:
    """Unified interface for calling LLMs (Anthropic / OpenAI)."""

    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def provider(self) -> str:
        return self._settings.llm_provider.lower()

    def _get_model(self) -> str:
        if self.provider == "anthropic":
            return self._settings.anthropic_chat_model
        return self._settings.openai_chat_model

    async def call_chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        *,
        max_tokens: int = 2048,
    ) -> str:
        """Call the configured LLM provider and return the text response."""
        if self.provider == "anthropic":
            return await self._call_anthropic(system_prompt, messages, max_tokens)
        return await self._call_openai(system_prompt, messages, max_tokens)

    async def _call_anthropic(
        self, system_prompt: str, messages: list[dict[str, str]], max_tokens: int
    ) -> str:
        model = self._settings.anthropic_chat_model
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages,
            "temperature": self._settings.llm_temperature,
            "top_p": self._settings.llm_top_p,
        }
        headers = {
            "x-api-key": self._settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = await self._retry_http_post(
            "https://api.anthropic.com/v1/messages",
            payload,
            headers,
            provider="anthropic",
        )
        return body["content"][0]["text"]

    async def _call_openai(
        self, system_prompt: str, messages: list[dict[str, str]], max_tokens: int
    ) -> str:
        model = self._settings.openai_chat_model
        all_messages = [{"role": "system", "content": system_prompt}] + messages
        payload = {
            "model": model,
            "messages": all_messages,
            "max_tokens": max_tokens,
            "temperature": self._settings.llm_temperature,
            "top_p": self._settings.llm_top_p,
            "frequency_penalty": self._settings.llm_frequency_penalty,
        }
        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        body = await self._retry_http_post(
            "https://api.openai.com/v1/chat/completions",
            payload,
            headers,
            provider="openai",
        )
        return body["choices"][0]["message"]["content"]

    async def _retry_http_post(
        self,
        url: str,
        payload: dict,
        headers: dict,
        *,
        provider: str,
    ) -> dict:
        """POST with exponential backoff on transient errors."""
        client = get_http_client()
        max_attempts = 1 + self._settings.llm_retry_max
        last_error: Exception | None = None

        for attempt in range(max_attempts):
            try:
                response = await client.post(url, json=payload, headers=headers)
                body_text = response.text

                if response.status_code == 200:
                    return response.json()

                if _is_retryable(response.status_code, body_text) and attempt < max_attempts - 1:
                    retry_after = _parse_retry_after(dict(response.headers))
                    delay = retry_after or (self._settings.llm_retry_base_sec * (2 ** attempt))
                    logger.warning(
                        "%s returned %d (attempt %d/%d), retrying in %.1fs",
                        provider, response.status_code, attempt + 1, max_attempts, delay,
                    )
                    await asyncio.sleep(delay)
                    continue

                raise LLMError(
                    f"{provider} returned {response.status_code}: {body_text[:200]}",
                    provider=provider,
                )

            except LLMError:
                raise
            except Exception as exc:
                last_error = exc
                if attempt < max_attempts - 1:
                    delay = self._settings.llm_retry_base_sec * (2 ** attempt)
                    logger.warning(
                        "%s request failed (attempt %d/%d): %s, retrying in %.1fs",
                        provider, attempt + 1, max_attempts, exc, delay,
                    )
                    await asyncio.sleep(delay)
                    continue

        raise LLMError(
            f"{provider} request failed after {max_attempts} attempts: {last_error}",
            provider=provider,
            retryable=True,
        )


def extract_json_from_llm_response(text: str) -> dict[str, Any]:
    """Extract JSON object from LLM response text, handling markdown fences."""
    # Try direct JSON parse first
    text = text.strip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # Try extracting from markdown code fence
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Fallback: find first { ... } block
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return {}
