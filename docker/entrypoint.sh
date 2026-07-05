#!/bin/sh
# Apply migrations, then start the API. Runs once the DB is reachable
# (compose waits for the db healthcheck before starting this container).
set -e

echo "Applying database migrations..."
alembic upgrade head

echo "Starting API on :8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
