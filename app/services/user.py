"""User service: business rules for users."""

from collections.abc import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EmailAlreadyExistsError
from app.models.user import User, UserRole
from app.repositories import user as user_repo


async def create_user(
    session: AsyncSession,
    *,
    name: str,
    email: str,
    role: UserRole,
) -> User:
    """Create a user, enforcing that the email is unique.

    Uniqueness is guarded twice on purpose:
    1. A friendly pre-check (`get_by_email`) for the common case.
    2. Catching the DB's IntegrityError as the *authoritative*, race-proof
       guarantee -- another request could insert the same email between our
       check and our insert (a TOCTOU race). Only the unique constraint can
       truly prevent that.
    """
    if await user_repo.get_by_email(session, email) is not None:
        raise EmailAlreadyExistsError(f"A user with email '{email}' already exists.")

    try:
        user = await user_repo.create(session, name=name, email=email, role=role)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise EmailAlreadyExistsError(
            f"A user with email '{email}' already exists."
        ) from None
    return user


async def list_users(
    session: AsyncSession, *, limit: int = 20, offset: int = 0
) -> tuple[Sequence[User], int]:
    return await user_repo.list_(session, limit=limit, offset=offset)
