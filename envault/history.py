"""Secret value history tracking for envault."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

_HISTORY_KEY = "__history__"
_MAX_ENTRIES = 20


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_history(vault: Any) -> dict:
    raw = vault.get(_HISTORY_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_history(vault: Any, data: dict) -> None:
    vault.set(_HISTORY_KEY, data)
    vault.save()


def record_history(vault: Any, key: str, old_value: str | None, new_value: str) -> None:
    """Append a history entry for *key* whenever its value changes."""
    data = _load_history(vault)
    entries = data.get(key, [])
    entries.append({"value": new_value, "previous": old_value, "timestamp": _now_iso()})
    if len(entries) > _MAX_ENTRIES:
        entries = entries[-_MAX_ENTRIES:]
    data[key] = entries
    _save_history(vault, data)


def get_history(vault: Any, key: str) -> list[dict]:
    """Return the history list for *key* (oldest first)."""
    data = _load_history(vault)
    return list(data.get(key, []))


def clear_history(vault: Any, key: str) -> bool:
    """Remove all history for *key*. Returns True if there was anything to clear."""
    data = _load_history(vault)
    if key not in data:
        return False
    del data[key]
    _save_history(vault, data)
    return True


def list_keys_with_history(vault: Any) -> list[str]:
    """Return all secret keys that have at least one history entry."""
    data = _load_history(vault)
    return [k for k, v in data.items() if v]
