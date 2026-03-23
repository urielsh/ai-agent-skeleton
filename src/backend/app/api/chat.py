"""Chat endpoint — send a message and receive orchestrator response."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.connection import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.redis_client import get_redis
from app.services.session_manager import SessionManager, SessionNotFoundError
from app.services.orchestrator import run_orchestrator

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


@router.post(
    "/sessions/{session_id}/chat",
    response_model=ChatResponse,
)
async def send_message(
    session_id: uuid.UUID,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    t0 = time.monotonic()

    mgr = SessionManager(db, get_redis())

    try:
        await mgr.get_session(session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save user message
    await mgr.add_message(session_id, "user", body.message)

    # Get current state
    draft = await mgr.get_current_draft(session_id)
    messages = await mgr.get_messages(session_id)
    history = [{"role": m.role, "content": m.content} for m in messages[:-1]]

    # Run orchestrator
    try:
        result = await run_orchestrator(
            body.message,
            history,
            draft,
            prompt_version=settings.prompt_version,
        )
    except Exception as exc:
        logger.exception("Orchestrator failed for session %s", session_id)
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")

    # Apply draft updates
    if result.get("draft_updates"):
        draft = await mgr.merge_draft(session_id, result["draft_updates"])

    # Save assistant reply
    await mgr.add_message(session_id, "assistant", result["reply"])

    elapsed_ms = round((time.monotonic() - t0) * 1000, 1)
    response = ChatResponse(
        session_id=str(session_id),
        reply=result["reply"],
        draft_input=draft,
        missing_fields=result.get("missing_fields", []),
        next_questions=result.get("next_questions", []),
    )

    json_response = JSONResponse(content=response.model_dump(mode="json"))
    json_response.headers["X-Response-Time-Ms"] = str(elapsed_ms)
    json_response.headers["X-SLA-Target-Ms"] = str(settings.chat_sla_sec * 1000)
    return json_response
