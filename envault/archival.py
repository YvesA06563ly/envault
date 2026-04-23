"""Archival module: mark secrets as archived and filter them from active listings."""

from __future__ import annotations

from typing import List

_STORE_KEY = "__archival__"


def _load_archive(vault) -> dict:
    raw = vault.get(_STORE_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_archive(vault, data: dict) -> None:
    vault.set(_STORE_KEY, data)
    vault.save()


def archive_secret(vault, key: str) -> None:
    """Mark *key* as archived."""
    data = _load_archive(vault)
    data[key] = True
    _save_archive(vault, data)


def unarchive_secret(vault, key: str) -> None:
    """Remove the archived mark from *key*."""
    data = _load_archive(vault)
    data.pop(key, None)
    _save_archive(vault, data)


def is_archived(vault, key: str) -> bool:
    """Return True if *key* is currently archived."""
    return _load_archive(vault).get(key, False)


def list_archived(vault) -> List[str]:
    """Return all keys that are archived."""
    return [k for k, v in _load_archive(vault).items() if v]


def filter_active(vault, keys: List[str]) -> List[str]:
    """Return only the keys from *keys* that are NOT archived."""
    archived = set(list_archived(vault))
    return [k for k in keys if k not in archived]
