"""Event endpoints."""

from datetime import datetime

from fastapi import APIRouter, Query, status

from app.api.deps import SessionDep
from app.schemas.event import EventCreate, EventRead
from app.schemas.pagination import Page
from app.services import event as event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(payload: EventCreate, session: SessionDep) -> EventRead:
    """Create an event. 400 if startTime is not before endTime."""
    return await event_service.create_event(
        session,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        venue=payload.venue,
        start_time=payload.start_time,
        end_time=payload.end_time,
        organizer=payload.organizer,
    )


@router.get("", response_model=Page[EventRead])
async def list_events(
    session: SessionDep,
    category: str | None = Query(None, description="Exact category match."),
    date_from: datetime | None = Query(
        None, alias="from", description="Only events starting on/after this time."
    ),
    date_to: datetime | None = Query(
        None, alias="to", description="Only events starting on/before this time."
    ),
    q: str | None = Query(
        None, min_length=1, description="Keyword search in title/description."
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Page[EventRead]:
    """List events (soonest first), filtered and paginated."""
    items, total = await event_service.list_events(
        session,
        category=category,
        date_from=date_from,
        date_to=date_to,
        q=q,
        limit=limit,
        offset=offset,
    )
    return Page(items=items, total=total, limit=limit, offset=offset)
