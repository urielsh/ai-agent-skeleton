"""Session CRUD endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.models.schemas import SessionResponse
from app.services.redis_client import get_redis
from app.services.session_manager import SessionManager, SessionNotFoundError

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _session_response(session) -> SessionResponse:
    return SessionResponse(
        session_id=str(session.id),
        status=session.status,
        draft_input=session.draft_input,
        created_at=session.created_at,
    )


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db, get_redis())
    session = await mgr.create_session()
    return _session_response(session)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db, get_redis())
    try:
        session = await mgr.get_session(session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_response(session)


@router.delete("/{session_id}", response_model=SessionResponse)
async def delete_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db, get_redis())
    try:
        session = await mgr.end_session(session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_response(session)
