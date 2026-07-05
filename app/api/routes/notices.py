"""Notice endpoints."""

from datetime import datetime

from fastapi import APIRouter, Query, Request, status

from app.api.deps import AdminUser, SessionDep
from app.core.ratelimit import WRITE_LIMIT, limiter
from app.schemas.notice import NoticeCreate, NoticeRead
from app.schemas.pagination import Page
from app.services import notice as notice_service

router = APIRouter(prefix="/notices", tags=["notices"])


@router.post("", response_model=NoticeRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_LIMIT)
async def create_notice(
    request: Request, payload: NoticeCreate, session: SessionDep, admin: AdminUser
) -> NoticeRead:
    """Create a notice (admins only). The author is the authenticated admin."""
    return await notice_service.create_notice(
        session,
        title=payload.title,
        content=payload.content,
        category=payload.category,
        poster=admin,
    )


@router.get("", response_model=Page[NoticeRead])
async def list_notices(
    session: SessionDep,
    category: str | None = Query(None, description="Exact category match."),
    date_from: datetime | None = Query(
        None, alias="from", description="Only notices created on/after this time."
    ),
    date_to: datetime | None = Query(
        None, alias="to", description="Only notices created on/before this time."
    ),
    q: str | None = Query(
        None, min_length=1, description="Keyword search in title/content."
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Page[NoticeRead]:
    """List notices (newest first), filtered and paginated."""
    items, total = await notice_service.list_notices(
        session,
        category=category,
        date_from=date_from,
        date_to=date_to,
        q=q,
        limit=limit,
        offset=offset,
    )
    return Page(items=items, total=total, limit=limit, offset=offset)
