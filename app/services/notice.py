"""Notice service: business rules for notices."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserNotFoundError
from app.models.notice import Notice
from app.repositories import notice as notice_repo
from app.repositories import user as user_repo


async def create_notice(
    session: AsyncSession,
    *,
    title: str,
    content: str,
    category: str,
    posted_by_id: uuid.UUID,
) -> Notice:
    """Create a notice, verifying the author (postedBy) actually exists.

    The DB's foreign key would reject an unknown author too, but checking here
    lets us return a clear "user not found" message instead of a raw FK error.
    """
    poster = await user_repo.get_by_id(session, posted_by_id)
    if poster is None:
        raise UserNotFoundError(
            f"No user found with id '{posted_by_id}' to post this notice."
        )

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
