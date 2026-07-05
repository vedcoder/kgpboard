"""Event data access."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, EventCategory, TargetYear


async def create(
    session: AsyncSession,
    *,
    title: str,
    description: str,
    category: EventCategory,
    venue: str,
    start_time: datetime,
    end_time: datetime,
    organizer: str,
    image_url: str | None = None,
    registration_url: str | None = None,
    target_year: TargetYear | None = None,
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
        image_url=image_url,
        registration_url=registration_url,
        target_year=target_year,
    )
    session.add(event)
    await session.flush()  # surfaces the start<end CHECK violation here
    await session.refresh(event)
    return event


async def get_by_id(session: AsyncSession, event_id: uuid.UUID) -> Event | None:
    """Fetch a single event by id, or None."""
    return await session.get(Event, event_id)


def _filters(
    *,
    category: EventCategory | None,
    date_from: datetime | None,
    date_to: datetime | None,
    q: str | None,
) -> list[ColumnElement[bool]]:
    """Turn optional filter values into a list of SQL conditions.

    Only non-None filters produce a condition, so an unset filter simply does
    not constrain the query. The list is applied to BOTH the count and the
    page query, guaranteeing they stay in sync.
    """
    conditions: list[ColumnElement[bool]] = []
    if category is not None:
        conditions.append(Event.category == category)
    if date_from is not None:
        conditions.append(Event.start_time >= date_from)
    if date_to is not None:
        conditions.append(Event.start_time <= date_to)
    if q is not None:
        like = f"%{q}%"
        conditions.append(or_(Event.title.ilike(like), Event.description.ilike(like)))
    return conditions


async def list_(
    session: AsyncSession,
    *,
    category: EventCategory | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[Sequence[Event], int]:
    """Return a filtered, paginated page of events plus the total match count."""
    conditions = _filters(category=category, date_from=date_from, date_to=date_to, q=q)

    total = await session.scalar(
        select(func.count()).select_from(Event).where(*conditions)
    )

    result = await session.execute(
        select(Event)
        .where(*conditions)
        .order_by(Event.start_time.asc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all(), total or 0
