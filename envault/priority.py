"""Priority management for secrets — assign, update, and query priority levels."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

_META_KEY = "__priority__"

LEVELS = ("low", "normal", "high", "critical")


def _load_priorities(vault) -> Dict[str, str]:
    raw = vault.get(_META_KEY)
    if not raw:
        return {}
    import json
    return json.loads(raw)


def _save_priorities(vault, data: Dict[str, str]) -> None:
    import json
    vault.set(_META_KEY, json.dumps(data))
    vault.save()


def set_priority(vault, key: str, level: str) -> None:
    """Assign a priority level to a secret key."""
    if level not in LEVELS:
        raise ValueError(f"Invalid priority '{level}'. Must be one of: {', '.join(LEVELS)}")
    data = _load_priorities(vault)
    data[key] = level
    _save_priorities(vault, data)


def clear_priority(vault, key: str) -> bool:
    """Remove the priority for a key. Returns True if it existed."""
    data = _load_priorities(vault)
    if key in data:
        del data[key]
        _save_priorities(vault, data)
        return True
    return False


def get_priority(vault, key: str) -> Optional[str]:
    """Return the priority level for a key, or None if unset."""
    return _load_priorities(vault).get(key)


def list_priorities(vault) -> List[Tuple[str, str]]:
    """Return all (key, level) pairs sorted by level severity descending."""
    data = _load_priorities(vault)
    order = {level: i for i, level in enumerate(reversed(LEVELS))}
    return sorted(data.items(), key=lambda kv: order.get(kv[1], 99))


def filter_by_priority(vault, level: str) -> List[str]:
    """Return all keys that have exactly the given priority level."""
    if level not in LEVELS:
        raise ValueError(f"Invalid priority '{level}'. Must be one of: {', '.join(LEVELS)}")
    return [k for k, v in _load_priorities(vault).items() if v == level]
