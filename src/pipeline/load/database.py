from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine


def get_engine(url: str | None = None) -> Engine:
    """Create an engine from DATABASE_URL (loaded from .env if present)."""
    load_dotenv()
    url = url or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env.")
    return create_engine(url, pool_pre_ping=True)
