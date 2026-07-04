"""Reusable column groups shared by every model.

Each entity has a UUID primary key and a `created_at` timestamp. Rather than
repeat those two columns in all three models, we define them once here and mix
them into each model class.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKeyMixin:
    # UUID primary key generated *by Postgres* (gen_random_uuid() is built in
    # since PG13). Server-side generation means the DB is the single source of
    # truth for ids, even if a row is inserted outside our app.
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )


class TimestampMixin:
    # `timezone=True` -> stored as `timestamptz`; always store UTC, never naive
    # local times. `server_default=now()` lets the DB stamp the row on insert.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
