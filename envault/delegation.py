"""Delegation: allow one identity to act on behalf of another for specific secrets."""

from __future__ import annotations

import json
from typing import Dict, List, Optional

_DELEGATION_KEY = "__delegations__"


def _load_delegations(vault) -> Dict[str, List[Dict]]:
    raw = vault.get(_DELEGATION_KEY)
    if not raw:
        return {}
    return json.loads(raw)


def _save_delegations(vault, data: Dict[str, List[Dict]]) -> None:
    vault.set(_DELEGATION_KEY, json.dumps(data))
    vault.save()


def delegate(vault, secret_key: str, delegator: str, delegate_to: str, permissions: Optional[List[str]] = None) -> None:
    """Grant delegate_to the ability to act on behalf of delegator for secret_key."""
    data = _load_delegations(vault)
    entries = data.setdefault(secret_key, [])
    # Remove existing entry for same delegator/delegate pair
    entries = [e for e in entries if not (e["delegator"] == delegator and e["delegate"] == delegate_to)]
    entries.append({
        "delegator": delegator,
        "delegate": delegate_to,
        "permissions": permissions or ["read"],
    })
    data[secret_key] = entries
    _save_delegations(vault, data)


def revoke_delegation(vault, secret_key: str, delegator: str, delegate_to: str) -> bool:
    """Revoke a delegation. Returns True if a record was removed."""
    data = _load_delegations(vault)
    entries = data.get(secret_key, [])
    new_entries = [e for e in entries if not (e["delegator"] == delegator and e["delegate"] == delegate_to)]
    if len(new_entries) == len(entries):
        return False
    data[secret_key] = new_entries
    if not data[secret_key]:
        del data[secret_key]
    _save_delegations(vault, data)
    return True


def get_delegations(vault, secret_key: str) -> List[Dict]:
    """Return all delegation records for a given secret."""
    data = _load_delegations(vault)
    return data.get(secret_key, [])


def can_delegate(vault, secret_key: str, identity: str, permission: str = "read") -> bool:
    """Check whether identity has been delegated a specific permission for secret_key."""
    for entry in get_delegations(vault, secret_key):
        if entry["delegate"] == identity and permission in entry.get("permissions", []):
            return True
    return False


def list_all_delegations(vault) -> Dict[str, List[Dict]]:
    """Return the full delegation map."""
    return _load_delegations(vault)
