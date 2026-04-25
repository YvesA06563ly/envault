"""Trust level management for secrets.

Allows assigning a trust level (low, medium, high, verified) to secrets,
which can be used by policies, scoring, and compliance checks.
"""

from __future__ import annotations

from typing import Dict, List, Optional

VALID_LEVELS = ("low", "medium", "high", "verified")
_KEY = "__trustlevels__"


def _load_trust(vault) -> Dict[str, str]:
    raw = vault.get(_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_trust(vault, data: Dict[str, str]) -> None:
    vault.set(_KEY, data)
    vault.save()


def set_trust(vault, key: str, level: str) -> None:
    """Assign a trust level to a secret key."""
    if level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid trust level {level!r}. Choose from: {', '.join(VALID_LEVELS)}"
        )
    data = _load_trust(vault)
    data[key] = level
    _save_trust(vault, data)


def clear_trust(vault, key: str) -> None:
    """Remove the trust level for a secret key."""
    data = _load_trust(vault)
    data.pop(key, None)
    _save_trust(vault, data)


def get_trust(vault, key: str) -> Optional[str]:
    """Return the trust level for a secret key, or None if unset."""
    return _load_trust(vault).get(key)


def list_by_trust(vault, level: str) -> List[str]:
    """Return all secret keys assigned the given trust level."""
    if level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid trust level {level!r}. Choose from: {', '.join(VALID_LEVELS)}"
        )
    data = _load_trust(vault)
    return sorted(k for k, v in data.items() if v == level)


def all_trust_levels(vault) -> Dict[str, str]:
    """Return a mapping of all keys to their assigned trust levels."""
    return dict(_load_trust(vault))
