"""Notice request/response schemas."""

import uuid
from datetime import datetime

from pydantic import Field

from app.schemas.base import CamelModel


class NoticeCreate(CamelModel):
    """Request body for POST /notices."""

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    category: str = Field(min_length=1, max_length=100)
    posted_by_id: uuid.UUID  # accepted as "postedById"


class NoticeRead(CamelModel):
    """Response body for a notice."""

    id: uuid.UUID
    title: str
    content: str
    category: str
    posted_by_id: uuid.UUID  # serialized as "postedById"
    created_at: datetime
