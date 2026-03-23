"""Health check endpoint."""

import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.models.schemas import DependencyHealth, HealthResponse
from app.services.redis_client import get_redis

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check database and Redis connectivity."""
    # Database check
    db_health = DependencyHealth(status="unhealthy")
    try:
        t0 = time.monotonic()
        await db.execute(text("SELECT 1"))
        db_health = DependencyHealth(
            status="healthy",
            latency_ms=round((time.monotonic() - t0) * 1000, 1),
        )
    except Exception:
        pass

    # Redis check
    redis_health = DependencyHealth(status="not_configured")
    redis = get_redis()
    if redis:
        try:
            t0 = time.monotonic()
            await redis.ping()
            redis_health = DependencyHealth(
                status="healthy",
                latency_ms=round((time.monotonic() - t0) * 1000, 1),
            )
        except Exception:
            redis_health = DependencyHealth(status="unhealthy")

    overall = "healthy" if db_health.status == "healthy" else "degraded"
    return HealthResponse(status=overall, database=db_health, redis=redis_health)
