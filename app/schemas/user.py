"""User request/response schemas."""

import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from app.models.user import UserRole
from app.schemas.base import CamelModel


class UserCreate(CamelModel):
    """Request body for POST /users (public self-registration).

    There is deliberately no `role` field: public sign-up always creates a
    `student`. Admins are provisioned out-of-band (see scripts/create_admin.py),
    so a user can never grant themselves admin.
    """

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr  # validated format (email-validator)
    password: str = Field(min_length=8, max_length=128)


class UserRead(CamelModel):
    """Response body for a user. Note: `password_hash` is never included."""

    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime  # serialized as "createdAt"


class UserRoleUpdate(CamelModel):
    """Request body for PATCH /users/{id}/role."""

    role: UserRole
