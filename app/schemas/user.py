"""User request/response schemas."""

import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from app.models.user import UserRole
from app.schemas.base import CamelModel


class UserCreate(CamelModel):
    """Request body for POST /users."""

    # `min_length=1` rejects empty strings; a missing field is rejected by
    # Pydantic automatically because it has no default.
    name: str = Field(min_length=1, max_length=255)
    # `EmailStr` validates the address format (needs the email-validator lib).
    email: EmailStr
    # Defaults to student, so `role` is optional in the request.
    role: UserRole = UserRole.student


class UserRead(CamelModel):
    """Response body for a user. Includes server-generated fields."""

    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime  # serialized as "createdAt"
