"""Model registry.

Importing every model here ensures they are all registered on
`Base.metadata` whenever `app.models` is imported. Alembic imports this package
so its autogenerate can "see" all tables.
"""

from app.models.event import Event, EventCategory, TargetYear
from app.models.notice import Notice, NoticeCategory
from app.models.user import User, UserRole

__all__ = [
    "Event",
    "EventCategory",
    "Notice",
    "NoticeCategory",
    "TargetYear",
    "User",
    "UserRole",
]
