"""FastAPI application entry point.

Run in dev with:  uv run uvicorn app.main:app --reload
Interactive docs:  http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.routes import events, notices, users

app = FastAPI(
    title="KGPBoard API",
    description="Campus events & notices API.",
    version="0.1.0",
)

# Turn domain/validation errors into clean JSON responses.
register_exception_handlers(app)

# Mount the feature routers.
app.include_router(users.router)
app.include_router(notices.router)
app.include_router(events.router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}
