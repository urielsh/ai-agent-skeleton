"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# --- Error ---

class ErrorResponse(BaseModel):
    detail: str


# --- Health ---

class DependencyHealth(BaseModel):
    status: str
    latency_ms: float | None = None

class HealthResponse(BaseModel):
    status: str
    database: DependencyHealth
    redis: DependencyHealth


# --- Session ---

class SessionResponse(BaseModel):
    session_id: str
    status: str
    draft_input: dict[str, Any] | None = None
    created_at: datetime | None = None

class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]


# --- Chat ---

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    draft_input: dict[str, Any] | None = None
    missing_fields: list[str] = []
    next_questions: list[str] = []

class ChatMessageSchema(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

class MessageHistoryResponse(BaseModel):
    messages: list[ChatMessageSchema]


# --- Engine ---

class EngineInput(BaseModel):
    claim: str = Field(..., min_length=1)
    confidence_level: str = Field(..., pattern="^(low|medium|high)$")
    supporting_reasons: list[str] = Field(..., min_length=1, max_length=3)
    domain: str = ""
    time_horizon: str = ""

class EngineOutput(BaseModel):
    score: int = Field(..., ge=1, le=10)
    label: str
    summary: str
    breakdown: dict[str, Any]


# --- Compute ---

class ComputeRequest(BaseModel):
    """Optional overrides for compute. Empty body uses session draft."""
    pass

class ComputeResponse(BaseModel):
    session_id: str
    score: int
    label: str
    summary: str
    breakdown: dict[str, Any]
    cached: bool = False
