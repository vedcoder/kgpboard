"""Notice model."""

import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.user import User


class NoticeCategory(str, enum.Enum):
    """Fixed set of notice categories (stored as a Postgres enum)."""

    academic = "Academic"
    examination = "Examination"
    placement = "Placement"
    hostel = "Hostel"
    scholarship = "Scholarship"
    general = "General"


# Store the human-readable value ("Academic"), not the member name ("academic").
def _values(enum_cls: type[enum.Enum]) -> list[str]:
    return [member.value for member in enum_cls]


class Notice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notices"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # long free text
    category: Mapped[NoticeCategory] = mapped_column(
        SAEnum(NoticeCategory, name="notice_category", values_callable=_values),
        nullable=False,
        index=True,
    )

    # "postedBy (User)" from the spec -> a foreign key to users.id.
    # ondelete="CASCADE": if the author is deleted, their notices go too.
    posted_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ORM-level convenience: `notice.posted_by` loads the related User object.
    posted_by: Mapped[User] = relationship(lazy="selectin")

    # Optional poster/graphic image URL (uploaded via /uploads).
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<Notice {self.title!r}>"
