"""Notice request/response schemas."""

import uuid
from datetime import datetime

from pydantic import Field

from app.schemas.base import CamelModel
from app.schemas.user import UserRead


class NoticeCreate(CamelModel):
    """Request body for POST /notices.

    On create the client sends only the author's id (`postedById`); the full
    User is embedded in the response, not the request.
    """

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
    # The spec models this as `postedBy (User)`, so we embed the whole user.
    posted_by: UserRead  # serialized as "postedBy"
    created_at: datetime
