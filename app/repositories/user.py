"""User data access."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


async def create(
    session: AsyncSession,
    *,
    name: str,
    email: str,
    role: UserRole,
    password_hash: str,
) -> User:
    """Insert a new user and return it (with id/created_at populated)."""
    user = User(name=name, email=email, role=role, password_hash=password_hash)
    session.add(user)
    await session.flush()  # emit INSERT now; surfaces the unique-email error here
    await session.refresh(user)  # load server defaults (id, created_at)
    return user


async def get_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Fetch a user by primary key, or None if not found."""
    return await session.get(User, user_id)


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    """Fetch a user by email, or None. Used for uniqueness / login checks."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def list_(
    session: AsyncSession,
    *,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[Sequence[User], int]:
    """Return a paginated page of users (newest first) plus the total count.

    `q` filters by email (case-insensitive substring).
    """
    conditions = []
    if q:
        conditions.append(User.email.ilike(f"%{q}%"))

    total = await session.scalar(
        select(func.count()).select_from(User).where(*conditions)
    )
    result = await session.execute(
        select(User)
        .where(*conditions)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all(), total or 0


async def update_role(session: AsyncSession, user: User, role: UserRole) -> User:
    """Set a user's role and persist it."""
    user.role = role
    await session.flush()
    await session.refresh(user)
    return user
