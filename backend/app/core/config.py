from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Local Agentic Enterprise Platform"
    env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_origin: str = "http://localhost:3000"

    database_url: str = Field(
        default="sqlite+aiosqlite:///./laep.db",
        description="Async SQLAlchemy database URL.",
    )
    redis_url: str = "redis://localhost:6379/0"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "laep-documents"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    refresh_token_minutes: int = 60 * 24 * 30

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    break_glass_username: str = "local-admin"
    break_glass_password: str = "change-me-now"

    ollama_url: str = "http://localhost:11434"
    ollama_timeout_seconds: int = 120
    model_router_default_chat: str = "qwen3.5:4b"
    model_router_default_embed: str = "qwen3-embedding:4b"
    model_router_default_ocr: str = "glm-ocr:latest"
    enable_gpu_auto_detect: bool = True

    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    rate_limit_per_minute: int = 120

    artifacts_dir: Path = Path("artifacts")
    logs_dir: Path = Path("logs")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    return settings
