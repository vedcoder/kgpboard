"""User data access."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


async def create(
    session: AsyncSession,
    *,
    name: str,
    email: str,
    role: UserRole,
) -> User:
    """Insert a new user and return it (with id/created_at populated)."""
    user = User(name=name, email=email, role=role)
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


async def list_all(session: AsyncSession) -> Sequence[User]:
    """Return all users, newest first."""
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()
