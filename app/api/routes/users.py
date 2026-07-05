"""User endpoints."""

from fastapi import APIRouter, Query, Request, status

from app.api.deps import SessionDep
from app.core.ratelimit import WRITE_LIMIT, limiter
from app.schemas.pagination import Page
from app.schemas.user import UserCreate, UserRead
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_LIMIT)
async def create_user(
    request: Request, payload: UserCreate, session: SessionDep
) -> UserRead:
    """Register a new user (public; always a student). 409 if email taken."""
    user = await user_service.create_user(
        session, name=payload.name, email=payload.email, password=payload.password
    )
    return user  # FastAPI serializes the ORM object via UserRead (from_attributes)


@router.get("", response_model=Page[UserRead])
async def list_users(
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100, description="Max rows to return."),
    offset: int = Query(0, ge=0, description="Rows to skip."),
) -> Page[UserRead]:
    """List users (newest first), paginated."""
    items, total = await user_service.list_users(session, limit=limit, offset=offset)
    return Page(items=items, total=total, limit=limit, offset=offset)
