"""Model registry.

Importing every model here ensures they are all registered on
`Base.metadata` whenever `app.models` is imported. Alembic imports this package
so its autogenerate can "see" all tables.
"""

from app.models.event import Event
from app.models.notice import Notice
from app.models.user import User, UserRole

__all__ = ["Event", "Notice", "User", "UserRole"]
