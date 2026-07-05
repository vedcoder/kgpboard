"""Event model."""

import enum
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import CheckConstraint, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class EventCategory(str, enum.Enum):
    """Fixed set of event categories (stored as a Postgres enum)."""

    workshop = "Workshop"
    talk = "Talk"
    cultural = "Cultural"
    sports = "Sports"
    placement = "Placement"
    fest = "Fest"


class TargetYear(str, enum.Enum):
    """Which student year(s) an event targets."""

    all = "All years"
    y1 = "1st year"
    y2 = "2nd year"
    y3 = "3rd year"
    y4 = "4th year"
    y5 = "5th year"


def _values(enum_cls: type[enum.Enum]) -> list[str]:
    return [member.value for member in enum_cls]


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
    category: Mapped[EventCategory] = mapped_column(
        SAEnum(EventCategory, name="event_category", values_callable=_values),
        nullable=False,
        index=True,
    )
    venue: Mapped[str] = mapped_column(String(255), nullable=False)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Optional registration link (e.g. a Google Form) shown on the event.
    registration_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Optional target student year(s) for the event.
    target_year: Mapped[TargetYear | None] = mapped_column(
        SAEnum(TargetYear, name="target_year", values_callable=_values),
        nullable=True,
        index=True,
    )

    # "organizer" is free text -- a person, club, or department name -- not a
    # foreign key. This matches the spec, which lists it plainly (unlike
    # Notice.postedBy, which is explicitly "(User)").
    organizer: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Optional poster image URL (uploaded via /uploads). Many events won't have one.
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<Event {self.title!r}>"
