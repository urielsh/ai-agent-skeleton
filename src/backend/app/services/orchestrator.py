"""Simplified LLM orchestrator for guided input collection."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.services.llm_router import LLMRouter, extract_json_from_llm_response
from app.services.session_manager import ALL_FIELDS, compute_missing_fields

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_system_prompt(version: str = "1.0") -> str:
    path = _PROMPT_DIR / f"orchestrator_v{version}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    logger.warning("Prompt file not found: %s, using fallback", path)
    return (
        "You are an analysis assistant. Help the user build a structured argument. "
        "Collect: claim, confidence_level (low/medium/high), supporting_reasons (up to 3), "
        "domain, and time_horizon. Return JSON with keys: reply, draft_updates, next_questions."
    )


async def run_orchestrator(
    user_message: str,
    history: list[dict[str, str]],
    current_draft: dict,
    *,
    prompt_version: str = "1.0",
) -> dict[str, Any]:
    """Process a user message through the LLM and return structured response.

    Returns dict with keys: reply, draft_updates, missing_fields, next_questions
    """
    system_prompt = _load_system_prompt(prompt_version)

    # Build context for the LLM
    draft_context = json.dumps(current_draft, indent=2) if current_draft else "{}"
    missing = compute_missing_fields(current_draft)

    augmented_system = (
        f"{system_prompt}\n\n"
        f"Current draft state:\n{draft_context}\n\n"
        f"Missing required fields: {missing}\n"
        f"All fields: {ALL_FIELDS}"
    )

    # Build message list
    messages = list(history) + [{"role": "user", "content": user_message}]

    router = LLMRouter()
    raw_response = await router.call_chat(augmented_system, messages)

    # Parse structured response from LLM
    parsed = extract_json_from_llm_response(raw_response)

    reply = parsed.get("reply", raw_response)
    draft_updates = parsed.get("draft_updates", {})
    next_questions = parsed.get("next_questions", [])

    # Recompute missing fields after applying updates
    merged = dict(current_draft)
    merged.update({k: v for k, v in draft_updates.items() if v is not None})
    new_missing = compute_missing_fields(merged)

    return {
        "reply": reply,
        "draft_updates": draft_updates,
        "missing_fields": new_missing,
        "next_questions": next_questions,
    }
