"""Freeze/unfreeze secrets to prevent accidental modification."""

from __future__ import annotations

from typing import List

_FREEZE_KEY = "__freeze__"


def _load_frozen(vault) -> dict:
    raw = vault.get(_FREEZE_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_frozen(vault, data: dict) -> None:
    vault.set(_FREEZE_KEY, data)
    vault.save()


def freeze(vault, key: str) -> None:
    """Mark *key* as frozen; raises KeyError if the secret does not exist."""
    secrets = vault.load()
    if key not in secrets:
        raise KeyError(f"Secret '{key}' not found")
    data = _load_frozen(vault)
    data[key] = True
    _save_frozen(vault, data)


def unfreeze(vault, key: str) -> None:
    """Remove the frozen mark from *key*."""
    data = _load_frozen(vault)
    data.pop(key, None)
    _save_frozen(vault, data)


def is_frozen(vault, key: str) -> bool:
    """Return True if *key* is currently frozen."""
    data = _load_frozen(vault)
    return bool(data.get(key, False))


def list_frozen(vault) -> List[str]:
    """Return a sorted list of all frozen secret keys."""
    data = _load_frozen(vault)
    return sorted(k for k, v in data.items() if v)


def assert_not_frozen(vault, key: str) -> None:
    """Raise PermissionError if *key* is frozen."""
    if is_frozen(vault, key):
        raise PermissionError(
            f"Secret '{key}' is frozen and cannot be modified. "
            "Unfreeze it first with: envault freeze unfreeze {key}"
        )
