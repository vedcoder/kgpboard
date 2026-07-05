"""Auth schemas."""

from app.schemas.base import CamelModel


class Token(CamelModel):
    """Response from POST /auth/login."""

    access_token: str
    token_type: str = "bearer"
