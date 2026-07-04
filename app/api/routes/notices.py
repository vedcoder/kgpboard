"""Notice endpoints."""

from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.schemas.notice import NoticeCreate, NoticeRead
from app.services import notice as notice_service

router = APIRouter(prefix="/notices", tags=["notices"])


@router.post("", response_model=NoticeRead, status_code=status.HTTP_201_CREATED)
async def create_notice(payload: NoticeCreate, session: SessionDep) -> NoticeRead:
    """Create a notice. 400 if the postedBy user does not exist."""
    return await notice_service.create_notice(
        session,
        title=payload.title,
        content=payload.content,
        category=payload.category,
        posted_by_id=payload.posted_by_id,
    )


@router.get("", response_model=list[NoticeRead])
async def list_notices(session: SessionDep) -> list[NoticeRead]:
    """List all notices, newest first."""
    return await notice_service.list_notices(session)
