"""Shared FastAPI dependencies for route handlers."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

# A reusable type alias: annotate a route parameter with `SessionDep` and
# FastAPI injects a fresh AsyncSession per request (from `get_session`), then
# closes it when the request finishes.
SessionDep = Annotated[AsyncSession, Depends(get_session)]
