"""Redis connection management with graceful degradation."""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

_redis_client = None


def _log_redis_failure(operation: str, key: str, exc: Exception) -> None:
    logger.warning("Redis %s failed for %s: %s", operation, key, exc)


async def init_redis(redis_url: str) -> Any | None:
    """Initialize Redis connection. Returns None if unavailable."""
    global _redis_client
    if not redis_url:
        logger.info("Redis URL not configured — running without cache")
        return None
    try:
        import redis.asyncio as aioredis
        _redis_client = aioredis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
        )
        await _redis_client.ping()
        logger.info("Redis connected: %s", redis_url.split("@")[-1])
        return _redis_client
    except Exception as exc:
        logger.warning("Redis unavailable — degrading to DB-only: %s", exc)
        _redis_client = None
        return None


async def close_redis() -> None:
    """Close Redis connection on shutdown."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


def get_redis() -> Any | None:
    """Return the current Redis client (or None if unavailable)."""
    return _redis_client


async def redis_get_json(key: str) -> dict | None:
    """Get a JSON value from Redis. Returns None on miss or error."""
    if not _redis_client:
        return None
    try:
        raw = await _redis_client.get(key)
        if raw:
            return json.loads(raw)
    except Exception as exc:
        _log_redis_failure("get", key, exc)
    return None


async def redis_set_json(key: str, value: Any, ttl_seconds: int = 86400) -> bool:
    """Set a JSON value in Redis with TTL. Returns True on success."""
    if not _redis_client:
        return False
    try:
        await _redis_client.set(key, json.dumps(value), ex=ttl_seconds)
        return True
    except Exception as exc:
        _log_redis_failure("set", key, exc)
        return False
