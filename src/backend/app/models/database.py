"""SQLAlchemy 2.0 declarative models — 3 tables."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CHAR,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Use JSONB on PostgreSQL, plain JSON elsewhere (e.g. SQLite in tests)
JSONVariant = JSON().with_variant(JSONB, "postgresql")


class Base(DeclarativeBase):
    pass


def _uuid_default() -> uuid.UUID:
    return uuid.uuid4()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=_uuid_default
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )
    draft_input: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    compute_results: Mapped[list["ComputeResult"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_sessions_status", "status"),
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=_uuid_default
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    session: Mapped["Session"] = relationship(back_populates="messages")

    __table_args__ = (
        Index("idx_chat_messages_session", "session_id"),
    )


class ComputeResult(Base):
    __tablename__ = "compute_results"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=_uuid_default
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    input_hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    engine_input: Mapped[dict] = mapped_column(JSONVariant, nullable=False)
    engine_output: Mapped[dict] = mapped_column(JSONVariant, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(20), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    session: Mapped["Session"] = relationship(back_populates="compute_results")

    __table_args__ = (
        Index("idx_compute_results_session", "session_id"),
        Index("idx_compute_results_hash", "input_hash"),
    )
