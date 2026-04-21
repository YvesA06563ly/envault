"""Retention policy management for envault secrets."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

RETENTION_KEY = "__retention__"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_retention(vault) -> dict:
    raw = vault.get(RETENTION_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_retention(vault, data: dict) -> None:
    vault.set(RETENTION_KEY, data)
    vault.save()


def set_retention(vault, key: str, days: int) -> None:
    """Set a retention period (in days) for a secret."""
    if days <= 0:
        raise ValueError("Retention days must be a positive integer.")
    data = _load_retention(vault)
    expires_at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    data[key] = {"days": days, "set_at": _now_iso(), "expires_at": expires_at}
    _save_retention(vault, data)


def clear_retention(vault, key: str) -> bool:
    """Remove the retention policy for a secret. Returns True if removed."""
    data = _load_retention(vault)
    if key in data:
        del data[key]
        _save_retention(vault, data)
        return True
    return False


def get_retention(vault, key: str) -> Optional[dict]:
    """Return the retention record for a key, or None."""
    return _load_retention(vault).get(key)


def is_expired(vault, key: str) -> bool:
    """Return True if the secret has exceeded its retention period."""
    record = get_retention(vault, key)
    if record is None:
        return False
    expires_at = datetime.fromisoformat(record["expires_at"])
    return datetime.now(timezone.utc) >= expires_at


def list_expired(vault) -> List[str]:
    """Return a list of secret keys whose retention period has expired."""
    data = _load_retention(vault)
    now = datetime.now(timezone.utc)
    return [
        key
        for key, record in data.items()
        if now >= datetime.fromisoformat(record["expires_at"])
    ]


def list_retention(vault) -> List[dict]:
    """Return all retention entries as a list of dicts with the key included."""
    data = _load_retention(vault)
    return [{"key": k, **v} for k, v in data.items()]
