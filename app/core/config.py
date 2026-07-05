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

    # --- JWT auth ---
    # Secret used to SIGN tokens. Anyone with this can mint valid tokens, so it
    # must stay secret and be strong in production. Loaded from the environment.
    jwt_secret: str
    # HS256 = symmetric signing with the shared secret above.
    jwt_algorithm: str = "HS256"
    # How long an access token stays valid after login.
    access_token_expire_minutes: int = 60

    # --- CORS ---
    # Comma-separated list of browser origins allowed to call the API.
    # Defaults to the Vite dev server. Override via env in other environments.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


# A single shared instance imported by the rest of the app.
settings = Settings()  # type: ignore[call-arg]  # values come from the environment
