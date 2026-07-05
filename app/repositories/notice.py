"""Notice data access."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notice import Notice
from app.models.user import User


async def create(
    session: AsyncSession,
    *,
    title: str,
    content: str,
    category: str,
    posted_by: User,
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
    )
    session.add(notice)
    await session.flush()
    # Refresh only the DB-generated columns; leave the loaded `posted_by` intact.
    await session.refresh(notice, attribute_names=["id", "created_at"])
    return notice


async def list_all(session: AsyncSession) -> Sequence[Notice]:
    """Return all notices, newest first."""
    result = await session.execute(select(Notice).order_by(Notice.created_at.desc()))
    return result.scalars().all()
