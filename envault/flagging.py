"""Secret flagging — mark secrets with status flags (e.g. suspicious, stale, reviewed)."""

from __future__ import annotations

from typing import Dict, List, Optional

VALID_FLAGS = {"suspicious", "stale", "reviewed", "deprecated", "needs-rotation"}

_STORE_KEY = "__flagging__"


def _load_flags(vault) -> Dict[str, List[str]]:
    raw = vault.get(_STORE_KEY)
    if not raw:
        return {}
    import json
    return json.loads(raw)


def _save_flags(vault, data: Dict[str, List[str]]) -> None:
    import json
    vault.set(_STORE_KEY, json.dumps(data))
    vault.save()


def add_flag(vault, key: str, flag: str) -> None:
    """Add a flag to a secret. Raises ValueError for unknown flags."""
    if flag not in VALID_FLAGS:
        raise ValueError(f"Unknown flag '{flag}'. Valid flags: {sorted(VALID_FLAGS)}")
    data = _load_flags(vault)
    flags = data.get(key, [])
    if flag not in flags:
        flags.append(flag)
    data[key] = flags
    _save_flags(vault, data)


def remove_flag(vault, key: str, flag: str) -> bool:
    """Remove a flag from a secret. Returns True if removed, False if not present."""
    data = _load_flags(vault)
    flags = data.get(key, [])
    if flag not in flags:
        return False
    flags.remove(flag)
    if flags:
        data[key] = flags
    else:
        data.pop(key, None)
    _save_flags(vault, data)
    return True


def get_flags(vault, key: str) -> List[str]:
    """Return all flags set on a secret."""
    return _load_flags(vault).get(key, [])


def has_flag(vault, key: str, flag: str) -> bool:
    """Check whether a secret has a specific flag."""
    return flag in get_flags(vault, key)


def list_flagged(vault, flag: Optional[str] = None) -> Dict[str, List[str]]:
    """Return all flagged secrets, optionally filtered by a specific flag."""
    data = _load_flags(vault)
    if flag is None:
        return {k: v for k, v in data.items() if v}
    return {k: v for k, v in data.items() if flag in v}


def clear_flags(vault, key: str) -> None:
    """Remove all flags from a secret."""
    data = _load_flags(vault)
    data.pop(key, None)
    _save_flags(vault, data)
