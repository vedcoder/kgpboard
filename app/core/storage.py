"""File storage abstraction.

Callers only know `storage.save_bytes(content, ext) -> url_path`. Today that's
the local filesystem; swapping in S3/Cloudflare R2 later means writing another
class with the same method and pointing `storage` at it -- nothing else changes.
"""

import uuid
from pathlib import Path
from typing import Protocol

from app.core.config import settings


class Storage(Protocol):
    def save_bytes(self, content: bytes, ext: str) -> str:
        """Persist bytes and return the URL path (e.g. '/uploads/ab12.png')."""
        ...


class LocalStorage:
    """Writes files to a local directory, served as static files by the app."""

    def __init__(self, base_dir: str, url_prefix: str = "/uploads") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.url_prefix = url_prefix

    def save_bytes(self, content: bytes, ext: str) -> str:
        name = f"{uuid.uuid4().hex}{ext}"  # random name -> no collisions, no path traversal
        (self.base_dir / name).write_bytes(content)
        return f"{self.url_prefix}/{name}"


# The single instance the app uses.
storage: Storage = LocalStorage(settings.upload_dir)
