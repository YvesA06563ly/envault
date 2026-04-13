"""Secret expiry management for envault."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional

_META_KEY = "__expiry_meta__"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_expiry(vault) -> dict:
    raw = vault.get(_META_KEY)
    if raw is None:
        return {}
    import json
    return json.loads(raw)


def _save_expiry(vault, data: dict) -> None:
    import json
    vault.set(_META_KEY, json.dumps(data))
    vault.save()


def set_expiry(vault, key: str, days: int) -> datetime:
    """Set an expiry date for *key* that is *days* days from now."""
    if days <= 0:
        raise ValueError("days must be a positive integer")
    data = _load_expiry(vault)
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    data[key] = expires_at.isoformat()
    _save_expiry(vault, data)
    return expires_at


def clear_expiry(vault, key: str) -> bool:
    """Remove expiry for *key*. Returns True if an entry existed."""
    data = _load_expiry(vault)
    if key in data:
        del data[key]
        _save_expiry(vault, data)
        return True
    return False


def get_expiry(vault, key: str) -> Optional[datetime]:
    """Return the expiry datetime for *key*, or None if not set."""
    data = _load_expiry(vault)
    raw = data.get(key)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def is_expired(vault, key: str) -> bool:
    """Return True if *key* has passed its expiry date."""
    expiry = get_expiry(vault, key)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def list_expiring(vault, within_days: int = 7) -> list[dict]:
    """Return secrets expiring within *within_days* days, sorted soonest first."""
    data = _load_expiry(vault)
    cutoff = datetime.now(timezone.utc) + timedelta(days=within_days)
    now = datetime.now(timezone.utc)
    results = []
    for key, raw in data.items():
        expiry = datetime.fromisoformat(raw)
        if expiry <= cutoff:
            results.append({
                "key": key,
                "expires_at": expiry,
                "expired": expiry < now,
            })
    results.sort(key=lambda r: r["expires_at"])
    return results
