"""Notice request/response schemas."""

import uuid
from datetime import datetime

from pydantic import Field

from app.models.notice import NoticeCategory
from app.schemas.base import CamelModel
from app.schemas.user import UserRead


class NoticeCreate(CamelModel):
    """Request body for POST /notices.

    There is no `postedById`: the author is the authenticated admin, taken from
    the JWT -- not something the client can spoof. The full User is embedded in
    the response.
    """

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    category: NoticeCategory  # must be one of the fixed categories
    image_url: str | None = Field(default=None, max_length=500)  # "imageUrl"


class NoticeRead(CamelModel):
    """Response body for a notice."""

    id: uuid.UUID
    title: str
    content: str
    category: NoticeCategory
    # The spec models this as `postedBy (User)`, so we embed the whole user.
    posted_by: UserRead  # serialized as "postedBy"
    image_url: str | None = None
    created_at: datetime
