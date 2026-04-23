"""Generic key-level metadata store for envault secrets."""
from __future__ import annotations

from typing import Any

_STORE_KEY = "__metadata__"


def _load_metadata(vault) -> dict[str, dict[str, Any]]:
    raw = vault.get(_STORE_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_metadata(vault, data: dict[str, dict[str, Any]]) -> None:
    vault.set(_STORE_KEY, data)
    vault.save()


def set_metadata(vault, key: str, field: str, value: Any) -> None:
    """Set an arbitrary metadata field on a secret key."""
    data = _load_metadata(vault)
    data.setdefault(key, {})[field] = value
    _save_metadata(vault, data)


def remove_metadata(vault, key: str, field: str) -> bool:
    """Remove a metadata field from a secret key. Returns True if it existed."""
    data = _load_metadata(vault)
    entry = data.get(key, {})
    if field not in entry:
        return False
    del entry[field]
    if not entry:
        data.pop(key, None)
    _save_metadata(vault, data)
    return True


def get_metadata(vault, key: str) -> dict[str, Any]:
    """Return all metadata fields for a secret key."""
    return dict(_load_metadata(vault).get(key, {}))


def get_field(vault, key: str, field: str, default: Any = None) -> Any:
    """Return a single metadata field value, or *default* if absent."""
    return _load_metadata(vault).get(key, {}).get(field, default)


def clear_metadata(vault, key: str) -> None:
    """Remove all metadata for a secret key."""
    data = _load_metadata(vault)
    data.pop(key, None)
    _save_metadata(vault, data)


def list_metadata(vault) -> dict[str, dict[str, Any]]:
    """Return the full metadata mapping for all keys."""
    return dict(_load_metadata(vault))
