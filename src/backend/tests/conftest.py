"""Shared test fixtures."""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.database import Base


# Force test configuration before app import
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = ""
os.environ["LLM_PROVIDER"] = "anthropic"
os.environ["ANTHROPIC_API_KEY"] = "test-key-not-real"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async SQLite session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an httpx test client with DB initialized via lifespan."""
    from app.config import get_settings
    get_settings.cache_clear()

    # Initialize DB in-memory for the app
    from app.db import connection
    await connection.init_db("sqlite+aiosqlite:///:memory:")
    await connection.create_tables()

    # Set up a no-op Redis
    from app.services import redis_client
    redis_client._redis_client = None

    # Set up httpx client
    import httpx
    from app.deps import set_http_client, clear_http_client
    http_client = httpx.AsyncClient(timeout=10)
    set_http_client(http_client)

    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    await http_client.aclose()
    clear_http_client()
    await connection.close_db()
    get_settings.cache_clear()


@pytest.fixture
def sample_engine_input() -> dict:
    """Sample input for the blackbox engine."""
    return {
        "claim": "Artificial intelligence will transform healthcare delivery within the next decade",
        "confidence_level": "high",
        "supporting_reasons": [
            "AI diagnostic tools have shown accuracy comparable to specialist physicians",
            "Major healthcare providers are investing billions in AI infrastructure",
            "Early deployments show significant cost and time savings",
        ],
        "domain": "healthcare",
        "time_horizon": "next 10 years",
    }
