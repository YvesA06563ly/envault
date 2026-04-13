"""Access control: per-secret read/write permissions tied to named profiles."""

from __future__ import annotations

import json
from typing import Dict, List, Optional

_ACCESS_KEY = "__access_control__"


def _load_acl(vault) -> Dict[str, Dict[str, List[str]]]:
    """Return the full ACL dict: {secret_key: {read: [...], write: [...]}}."""
    raw = vault.get(_ACCESS_KEY)
    if raw is None:
        return {}
    return json.loads(raw)


def _save_acl(vault, acl: Dict[str, Dict[str, List[str]]]) -> None:
    vault.set(_ACCESS_KEY, json.dumps(acl))
    vault.save()


def grant(vault, secret_key: str, profile: str, permission: str) -> None:
    """Grant *profile* the given *permission* ('read' or 'write') on *secret_key*."""
    if permission not in ("read", "write"):
        raise ValueError(f"Invalid permission '{permission}'. Must be 'read' or 'write'.")
    acl = _load_acl(vault)
    entry = acl.setdefault(secret_key, {"read": [], "write": []})
    if profile not in entry[permission]:
        entry[permission].append(profile)
    _save_acl(vault, acl)


def revoke(vault, secret_key: str, profile: str, permission: str) -> None:
    """Revoke *profile*'s *permission* on *secret_key*."""
    if permission not in ("read", "write"):
        raise ValueError(f"Invalid permission '{permission}'. Must be 'read' or 'write'.")
    acl = _load_acl(vault)
    entry = acl.get(secret_key, {})
    perms: List[str] = entry.get(permission, [])
    if profile in perms:
        perms.remove(profile)
    _save_acl(vault, acl)


def can(vault, secret_key: str, profile: str, permission: str) -> bool:
    """Return True if *profile* holds *permission* on *secret_key*."""
    acl = _load_acl(vault)
    return profile in acl.get(secret_key, {}).get(permission, [])


def list_permissions(vault, secret_key: str) -> Optional[Dict[str, List[str]]]:
    """Return the permission dict for *secret_key*, or None if not configured."""
    acl = _load_acl(vault)
    return acl.get(secret_key)


def list_profile_grants(vault, profile: str) -> Dict[str, List[str]]:
    """Return {secret_key: [permissions]} for everything *profile* can access."""
    acl = _load_acl(vault)
    result: Dict[str, List[str]] = {}
    for key, perms in acl.items():
        granted = [p for p in ("read", "write") if profile in perms.get(p, [])]
        if granted:
            result[key] = granted
    return result
