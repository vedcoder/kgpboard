#!/bin/sh
# Apply migrations, then start the API. Runs once the DB is reachable
# (compose waits for the db healthcheck before starting this container).
set -e

echo "Applying database migrations..."
alembic upgrade head

# Railway/Render inject $PORT; fall back to 8000 for local Docker.
PORT="${PORT:-8000}"
echo "Starting API on :${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
