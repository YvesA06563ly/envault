"""Visibility control for secrets (public / private / restricted)."""

from __future__ import annotations

from typing import Dict, List, Optional

VISIBILITY_KEY = "__visibility__"
VALID_LEVELS = {"public", "private", "restricted"}
DEFAULT_LEVEL = "private"


def _load_visibility(vault) -> Dict[str, str]:
    raw = vault.get(VISIBILITY_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_visibility(vault, data: Dict[str, str]) -> None:
    vault.set(VISIBILITY_KEY, data)
    vault.save()


def set_visibility(vault, key: str, level: str) -> None:
    """Set the visibility level for *key*."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid visibility level '{level}'. Choose from: {sorted(VALID_LEVELS)}")
    data = _load_visibility(vault)
    data[key] = level
    _save_visibility(vault, data)


def clear_visibility(vault, key: str) -> None:
    """Remove explicit visibility for *key* (falls back to default)."""
    data = _load_visibility(vault)
    data.pop(key, None)
    _save_visibility(vault, data)


def get_visibility(vault, key: str) -> str:
    """Return the visibility level for *key*, defaulting to 'private'."""
    data = _load_visibility(vault)
    return data.get(key, DEFAULT_LEVEL)


def list_visibility(vault) -> Dict[str, str]:
    """Return a mapping of all keys with explicit visibility settings."""
    return dict(_load_visibility(vault))


def find_by_visibility(vault, level: str) -> List[str]:
    """Return all keys that have the given visibility level."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid visibility level '{level}'. Choose from: {sorted(VALID_LEVELS)}")
    data = _load_visibility(vault)
    return [k for k, v in data.items() if v == level]
