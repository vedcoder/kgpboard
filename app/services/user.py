"""User service: business rules for users."""

from collections.abc import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories import user as user_repo


async def create_user(
    session: AsyncSession,
    *,
    name: str,
    email: str,
    password: str,
    role: UserRole = UserRole.student,
) -> User:
    """Register a user (default role: student), enforcing unique email.

    The plaintext password is hashed here and never stored raw. Uniqueness is
    guarded twice: a friendly pre-check, plus catching the DB's IntegrityError
    as the race-proof backstop.
    """
    if await user_repo.get_by_email(session, email) is not None:
        raise EmailAlreadyExistsError(f"A user with email '{email}' already exists.")

    try:
        user = await user_repo.create(
            session,
            name=name,
            email=email,
            role=role,
            password_hash=hash_password(password),
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise EmailAlreadyExistsError(
            f"A user with email '{email}' already exists."
        ) from None
    return user


async def authenticate_user(
    session: AsyncSession, *, email: str, password: str
) -> User:
    """Return the user if email+password are correct, else raise.

    The same error is raised whether the email is unknown or the password is
    wrong -- so an attacker can't tell which emails exist (no user enumeration).
    """
    user = await user_repo.get_by_email(session, email)
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Incorrect email or password.")
    return user


async def list_users(
    session: AsyncSession, *, limit: int = 20, offset: int = 0
) -> tuple[Sequence[User], int]:
    return await user_repo.list_(session, limit=limit, offset=offset)
