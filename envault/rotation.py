"""Secret rotation logic for envault."""

from __future__ import annotations

import datetime
from typing import Optional

ROTATION_META_KEY = "__rotation_meta__"


def get_rotation_meta(vault) -> dict:
    """Retrieve rotation metadata stored inside the vault."""
    raw = vault.secrets.get(ROTATION_META_KEY, {})
    if isinstance(raw, str):
        import json
        try:
            return json.loads(raw)
        except Exception:
            return {}
    return raw


def set_rotation_meta(vault, meta: dict) -> None:
    """Persist rotation metadata inside the vault."""
    import json
    vault.secrets[ROTATION_META_KEY] = json.dumps(meta)
    vault.save()


def record_rotation(vault, key: str) -> None:
    """Record the current UTC timestamp as the last rotation time for *key*."""
    meta = get_rotation_meta(vault)
    meta[key] = datetime.datetime.utcnow().isoformat()
    set_rotation_meta(vault, meta)


def last_rotated(vault, key: str) -> Optional[datetime.datetime]:
    """Return the last rotation datetime for *key*, or None if never rotated."""
    meta = get_rotation_meta(vault)
    ts = meta.get(key)
    if ts is None:
        return None
    return datetime.datetime.fromisoformat(ts)


def needs_rotation(vault, key: str, max_age_days: int = 90) -> bool:
    """Return True if *key* has not been rotated within *max_age_days* days."""
    rotated_at = last_rotated(vault, key)
    if rotated_at is None:
        return True
    age = datetime.datetime.utcnow() - rotated_at
    return age.days >= max_age_days


def rotate_secret(vault, key: str, new_value: str) -> None:
    """Replace the value of *key* with *new_value* and record the rotation time."""
    if key == ROTATION_META_KEY:
        raise ValueError(f"Cannot rotate reserved key '{ROTATION_META_KEY}'.")
    vault.set(key, new_value)
    record_rotation(vault, key)
