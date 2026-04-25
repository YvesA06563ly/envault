"""Secret versioning: track value versions for each secret key."""
from __future__ import annotations

from typing import Any

_VERSIONING_KEY = "__versioning__"


def _load_versions(vault: Any) -> dict:
    raw = vault.get(_VERSIONING_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_versions(vault: Any, versions: dict) -> None:
    vault.set(_VERSIONING_KEY, versions)
    vault.save()


def record_version(vault: Any, key: str, value: str) -> int:
    """Append *value* to the version history of *key*.

    Returns the new version number (1-based).
    """
    versions = _load_versions(vault)
    history: list = versions.get(key, [])
    history.append(value)
    versions[key] = history
    _save_versions(vault, versions)
    return len(history)


def get_versions(vault: Any, key: str) -> list[str]:
    """Return the full version history list for *key* (oldest first)."""
    versions = _load_versions(vault)
    return list(versions.get(key, []))


def get_version(vault: Any, key: str, version: int) -> str | None:
    """Return a specific 1-based *version* of *key*, or None if not found."""
    history = get_versions(vault, key)
    if version < 1 or version > len(history):
        return None
    return history[version - 1]


def latest_version(vault: Any, key: str) -> int:
    """Return the current (latest) version number for *key*, or 0 if none."""
    return len(get_versions(vault, key))


def purge_versions(vault: Any, key: str, keep: int = 0) -> int:
    """Remove old versions of *key*, keeping the most recent *keep* entries.

    Passing ``keep=0`` removes all version history for *key*.
    Returns the number of entries removed.
    """
    versions = _load_versions(vault)
    history: list = versions.get(key, [])
    removed = max(0, len(history) - keep)
    versions[key] = history[-keep:] if keep > 0 else []
    _save_versions(vault, versions)
    return removed


def list_versioned_keys(vault: Any) -> list[str]:
    """Return all keys that have at least one recorded version."""
    versions = _load_versions(vault)
    return [k for k, v in versions.items() if v]
