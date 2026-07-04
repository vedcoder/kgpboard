"""Event service: business rules for events."""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTimeRangeError
from app.models.event import Event
from app.repositories import event as event_repo


async def create_event(
    session: AsyncSession,
    *,
    title: str,
    description: str,
    category: str,
    venue: str,
    start_time: datetime,
    end_time: datetime,
    organizer: str,
) -> Event:
    """Create an event, enforcing that startTime comes before endTime.

    We check here to return a friendly 400 *before* hitting the database; the
    CHECK constraint remains the last-line-of-defense backstop.
    """
    if start_time >= end_time:
        raise InvalidTimeRangeError("startTime must be before endTime.")

    event = await event_repo.create(
        session,
        title=title,
        description=description,
        category=category,
        venue=venue,
        start_time=start_time,
        end_time=end_time,
        organizer=organizer,
    )
    await session.commit()
    return event


async def list_events(session: AsyncSession) -> Sequence[Event]:
    return await event_repo.list_all(session)
