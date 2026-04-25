"""Endorsement module: allow users to endorse secrets as verified/trusted."""

from __future__ import annotations

from typing import Any

_KEY = "__endorsements__"


def _load_endorsements(vault: Any) -> dict:
    raw = vault.get(_KEY)
    return raw if isinstance(raw, dict) else {}


def _save_endorsements(vault: Any, data: dict) -> None:
    vault.set(_KEY, data)
    vault.save()


def endorse(vault: Any, key: str, user: str) -> None:
    """Add a user endorsement to a secret."""
    data = _load_endorsements(vault)
    endorsers = set(data.get(key, []))
    endorsers.add(user)
    data[key] = sorted(endorsers)
    _save_endorsements(vault, data)


def revoke_endorsement(vault: Any, key: str, user: str) -> bool:
    """Remove a user endorsement from a secret. Returns True if removed."""
    data = _load_endorsements(vault)
    endorsers = set(data.get(key, []))
    if user not in endorsers:
        return False
    endorsers.discard(user)
    if endorsers:
        data[key] = sorted(endorsers)
    else:
        data.pop(key, None)
    _save_endorsements(vault, data)
    return True


def get_endorsers(vault: Any, key: str) -> list[str]:
    """Return the list of users who have endorsed a secret."""
    data = _load_endorsements(vault)
    return list(data.get(key, []))


def is_endorsed_by(vault: Any, key: str, user: str) -> bool:
    """Check whether a specific user has endorsed a secret."""
    return user in get_endorsers(vault, key)


def endorsement_count(vault: Any, key: str) -> int:
    """Return the number of endorsements for a secret."""
    return len(get_endorsers(vault, key))


def list_endorsed(vault: Any) -> dict[str, list[str]]:
    """Return all secrets that have at least one endorsement."""
    return {k: v for k, v in _load_endorsements(vault).items() if v}
