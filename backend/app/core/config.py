"""Centralized application configuration using pydantic-settings.

Adheres strictly to ScholarPulse AGENTS.md Section 4:
- All environment-specific settings are environment-driven.
- Safe defaults are provided only for non-sensitive local development.
- Secrets are treated as opaque and never exposed in logs or API responses.
"""

from functools import lru_cache
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings validated at startup."""

    # Application settings
    APP_ENV: str = Field(default="development", description="Runtime environment: development, test, or production")
    APP_NAME: str = Field(default="ScholarPulse", description="Application service name")
    API_V1_PREFIX: str = Field(default="/api/v1", description="Prefix for Version 1 API endpoints")
    HOST: str = Field(default="0.0.0.0", description="Host bind address")
    PORT: int = Field(default=8000, description="Port number")
    LOG_LEVEL: str = Field(default="INFO", description="Logging verbosity")

    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/scholarpulse",
        description="PostgreSQL database connection URL",
    )
    TEST_DATABASE_URL: str = Field(
        default="sqlite:///./test.db",
        description="Isolated database connection URL for testing",
    )

    # CORS settings
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins for web clients",
    )

    # Security settings (used only when authentication is enabled)
    SECRET_KEY: str = Field(
        default="placeholder-secret-key-for-development-only-change-in-prod",
        description="Secret key for signing session tokens",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=1440,
        description="Access token lifetime in minutes",
    )

    # Paths
    DATASET_PATH: str = Field(
        default="./datasets/raw/sample_papers.json",
        description="Path to local research dataset",
    )
    ARTIFACTS_PATH: str = Field(
        default="./artifacts",
        description="Path to derived indexes, vectorizers, and models",
    )

    # Optional external provider credentials (disabled by default)
    OPENALEX_API_KEY: Union[str, None] = Field(
        default=None,
        description="Optional OpenAlex API key",
    )
    CROSSREF_MAILTO: Union[str, None] = Field(
        default=None,
        description="Optional Crossref contact email",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
