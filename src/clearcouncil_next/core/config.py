"""Runtime configuration for the next-generation platform."""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CC_NEXT_", extra="ignore")

    app_name: str = "ClearCouncil Next"
    environment: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    database_url: str = "sqlite:///./clearcouncil_next.db"
    worker_poll_seconds: int = 5
    api_token: Optional[str] = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cache settings so modules can import safely without repeated parsing."""
    return Settings()
