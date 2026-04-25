"""Provenance tracking: record the origin/source of each secret."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

_KEY = "__provenance__"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_provenance(vault) -> dict[str, Any]:
    raw = vault.get(_KEY)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _save_provenance(vault, data: dict[str, Any]) -> None:
    vault.set(_KEY, json.dumps(data))
    vault.save()


def set_provenance(
    vault,
    key: str,
    source: str,
    author: str | None = None,
    note: str | None = None,
) -> None:
    """Record the provenance of a secret."""
    data = _load_provenance(vault)
    data[key] = {
        "source": source,
        "author": author,
        "note": note,
        "recorded_at": _now_iso(),
    }
    _save_provenance(vault, data)


def clear_provenance(vault, key: str) -> None:
    """Remove provenance information for a secret."""
    data = _load_provenance(vault)
    data.pop(key, None)
    _save_provenance(vault, data)


def get_provenance(vault, key: str) -> dict[str, Any] | None:
    """Return provenance record for a key, or None if not set."""
    return _load_provenance(vault).get(key)


def list_provenance(vault) -> dict[str, dict[str, Any]]:
    """Return all provenance records."""
    return dict(_load_provenance(vault))


def has_provenance(vault, key: str) -> bool:
    """Return True if provenance is recorded for the given key."""
    return key in _load_provenance(vault)
