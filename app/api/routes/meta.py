"""Metadata endpoint: the fixed option lists the UI needs for dropdowns."""

from fastapi import APIRouter

from app.models.event import EventCategory, TargetYear
from app.models.notice import NoticeCategory

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("")
async def get_meta() -> dict[str, list[str]]:
    """Return the allowed category and target-year values."""
    return {
        "noticeCategories": [c.value for c in NoticeCategory],
        "eventCategories": [c.value for c in EventCategory],
        "targetYears": [y.value for y in TargetYear],
    }
