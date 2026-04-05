"""
Asynchronous database session management.
Used by semantic matching endpoints that rely on asyncpg + pgvector.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def _build_async_db_url() -> str:
    db_url = settings.get_database_url()
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return db_url


ASYNC_DATABASE_URL = _build_async_db_url()

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session
