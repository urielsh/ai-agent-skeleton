"""Compute endpoint — run the blackbox engine on session draft."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.engine.blackbox import compute
from app.models.database import ComputeResult
from app.models.schemas import ComputeResponse
from app.services.redis_client import get_redis
from app.services.session_manager import (
    SessionManager,
    SessionNotFoundError,
    compute_missing_fields,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["compute"])


@router.post(
    "/sessions/{session_id}/compute",
    response_model=ComputeResponse,
)
async def run_compute(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    mgr = SessionManager(db, get_redis())

    try:
        await mgr.get_session(session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")

    draft = await mgr.get_current_draft(session_id)

    # Check required fields
    missing = compute_missing_fields(draft)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing)}",
        )

    # Check cache by input hash
    input_hash = hashlib.sha256(
        json.dumps(draft, sort_keys=True).encode()
    ).hexdigest()

    cached = await db.execute(
        select(ComputeResult)
        .where(ComputeResult.session_id == session_id)
        .where(ComputeResult.input_hash == input_hash)
    )
    existing = cached.scalar_one_or_none()
    if existing:
        return ComputeResponse(
            session_id=str(session_id),
            score=existing.score,
            label=existing.label,
            summary=existing.engine_output.get("summary", ""),
            breakdown=existing.engine_output.get("breakdown", {}),
            cached=True,
        )

    # Run engine
    engine_output = compute(draft)

    # Persist result
    result = ComputeResult(
        session_id=session_id,
        input_hash=input_hash,
        engine_input=draft,
        engine_output=engine_output,
        score=engine_output["score"],
        label=engine_output["label"],
    )
    db.add(result)
    await db.flush()

    return ComputeResponse(
        session_id=str(session_id),
        score=engine_output["score"],
        label=engine_output["label"],
        summary=engine_output["summary"],
        breakdown=engine_output["breakdown"],
        cached=False,
    )
