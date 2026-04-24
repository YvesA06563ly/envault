"""Read-only protection for secrets in the vault."""

from __future__ import annotations

import json
from typing import List

_READONLY_KEY = "__readonly__"


def _load_readonly(vault) -> dict:
    raw = vault.get(_READONLY_KEY)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _save_readonly(vault, data: dict) -> None:
    vault.set(_READONLY_KEY, json.dumps(data))
    vault.save()


def protect(vault, key: str) -> None:
    """Mark a secret as read-only, preventing modification or deletion."""
    data = _load_readonly(vault)
    data[key] = True
    _save_readonly(vault, data)


def unprotect(vault, key: str) -> None:
    """Remove read-only protection from a secret."""
    data = _load_readonly(vault)
    data.pop(key, None)
    _save_readonly(vault, data)


def is_protected(vault, key: str) -> bool:
    """Return True if the secret is currently read-only."""
    data = _load_readonly(vault)
    return bool(data.get(key, False))


def list_protected(vault) -> List[str]:
    """Return a sorted list of all read-only secret keys."""
    data = _load_readonly(vault)
    return sorted(k for k, v in data.items() if v)


def assert_writable(vault, key: str) -> None:
    """Raise a PermissionError if the secret is read-only."""
    if is_protected(vault, key):
        raise PermissionError(
            f"Secret '{key}' is read-only and cannot be modified or deleted."
        )
