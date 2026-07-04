"""Event data access."""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


async def create(
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
    """Insert a new event and return it."""
    event = Event(
        title=title,
        description=description,
        category=category,
        venue=venue,
        start_time=start_time,
        end_time=end_time,
        organizer=organizer,
    )
    session.add(event)
    await session.flush()  # surfaces the start<end CHECK violation here
    await session.refresh(event)
    return event


async def list_all(session: AsyncSession) -> Sequence[Event]:
    """Return all events, soonest start first."""
    result = await session.execute(select(Event).order_by(Event.start_time.asc()))
    return result.scalars().all()
