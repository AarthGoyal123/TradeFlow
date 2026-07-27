"""Typed application settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="TRADEFLOW_", env_file=".env", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite:///./tradeflow.sqlite"
    upload_dir: Path = Path("./data/uploads")
    output_dir: Path = Path("./data/outputs")
    template_root: Path = Path("../templates")
    max_upload_size_mb: int = Field(default=50, gt=0)
    allowed_extensions: tuple[str, ...] = (".xlsx",)
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()

