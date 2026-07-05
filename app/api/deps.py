"""Shared FastAPI dependencies for route handlers."""

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_session
from app.models.user import User, UserRole
from app.repositories import user as user_repo

# A reusable type alias: annotate a route parameter with `SessionDep` and
# FastAPI injects a fresh AsyncSession per request (from `get_session`), then
# closes it when the request finishes.
SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Tells FastAPI how to read the token (Authorization: Bearer <token>) and wires
# the "Authorize" button in /docs to the login endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Resolve the Bearer token to a real User, or raise 401.

    Authentication only -- it proves *who* you are. Any authenticated user
    (student or admin) passes.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise credentials_error from None

    user = await user_repo.get_by_id(session, user_id)
    if user is None:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_admin(user: CurrentUser) -> User:
    """Authorization gate: passes only if the current user is an admin.

    Builds on get_current_user, so a missing/invalid token still yields 401;
    a valid non-admin yields 403.
    """
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required for this action.",
        )
    return user


AdminUser = Annotated[User, Depends(require_admin)]
