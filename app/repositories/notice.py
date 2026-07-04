"""Notice data access."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notice import Notice


async def create(
    session: AsyncSession,
    *,
    title: str,
    content: str,
    category: str,
    posted_by_id: uuid.UUID,
) -> Notice:
    """Insert a new notice and return it."""
    notice = Notice(
        title=title,
        content=content,
        category=category,
        posted_by_id=posted_by_id,
    )
    session.add(notice)
    await session.flush()  # surfaces FK violation (unknown posted_by_id) here
    await session.refresh(notice)
    return notice


async def list_all(session: AsyncSession) -> Sequence[Notice]:
    """Return all notices, newest first."""
    result = await session.execute(select(Notice).order_by(Notice.created_at.desc()))
    return result.scalars().all()
