"""User model."""

import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, enum.Enum):
    """Allowed values for `User.role`.

    Subclassing `str` makes the enum JSON-serializable and comparable to plain
    strings, while still constraining values to this fixed set both in Python
    and (via a Postgres ENUM type) in the database.
    """

    student = "student"
    admin = "admin"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # `unique=True` creates a UNIQUE constraint -> the DB itself rejects a second
    # user with the same email, even under concurrent inserts. `index=True`
    # makes "find user by email" fast (used for login later).
    email: Mapped[str] = mapped_column(
        String(320), unique=True, index=True, nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.student,
    )

    # Argon2 hash of the user's password. Never exposed by any response schema.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:  # nicer debugging output
        return f"<User {self.email} ({self.role.value})>"
