"""TTL (time-to-live) management for secrets.

Stores a duration (in seconds) after which a secret should be considered
stale.  Unlike hard expiry, TTL is relative to when the secret was last
written (recorded in history) rather than a fixed wall-clock deadline.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from typing import Optional

_TTL_KEY = "__ttl__"


def _load_ttls(vault) -> dict:
    raw = vault.get(_TTL_KEY)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _save_ttls(vault, data: dict) -> None:
    vault.set(_TTL_KEY, json.dumps(data))
    vault.save()


def set_ttl(vault, key: str, seconds: int) -> None:
    """Attach a TTL (in seconds) to *key*."""
    if seconds <= 0:
        raise ValueError("TTL must be a positive number of seconds.")
    ttls = _load_ttls(vault)
    ttls[key] = seconds
    _save_ttls(vault, ttls)


def clear_ttl(vault, key: str) -> None:
    """Remove the TTL for *key* (if any)."""
    ttls = _load_ttls(vault)
    ttls.pop(key, None)
    _save_ttls(vault, ttls)


def get_ttl(vault, key: str) -> Optional[int]:
    """Return the TTL in seconds for *key*, or None if not set."""
    return _load_ttls(vault).get(key)


def is_stale(vault, key: str, last_written: Optional[datetime]) -> bool:
    """Return True if *key* has exceeded its TTL relative to *last_written*.

    If no TTL is set, or *last_written* is None, the secret is never stale.
    """
    ttl = get_ttl(vault, key)
    if ttl is None or last_written is None:
        return False
    now = datetime.now(tz=timezone.utc)
    if last_written.tzinfo is None:
        last_written = last_written.replace(tzinfo=timezone.utc)
    return (now - last_written) > timedelta(seconds=ttl)


def list_ttls(vault) -> dict:
    """Return a mapping of key -> TTL seconds for all keys that have a TTL."""
    return dict(_load_ttls(vault))
