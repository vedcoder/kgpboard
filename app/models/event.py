"""Event model."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Event(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "events"

    # Enforce the "start must come before end" rule at the DATABASE level, so a
    # bad range is impossible to persist no matter what the app code does. The
    # service layer will also check this to return a friendly 400 -- but this is
    # the last line of defense.
    __table_args__ = (
        CheckConstraint("start_time < end_time", name="ck_events_start_before_end"),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    venue: Mapped[str] = mapped_column(String(255), nullable=False)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # "organizer" is free text -- a person, club, or department name -- not a
    # foreign key. This matches the spec, which lists it plainly (unlike
    # Notice.postedBy, which is explicitly "(User)").
    organizer: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Event {self.title!r}>"
