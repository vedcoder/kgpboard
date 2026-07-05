"""User endpoints."""

from fastapi import APIRouter, Query, status

from app.api.deps import SessionDep
from app.schemas.pagination import Page
from app.schemas.user import UserCreate, UserRead
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: SessionDep) -> UserRead:
    """Create a new user. 409 if the email is already taken."""
    user = await user_service.create_user(
        session, name=payload.name, email=payload.email, role=payload.role
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
