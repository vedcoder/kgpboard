"""Generic pagination envelope for list endpoints."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """A page of results plus the metadata a client needs to paginate.

    `Page[EventRead]` produces a response like:
        {"items": [...], "total": 42, "limit": 20, "offset": 0}
    `total` is the count of ALL matching rows (ignoring limit/offset), so a
    client can compute how many pages exist.
    """

    items: list[T]
    total: int
    limit: int
    offset: int
