"""Image upload endpoint."""

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

from app.api.deps import AdminUser
from app.core.config import settings
from app.core.ratelimit import WRITE_LIMIT, limiter
from app.core.storage import storage

router = APIRouter(tags=["uploads"])

# Allowed image content-types mapped to the file extension we store.
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@router.post("/uploads")
@limiter.limit(WRITE_LIMIT)
async def upload_image(
    request: Request,
    admin: AdminUser,
    file: UploadFile = File(...),
) -> dict[str, str]:
    """Upload a poster (admins only). Returns an absolute URL to the stored file.

    Validates the content type and size, and stores under a random name so a
    malicious filename can't cause a path traversal or overwrite.
    """
    ext = ALLOWED_TYPES.get(file.content_type or "")
    if ext is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Only JPEG, PNG, or WebP images are allowed.",
        )

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Image must be 5 MB or smaller."
        )

    path = storage.save_bytes(content, ext)  # e.g. "/uploads/ab12.png"
    return {"url": str(request.base_url).rstrip("/") + path}
