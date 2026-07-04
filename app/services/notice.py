"""Notice service: business rules for notices."""

import uuid
from collections.abc import Sequence

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
    if await user_repo.get_by_id(session, posted_by_id) is None:
        raise UserNotFoundError(
            f"No user found with id '{posted_by_id}' to post this notice."
        )

    notice = await notice_repo.create(
        session,
        title=title,
        content=content,
        category=category,
        posted_by_id=posted_by_id,
    )
    await session.commit()
    return notice


async def list_notices(session: AsyncSession) -> Sequence[Notice]:
    return await notice_repo.list_all(session)
