from __future__ import annotations

from datetime import datetime, timezone
import os


def env(name: str, default: str | None = None) -> str:
    """Fetch and validate an env var as a non-empty string."""
    value = os.getenv(name, default)
    if value is None or str(value).strip() == "":
        raise RuntimeError(f"Missing env var: {name}")
    return str(value).strip()


def now_utc_iso() -> str:
    """Return a UTC ISO-8601 timestamp for ingestion metadata."""
    return datetime.now(timezone.utc).isoformat()
