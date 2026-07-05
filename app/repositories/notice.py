"""Notice data access."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notice import Notice, NoticeCategory
from app.models.user import User


async def get_by_id(session: AsyncSession, notice_id: uuid.UUID) -> Notice | None:
    """Fetch a single notice by id (with posted_by loaded), or None."""
    result = await session.execute(select(Notice).where(Notice.id == notice_id))
    return result.scalar_one_or_none()


async def create(
    session: AsyncSession,
    *,
    title: str,
    content: str,
    category: NoticeCategory,
    posted_by: User,
    image_url: str | None = None,
) -> Notice:
    """Insert a new notice and return it.

    We pass the User *object* (not just its id) and assign the relationship.
    SQLAlchemy derives `posted_by_id` from it on flush, and -- importantly --
    `notice.posted_by` is populated in memory, so serializing the nested user
    in the response needs no extra query and no risky async lazy-load.
    """
    notice = Notice(
        title=title,
        content=content,
        category=category,
        posted_by=posted_by,
        image_url=image_url,
    )
    session.add(notice)
    await session.flush()
    # Refresh only the DB-generated columns; leave the loaded `posted_by` intact.
    await session.refresh(notice, attribute_names=["id", "created_at"])
    return notice


def _filters(
    *,
    category: NoticeCategory | None,
    date_from: datetime | None,
    date_to: datetime | None,
    q: str | None,
) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = []
    if category is not None:
        conditions.append(Notice.category == category)
    if date_from is not None:
        conditions.append(Notice.created_at >= date_from)
    if date_to is not None:
        conditions.append(Notice.created_at <= date_to)
    if q is not None:
        like = f"%{q}%"
        conditions.append(or_(Notice.title.ilike(like), Notice.content.ilike(like)))
    return conditions


async def list_(
    session: AsyncSession,
    *,
    category: NoticeCategory | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[Sequence[Notice], int]:
    """Return a filtered, paginated page of notices plus the total match count."""
    conditions = _filters(category=category, date_from=date_from, date_to=date_to, q=q)

    total = await session.scalar(
        select(func.count()).select_from(Notice).where(*conditions)
    )

    result = await session.execute(
        select(Notice)
        .where(*conditions)
        .order_by(Notice.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all(), total or 0
