# backend/app/db/session.py
"""Async SQLAlchemy engine and session factory."""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config.settings import get_settings


def _asyncpg_url(raw_url: str) -> str:
    """LangGraph's Postgres checkpointer wants a plain 'postgresql://' URL
    (psycopg driver). SQLAlchemy's async engine wants 'postgresql+asyncpg://'.
    We store the plain form in .env and derive this one."""
    return raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)


_settings = get_settings()

if _settings.database_url:
    engine = create_async_engine(_asyncpg_url(_settings.database_url), echo=False, pool_pre_ping=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
else:
    # No DATABASE_URL configured — conversation persistence (api/conversations.py,
    # chat_service._persist_turn) degrades gracefully to a no-op rather than crashing.
    engine = None
    AsyncSessionLocal = None


async def get_db_session() -> AsyncSession:
    """FastAPI dependency: yields a DB session, closes it after the request.
    Raises a clear error if no database is configured."""
    if AsyncSessionLocal is None:
        from app.core.exceptions import DatabaseError
        raise DatabaseError("DATABASE_URL is not configured — cannot access the database")
    async with AsyncSessionLocal() as session:
        yield session
