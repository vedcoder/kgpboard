"""Notice service: business rules for notices."""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notice import Notice
from app.models.user import User
from app.repositories import notice as notice_repo


async def create_notice(
    session: AsyncSession,
    *,
    title: str,
    content: str,
    category: str,
    poster: User,
) -> Notice:
    """Create a notice authored by `poster` (the authenticated admin).

    No "author exists" check is needed anymore -- the poster comes from a valid
    token, so it's guaranteed to be a real user.
    """
    notice = await notice_repo.create(
        session,
        title=title,
        content=content,
        category=category,
        posted_by=poster,
    )
    await session.commit()
    return notice


async def list_notices(
    session: AsyncSession,
    *,
    category: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[Sequence[Notice], int]:
    return await notice_repo.list_(
        session,
        category=category,
        date_from=date_from,
        date_to=date_to,
        q=q,
        limit=limit,
        offset=offset,
    )
