"""Vault locking: prevent concurrent writes by acquiring a lock record."""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Optional

_LOCK_KEY = "__envault_lock__"
_DEFAULT_TTL = 30  # seconds


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_ts() -> float:
    return time.time()


def acquire_lock(vault, owner: str, ttl: int = _DEFAULT_TTL) -> bool:
    """Attempt to acquire the vault lock for *owner*.

    Returns True if the lock was acquired, False if already held by someone
    else and still within its TTL.
    """
    raw = vault.get(_LOCK_KEY)
    if raw is not None:
        try:
            parts = raw.split("|")
            held_by, expires_at = parts[0], float(parts[1])
        except (ValueError, IndexError):
            held_by, expires_at = "", 0.0

        if _now_ts() < expires_at and held_by != owner:
            return False

    expires_at = _now_ts() + ttl
    vault.set(_LOCK_KEY, f"{owner}|{expires_at}|{_now_iso()}")
    vault.save()
    return True


def release_lock(vault, owner: str) -> bool:
    """Release the lock if held by *owner*.

    Returns True if released, False if not held by *owner*.
    """
    raw = vault.get(_LOCK_KEY)
    if raw is None:
        return False
    try:
        held_by = raw.split("|")[0]
    except IndexError:
        return False

    if held_by != owner:
        return False

    vault.set(_LOCK_KEY, None)  # clear
    vault.save()
    return True


def lock_status(vault) -> Optional[dict]:
    """Return current lock info or None if unlocked."""
    raw = vault.get(_LOCK_KEY)
    if raw is None:
        return None
    try:
        parts = raw.split("|")
        held_by, expires_at, acquired_at = parts[0], float(parts[1]), parts[2]
    except (ValueError, IndexError):
        return None

    if _now_ts() >= expires_at:
        return None  # expired — treat as unlocked

    return {
        "owner": held_by,
        "expires_at": expires_at,
        "acquired_at": acquired_at,
        "ttl_remaining": max(0.0, expires_at - _now_ts()),
    }
