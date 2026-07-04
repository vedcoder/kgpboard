"""Async database engine and session factory.

- `engine`: one long-lived object per process. It owns the connection pool to
  Postgres. Created once, shared everywhere.
- `AsyncSessionLocal`: a factory that hands out short-lived `AsyncSession`
  objects -- one per request/unit-of-work. A session is your staging area for
  reads and writes; you commit or roll it back, then throw it away.
- `get_session`: an async generator we'll later plug into FastAPI's dependency
  injection so each request gets its own session that is always closed.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,  # set True to log every SQL statement -- handy while learning
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # keep attribute values usable after commit()
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a session, guaranteeing it is closed when the caller is done."""
    async with AsyncSessionLocal() as session:
        yield session
