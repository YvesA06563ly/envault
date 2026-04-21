"""Ownership tracking for vault secrets."""

from __future__ import annotations

from typing import Dict, List, Optional

_OWNERSHIP_KEY = "__ownership__"


def _load_ownership(vault) -> Dict[str, str]:
    raw = vault.get(_OWNERSHIP_KEY)
    if not raw:
        return {}
    import json
    return json.loads(raw)


def _save_ownership(vault, data: Dict[str, str]) -> None:
    import json
    vault.set(_OWNERSHIP_KEY, json.dumps(data))
    vault.save()


def set_owner(vault, key: str, owner: str) -> None:
    """Assign an owner to a secret key."""
    if not owner or not owner.strip():
        raise ValueError("Owner must be a non-empty string.")
    data = _load_ownership(vault)
    data[key] = owner.strip()
    _save_ownership(vault, data)


def clear_owner(vault, key: str) -> None:
    """Remove ownership record for a secret key."""
    data = _load_ownership(vault)
    data.pop(key, None)
    _save_ownership(vault, data)


def get_owner(vault, key: str) -> Optional[str]:
    """Return the owner of a secret key, or None if unset."""
    return _load_ownership(vault).get(key)


def list_owned_by(vault, owner: str) -> List[str]:
    """Return all keys owned by the given owner."""
    data = _load_ownership(vault)
    return sorted(k for k, v in data.items() if v == owner)


def list_all_ownership(vault) -> Dict[str, str]:
    """Return the full ownership mapping."""
    return dict(_load_ownership(vault))
