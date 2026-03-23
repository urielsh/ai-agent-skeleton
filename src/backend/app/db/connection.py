"""Async database engine and session factory."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

_async_engine = None
_async_session_factory = None


async def init_db(database_url: str) -> None:
    """Initialize the async engine and session factory."""
    global _async_engine, _async_session_factory
    _async_engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )
    _async_session_factory = async_sessionmaker(
        _async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a database session."""
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_db() -> None:
    """Dispose the engine on shutdown."""
    global _async_engine, _async_session_factory
    if _async_engine:
        await _async_engine.dispose()
    _async_engine = None
    _async_session_factory = None


async def create_tables() -> None:
    """Create all tables defined in the ORM metadata."""
    from app.models.database import Base

    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_engine():
    """Return the current engine (for Alembic migrations)."""
    return _async_engine


def get_session_factory():
    """Return the current async session factory."""
    return _async_session_factory
