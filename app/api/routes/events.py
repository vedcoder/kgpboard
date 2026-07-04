"""Event endpoints."""

from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.schemas.event import EventCreate, EventRead
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


@router.get("", response_model=list[EventRead])
async def list_events(session: SessionDep) -> list[EventRead]:
    """List all events, soonest first."""
    return await event_service.list_events(session)
