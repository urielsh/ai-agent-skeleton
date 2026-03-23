"""Session lifecycle and draft state management."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import ChatMessage, Session
from app.services.redis_client import redis_get_json, redis_set_json

logger = logging.getLogger(__name__)

# Fields the engine requires to compute
REQUIRED_FIELDS = ["claim", "confidence_level", "supporting_reasons"]
ALL_FIELDS = ["claim", "confidence_level", "supporting_reasons", "domain", "time_horizon"]


class SessionNotFoundError(Exception):
    pass


class SessionManager:
    """Manages session state across Redis (hot) and PostgreSQL (cold)."""

    def __init__(self, db: AsyncSession, redis: Any | None = None):
        self._db = db
        self._redis = redis

    async def create_session(self) -> Session:
        session = Session(id=uuid.uuid4(), status="active", draft_input={})
        self._db.add(session)
        await self._db.flush()
        await redis_set_json(f"draft:{session.id}", {})
        logger.info("Session created: %s", session.id)
        return session

    async def get_session(self, session_id: uuid.UUID) -> Session:
        result = await self._db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise SessionNotFoundError(f"Session {session_id} not found")
        return session

    async def end_session(self, session_id: uuid.UUID) -> Session:
        session = await self.get_session(session_id)
        session.status = "ended"
        await self._db.flush()
        return session

    async def get_current_draft(self, session_id: uuid.UUID) -> dict:
        """Get draft from Redis (hot) with PostgreSQL fallback."""
        cached = await redis_get_json(f"draft:{session_id}")
        if cached is not None:
            return cached
        session = await self.get_session(session_id)
        return session.draft_input or {}

    async def save_draft(self, session_id: uuid.UUID, draft: dict) -> None:
        """Save draft to both Redis and PostgreSQL."""
        await redis_set_json(f"draft:{session_id}", draft)
        session = await self.get_session(session_id)
        session.draft_input = draft
        await self._db.flush()

    async def merge_draft(self, session_id: uuid.UUID, updates: dict) -> dict:
        """Merge updates into the current draft and save."""
        current = await self.get_current_draft(session_id)
        current.update({k: v for k, v in updates.items() if v is not None})
        await self.save_draft(session_id, current)
        return current

    async def add_message(
        self, session_id: uuid.UUID, role: str, content: str
    ) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, role=role, content=content)
        self._db.add(msg)
        await self._db.flush()
        return msg

    async def get_messages(self, session_id: uuid.UUID) -> list[ChatMessage]:
        result = await self._db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        return list(result.scalars().all())


def compute_missing_fields(draft: dict) -> list[str]:
    """Return list of required fields not yet present in the draft."""
    missing = []
    for field in REQUIRED_FIELDS:
        val = draft.get(field)
        if val is None or val == "" or val == []:
            missing.append(field)
    return missing


def merge_drafts(base: dict, updates: dict) -> dict:
    """Merge updates into base draft, skipping None values."""
    merged = dict(base)
    for k, v in updates.items():
        if v is not None:
            merged[k] = v
    return merged
