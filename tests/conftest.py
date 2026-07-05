"""Pytest fixtures: an isolated Postgres test database + HTTP client.

Strategy:
- Use a dedicated `kgpboard_test` database, built once from the models.
- Give each test its own engine with NullPool. Every async test runs on its
  own event loop; NullPool ensures no connection is reused across loops (which
  is what causes "attached to a different loop" errors).
- Override the app's `get_session` so requests hit the test DB.
- Truncate all tables after each test, keeping tests independent.
"""

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.models  # noqa: F401  -- register models on Base.metadata
from app.api.deps import get_session
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.base import Base
from app.main import app
from app.models.user import UserRole
from app.services import user as user_service

# Rate limiting is process-global in-memory state; disable it under test so
# many requests across tests don't trip the limit. It's verified separately.
limiter.enabled = False

# Same server as dev, but a dedicated database name.
TEST_URL = make_url(settings.database_url).set(database="kgpboard_test")
_TEST_URL_STR = TEST_URL.render_as_string(hide_password=False)

# Created once per test session (lazily, inside the first test's loop).
_schema_ready = False


async def _create_test_database() -> None:
    """(Re)create an empty kgpboard_test database."""
    conn = await asyncpg.connect(
        host=TEST_URL.host,
        port=TEST_URL.port or 5432,
        user=TEST_URL.username,
        password=TEST_URL.password,
        database="postgres",  # maintenance DB
    )
    await conn.execute("DROP DATABASE IF EXISTS kgpboard_test")
    await conn.execute("CREATE DATABASE kgpboard_test")
    await conn.close()


@pytest_asyncio.fixture
async def engine():
    """A per-test engine (NullPool). Builds the DB + schema once, lazily."""
    global _schema_ready
    if not _schema_ready:
        await _create_test_database()
        tmp = create_async_engine(_TEST_URL_STR, poolclass=NullPool)
        async with tmp.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await tmp.dispose()
        _schema_ready = True

    eng = create_async_engine(_TEST_URL_STR, poolclass=NullPool)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine):
    """A raw session for fixtures/tests that touch the DB directly."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(engine):
    """After every test, wipe all rows so tests stay independent."""
    yield
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE users, notices, events CASCADE"))


@pytest_asyncio.fixture
async def client(engine):
    """HTTP client wired to the app, with get_session pointed at the test DB."""
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def _get_test_session():
        async with factory() as s:
            yield s

    app.dependency_overrides[get_session] = _get_test_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def _login(client: AsyncClient, email: str, password: str) -> dict[str, str]:
    resp = await client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    token = resp.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client, session) -> dict[str, str]:
    """Create an admin and return an Authorization header for them."""
    await user_service.create_user(
        session, name="Admin", email="admin@test.com",
        password="adminpass1", role=UserRole.admin,
    )
    return await _login(client, "admin@test.com", "adminpass1")


@pytest_asyncio.fixture
async def student_headers(client) -> dict[str, str]:
    """Register a student via the public API and return their auth header."""
    await client.post(
        "/users",
        json={"name": "Ravi", "email": "ravi@test.com", "password": "studentpass1"},
    )
    return await _login(client, "ravi@test.com", "studentpass1")
