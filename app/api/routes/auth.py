"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, SessionDep
from app.core.security import create_access_token
from app.schemas.auth import Token
from app.schemas.user import UserRead
from app.services import user as user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    session: SessionDep,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Exchange email + password for an access token.

    Uses the standard OAuth2 password form, so the `username` field carries the
    email. This is what wires up the "Authorize" button in /docs.
    """
    user = await user_service.authenticate_user(
        session, email=form.username, password=form.password
    )
    token = create_access_token(subject=str(user.id), role=user.role.value)
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser) -> UserRead:
    """Return the currently authenticated user (proves the token works)."""
    return current_user
