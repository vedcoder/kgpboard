"""Application configuration.

Settings are loaded from environment variables (and a local `.env` file in dev)
into a single typed `Settings` object. Nothing that varies per-environment or is
secret should be hardcoded anywhere else in the app -- it comes from here.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Read from a `.env` file if present; ignore any env vars we don't declare.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # SQLAlchemy async connection URL, e.g.
    #   postgresql+asyncpg://user:pass@localhost:5432/kgpboard
    database_url: str


# A single shared instance imported by the rest of the app.
settings = Settings()  # type: ignore[call-arg]  # values come from the environment
