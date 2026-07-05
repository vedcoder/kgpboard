"""Rate limiting for write endpoints.

Uses SlowAPI with an in-memory store. NOTE: in-memory state resets on restart
and is NOT shared across multiple workers/replicas. For real production, point
`storage_uri` at Redis (e.g. "redis://localhost:6379") -- a one-line change; the
rest of this code is unaffected.
"""

import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.security import decode_token


def client_key(request: Request) -> str:
    """Identify the caller for rate-limiting.

    Prefer the authenticated user (so limits are per-account when logged in);
    fall back to the client IP for anonymous requests like registration.
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            payload = decode_token(auth.removeprefix("Bearer "))
            return f"user:{payload['sub']}"
        except (jwt.PyJWTError, KeyError):
            pass
    return get_remote_address(request)


# storage_uri defaults to in-memory ("memory://"). Swap for Redis in prod.
limiter = Limiter(key_func=client_key)

# The shared limit for write endpoints; referenced by the route decorators.
WRITE_LIMIT = "5/minute"
