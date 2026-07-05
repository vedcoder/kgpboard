"""Event service: business rules for events."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTimeRangeError, NotFoundError
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
    image_url: str | None = None,
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
        image_url=image_url,
    )
    await session.commit()
    return event


async def get_event(session: AsyncSession, event_id: uuid.UUID) -> Event:
    """Return one event or raise NotFoundError (-> 404)."""
    event = await event_repo.get_by_id(session, event_id)
    if event is None:
        raise NotFoundError(f"No event found with id '{event_id}'.")
    return event


async def list_events(
    session: AsyncSession,
    *,
    category: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[Sequence[Event], int]:
    return await event_repo.list_(
        session,
        category=category,
        date_from=date_from,
        date_to=date_to,
        q=q,
        limit=limit,
        offset=offset,
    )
