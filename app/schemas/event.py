"""Event request/response schemas."""

import uuid
from datetime import datetime

from pydantic import Field

from app.schemas.base import CamelModel


class EventCreate(CamelModel):
    """Request body for POST /events.

    Note: the startTime < endTime rule is a *business rule* enforced in the
    service layer (and the DB), not here -- so the API returns our clean
    domain-error message rather than a schema error.
    """

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    category: str = Field(min_length=1, max_length=100)
    venue: str = Field(min_length=1, max_length=255)
    start_time: datetime  # accepted as "startTime" (ISO 8601)
    end_time: datetime  # accepted as "endTime"
    organizer: str = Field(min_length=1, max_length=255)


class EventRead(CamelModel):
    """Response body for an event."""

    id: uuid.UUID
    title: str
    description: str
    category: str
    venue: str
    start_time: datetime
    end_time: datetime
    organizer: str
    created_at: datetime
