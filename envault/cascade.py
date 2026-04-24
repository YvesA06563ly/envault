"""Cascade: propagate secret changes to dependent secrets automatically."""

from __future__ import annotations

from typing import Any

_CASCADE_KEY = "__cascade__"


def _load_cascade(vault: Any) -> dict:
    raw = vault.get(_CASCADE_KEY)
    if not raw:
        return {}
    import json
    return json.loads(raw)


def _save_cascade(vault: Any, data: dict) -> None:
    import json
    vault.set(_CASCADE_KEY, json.dumps(data))
    vault.save()


def add_cascade(vault: Any, source_key: str, target_key: str) -> None:
    """Register that target_key should be updated whenever source_key changes."""
    data = _load_cascade(vault)
    targets = set(data.get(source_key, []))
    targets.add(target_key)
    data[source_key] = sorted(targets)
    _save_cascade(vault, data)


def remove_cascade(vault: Any, source_key: str, target_key: str) -> bool:
    """Remove a cascade link. Returns True if it existed."""
    data = _load_cascade(vault)
    targets = set(data.get(source_key, []))
    if target_key not in targets:
        return False
    targets.discard(target_key)
    if targets:
        data[source_key] = sorted(targets)
    else:
        data.pop(source_key, None)
    _save_cascade(vault, data)
    return True


def list_cascade(vault: Any, source_key: str) -> list[str]:
    """Return all target keys that cascade from source_key."""
    data = _load_cascade(vault)
    return data.get(source_key, [])


def list_all_cascades(vault: Any) -> dict[str, list[str]]:
    """Return the full cascade mapping."""
    return _load_cascade(vault)


def resolve_cascade(vault: Any, source_key: str, visited: set[str] | None = None) -> list[str]:
    """Recursively resolve all downstream keys from source_key (cycle-safe)."""
    if visited is None:
        visited = set()
    if source_key in visited:
        return []
    visited.add(source_key)
    data = _load_cascade(vault)
    result = []
    for target in data.get(source_key, []):
        result.append(target)
        result.extend(resolve_cascade(vault, target, visited))
    return result
