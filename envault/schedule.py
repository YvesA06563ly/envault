"""Scheduled rotation management for envault secrets."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional

_SCHEDULE_KEY = "__envault_schedule__"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_schedules(vault) -> dict:
    raw = vault.get(_SCHEDULE_KEY)
    if raw is None:
        return {}
    import json
    return json.loads(raw)


def _save_schedules(vault, data: dict) -> None:
    import json
    vault.set(_SCHEDULE_KEY, json.dumps(data))
    vault.save()


def set_schedule(vault, key: str, interval_days: int, notify: bool = False) -> None:
    """Schedule automatic rotation for *key* every *interval_days* days."""
    if interval_days < 1:
        raise ValueError("interval_days must be >= 1")
    schedules = _load_schedules(vault)
    schedules[key] = {
        "interval_days": interval_days,
        "notify": notify,
        "created_at": _now_iso(),
    }
    _save_schedules(vault, schedules)


def remove_schedule(vault, key: str) -> bool:
    """Remove the rotation schedule for *key*. Returns True if it existed."""
    schedules = _load_schedules(vault)
    if key not in schedules:
        return False
    del schedules[key]
    _save_schedules(vault, schedules)
    return True


def get_schedule(vault, key: str) -> Optional[dict]:
    """Return the schedule entry for *key*, or None."""
    return _load_schedules(vault).get(key)


def list_schedules(vault) -> dict:
    """Return all scheduled keys and their settings."""
    return dict(_load_schedules(vault))


def due_keys(vault, last_rotated_fn) -> list[str]:
    """Return keys whose rotation interval has elapsed.

    *last_rotated_fn* is a callable(key) -> Optional[datetime].
    """
    schedules = _load_schedules(vault)
    now = datetime.now(timezone.utc)
    result = []
    for key, cfg in schedules.items():
        lr = last_rotated_fn(key)
        if lr is None:
            result.append(key)
            continue
        if isinstance(lr, str):
            lr = datetime.fromisoformat(lr)
        delta = timedelta(days=cfg["interval_days"])
        if now - lr >= delta:
            result.append(key)
    return result
