"""Snapshot: capture and restore vault secret snapshots."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

_SNAPSHOT_KEY = "__snapshots__"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_snapshots(vault: Any) -> dict:
    raw = vault.get(_SNAPSHOT_KEY)
    if raw is None:
        return {}
    return json.loads(raw)


def _save_snapshots(vault: Any, snapshots: dict) -> None:
    vault.set(_SNAPSHOT_KEY, json.dumps(snapshots))
    vault.save()


def create_snapshot(vault: Any, name: str, keys: list[str]) -> dict:
    """Capture current values of *keys* into a named snapshot."""
    snapshots = _load_snapshots(vault)
    data = {}
    for key in keys:
        value = vault.get(key)
        if value is not None:
            data[key] = value
    entry = {"created_at": _now_iso(), "secrets": data}
    snapshots[name] = entry
    _save_snapshots(vault, snapshots)
    return entry


def restore_snapshot(vault: Any, name: str) -> list[str]:
    """Restore secrets from a named snapshot. Returns list of restored keys."""
    snapshots = _load_snapshots(vault)
    if name not in snapshots:
        raise KeyError(f"Snapshot '{name}' not found.")
    restored = []
    for key, value in snapshots[name]["secrets"].items():
        vault.set(key, value)
        restored.append(key)
    vault.save()
    return restored


def list_snapshots(vault: Any) -> list[dict]:
    """Return all snapshots with name and metadata."""
    snapshots = _load_snapshots(vault)
    return [
        {"name": name, "created_at": meta["created_at"], "keys": list(meta["secrets"].keys())}
        for name, meta in snapshots.items()
    ]


def delete_snapshot(vault: Any, name: str) -> None:
    """Remove a named snapshot."""
    snapshots = _load_snapshots(vault)
    if name not in snapshots:
        raise KeyError(f"Snapshot '{name}' not found.")
    del snapshots[name]
    _save_snapshots(vault, snapshots)
