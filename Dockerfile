# Official uv image bundles Python 3.14 + uv, so builds are fast and reproducible.
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

# Compile to bytecode for faster startup; copy (not symlink) into the venv.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies FIRST, from the lockfile, as a cached layer. This layer
# is rebuilt only when pyproject.toml / uv.lock change -- not on every code edit.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application code and migration tooling.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts
COPY docker ./docker
RUN chmod +x docker/entrypoint.sh

# Put the venv on PATH so `alembic` / `uvicorn` resolve directly, and make the
# app importable no matter the working dir (e.g. `python scripts/create_admin.py`).
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

EXPOSE 8000
ENTRYPOINT ["/app/docker/entrypoint.sh"]
