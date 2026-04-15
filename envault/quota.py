"""Quota management: limit the number of secrets per namespace or vault."""

from __future__ import annotations

from typing import Optional

_QUOTA_KEY = "__quota__"


def _load_quotas(vault) -> dict:
    raw = vault.get(_QUOTA_KEY)
    if raw is None:
        return {}
    import json
    return json.loads(raw)


def _save_quotas(vault, data: dict) -> None:
    import json
    vault.set(_QUOTA_KEY, json.dumps(data))
    vault.save()


def set_quota(vault, scope: str, limit: int) -> None:
    """Set the maximum number of secrets allowed for *scope*."""
    if limit < 1:
        raise ValueError("Quota limit must be a positive integer.")
    data = _load_quotas(vault)
    data[scope] = limit
    _save_quotas(vault, data)


def remove_quota(vault, scope: str) -> bool:
    """Remove the quota for *scope*. Returns True if it existed."""
    data = _load_quotas(vault)
    if scope not in data:
        return False
    del data[scope]
    _save_quotas(vault, data)
    return True


def get_quota(vault, scope: str) -> Optional[int]:
    """Return the quota limit for *scope*, or None if not set."""
    return _load_quotas(vault).get(scope)


def list_quotas(vault) -> dict:
    """Return all quota definitions as {scope: limit}."""
    return dict(_load_quotas(vault))


def check_quota(vault, scope: str, current_count: int) -> bool:
    """Return True if *current_count* is within the quota for *scope*.

    If no quota is defined for *scope*, always returns True.
    """
    limit = get_quota(vault, scope)
    if limit is None:
        return True
    return current_count < limit
