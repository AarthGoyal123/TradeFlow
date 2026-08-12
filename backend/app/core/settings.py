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
    allowed_extensions: tuple[str, ...] = (".xlsx", ".xls")
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    @property
    def resolved_template_root(self) -> Path:
        """Return template root as an absolute path."""
        if self.template_root.is_absolute():
            return self.template_root
        return (Path.cwd() / self.template_root).resolve()

    @property
    def resolved_upload_dir(self) -> Path:
        """Return upload directory as an absolute path."""
        if self.upload_dir.is_absolute():
            return self.upload_dir
        return (Path.cwd() / self.upload_dir).resolve()

    @property
    def resolved_output_dir(self) -> Path:
        """Return output directory as an absolute path."""
        if self.output_dir.is_absolute():
            return self.output_dir
        return (Path.cwd() / self.output_dir).resolve()

    @property
    def resolved_database_path(self) -> Path:
        """Return SQLite database path for local file-backed URLs."""
        prefix = "sqlite:///"
        if not self.database_url.startswith(prefix):
            raise ValueError("Only sqlite:/// database URLs are supported")
        database_path = Path(self.database_url.removeprefix(prefix))
        if database_path.is_absolute():
            return database_path
        return (Path.cwd() / database_path).resolve()


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
