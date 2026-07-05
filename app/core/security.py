"""Security primitives: password hashing and JWT tokens.

Two independent concerns live here:
- Passwords are *hashed* (one-way) with Argon2. We never store or compare the
  raw password -- only its hash. Verifying re-hashes the input and compares.
- Access tokens are *signed* (not encrypted) JWTs. The client can read the
  payload, but cannot forge one without the secret. We trust a token because
  the signature proves we issued it.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# Argon2 with sane defaults; `.recommended()` picks a modern, strong scheme.
_password_hash = PasswordHash.recommended()


def hash_password(plain: str) -> str:
    """Return an Argon2 hash of the password (safe to store)."""
    return _password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a stored hash."""
    return _password_hash.verify(plain, hashed)


def create_access_token(*, subject: str, role: str) -> str:
    """Create a signed JWT carrying the user id (`sub`) and `role`.

    `exp` (expiry) is embedded and enforced by the decoder, so an old token
    stops working on its own.
    """
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Verify signature + expiry and return the payload.

    Raises `jwt.PyJWTError` (or a subclass) if the token is invalid or expired;
    callers translate that into a 401.
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
