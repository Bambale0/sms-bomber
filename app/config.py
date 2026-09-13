from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or `.env`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(min_length=1)
    request_timeout_seconds: float = Field(default=5.0, gt=0, le=30)
    max_concurrency: int = Field(default=5, ge=1, le=20)
    max_retries: int = Field(default=2, ge=0, le=5)
    retry_base_delay_seconds: float = Field(default=0.25, ge=0, le=5)
    allowed_target_hosts: str = "localhost,127.0.0.1"
    sandbox_target_url: str = "http://localhost:8080/test-notification"

    @property
    def allowed_hosts(self) -> frozenset[str]:
        return frozenset(
            host.strip().lower()
            for host in self.allowed_target_hosts.split(",")
            if host.strip()
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
