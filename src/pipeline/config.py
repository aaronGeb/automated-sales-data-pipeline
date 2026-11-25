from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # extra="ignore": .env also holds POSTGRES_* values used by docker compose
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    schema_path: Path = Path("config/schemas/sales_schema.yaml")
    processed_dir: Path = Path("data/processed")
    rejected_dir: Path = Path("data/rejected")
    log_dir: Path = Path("logs")


@lru_cache
def get_settings() -> Settings:
    return Settings()
