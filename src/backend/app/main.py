"""FastAPI application factory with lifespan management."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.router import api_router
from app.config import get_settings
from app.middleware import RateLimitMiddleware
from app.db.connection import close_db, create_tables, init_db
from app.deps import clear_http_client, set_http_client
from app.services.redis_client import close_redis, init_redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB, Redis, httpx. Shutdown: close all."""
    settings = get_settings()

    # Initialize database
    await init_db(settings.database_url)
    logger.info("Database initialized: %s", settings.database_url.split("@")[-1])

    # Create tables
    await create_tables()
    logger.info("Database tables created")

    # Initialize Redis (graceful — None if unavailable)
    await init_redis(settings.redis_url)

    # Initialize shared httpx client
    http_client = httpx.AsyncClient(timeout=settings.llm_timeout_sec)
    set_http_client(http_client)
    logger.info("httpx client initialized (timeout=%ss)", settings.llm_timeout_sec)

    # Ensure reports directory exists
    Path(settings.reports_dir).mkdir(parents=True, exist_ok=True)

    yield

    # Shutdown
    await http_client.aclose()
    clear_http_client()
    await close_redis()
    await close_db()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI Agent Skeleton API",
        description="A full-stack AI agent skeleton: INPUT -> LLM + ENGINE -> OUTPUT.",
        version="1.0.0",
        lifespan=lifespan,
    )
    settings = get_settings()
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.rate_limit_per_minute,
    )
    cors_origins = [
        o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()
    ] if settings.cors_allowed_origins else [
        "http://localhost:5173", "http://localhost:3000",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    app.include_router(api_router)
    _register_spa_routes(app)
    return app


def _register_spa_routes(app: FastAPI) -> None:
    """Serve built frontend assets when a production bundle exists."""
    static_dir = Path(__file__).resolve().parent.parent / "static"
    index_path = static_dir / "index.html"
    if not index_path.exists():
        return

    static_root = static_dir.resolve()

    @app.get("/", include_in_schema=False)
    async def spa_root() -> FileResponse:
        return FileResponse(index_path)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        requested = (static_dir / full_path).resolve()
        if requested.is_file() and requested.is_relative_to(static_root):
            return FileResponse(requested)
        return FileResponse(index_path)


app = create_app()
