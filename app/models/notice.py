"""Notice model."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.user import User


class Notice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notices"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # long free text
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # "postedBy (User)" from the spec -> a foreign key to users.id.
    # ondelete="CASCADE": if the author is deleted, their notices go too.
    posted_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ORM-level convenience: `notice.posted_by` loads the related User object.
    posted_by: Mapped[User] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<Notice {self.title!r}>"
