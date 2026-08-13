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
    upload_dir: Path = Path("./data/uploads")
    output_dir: Path = Path("./data/outputs")
    template_root: Path = Path("../templates")
    max_upload_size_mb: int = Field(default=50, gt=0)
    allowed_extensions: tuple[str, ...] = (".xlsx", ".xls")
    upload_size_limit_mb: int = 50
    
    # Persistence
    database_url: str = "sqlite:///./data/tradeflow.db"
    
    # Storage Architecture
    storage_backend: Literal["local", "s3"] = "local"
    s3_endpoint_url: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket_name: str | None = None
    s3_region: str | None = None
    
    # Infrastructure
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    
    # Background Processing Configuration
    job_executor: Literal["sync", "celery"] = "sync"
    celery_broker_url: str = "memory://"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Authentication Settings
    auth_secret: str = "super-secret-development-key-change-in-production"
    jwt_expire_minutes: int = 60
    cookie_secure: bool = False  # Set True in production (HTTPS)
    cookie_samesite: str = "lax"

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
