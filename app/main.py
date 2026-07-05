"""FastAPI application entry point.

Run in dev with:  uv run uvicorn app.main:app --reload
Interactive docs:  http://127.0.0.1:8000/docs
"""

from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from app.api.errors import register_exception_handlers
from app.api.routes import auth, events, notices, uploads, users
from app.core.config import settings
from app.core.ratelimit import limiter

app = FastAPI(
    title="KGPBoard API",
    description="Campus events & notices API.",
    version="0.1.0",
)

# Allow the browser frontend (different origin) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the rate limiter and a 429 handler that matches our error shape.
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": f"Rate limit exceeded: {exc.detail}. Try again later."},
    )


# Turn domain/validation errors into clean JSON responses.
register_exception_handlers(app)

# Serve uploaded posters as static files (dir created if missing).
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Mount the feature routers.
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notices.router)
app.include_router(events.router)
app.include_router(uploads.router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}
