"""Sensitivity classification for secrets (low, medium, high, critical)."""

from __future__ import annotations

from typing import Dict, List, Optional

VALID_LEVELS = ("low", "medium", "high", "critical")
_KEY = "__sensitivity__"


def _load_sensitivity(vault) -> Dict[str, str]:
    raw = vault.get(_KEY)
    if isinstance(raw, dict):
        return dict(raw)
    return {}


def _save_sensitivity(vault, data: Dict[str, str]) -> None:
    vault.set(_KEY, data)
    vault.save()


def set_sensitivity(vault, key: str, level: str) -> None:
    """Assign a sensitivity level to a secret key."""
    level = level.lower()
    if level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid sensitivity level '{level}'. Choose from: {', '.join(VALID_LEVELS)}"
        )
    data = _load_sensitivity(vault)
    data[key] = level
    _save_sensitivity(vault, data)


def clear_sensitivity(vault, key: str) -> None:
    """Remove the sensitivity classification for a secret key."""
    data = _load_sensitivity(vault)
    data.pop(key, None)
    _save_sensitivity(vault, data)


def get_sensitivity(vault, key: str) -> Optional[str]:
    """Return the sensitivity level for a secret key, or None."""
    return _load_sensitivity(vault).get(key)


def list_by_level(vault, level: str) -> List[str]:
    """Return all keys classified at a given sensitivity level."""
    level = level.lower()
    if level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid sensitivity level '{level}'. Choose from: {', '.join(VALID_LEVELS)}"
        )
    data = _load_sensitivity(vault)
    return sorted(k for k, v in data.items() if v == level)


def list_all(vault) -> Dict[str, str]:
    """Return a mapping of all keys to their sensitivity levels."""
    return dict(_load_sensitivity(vault))
