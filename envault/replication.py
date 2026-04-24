"""Replication support for envault.

Allows secrets (or subsets) to be replicated from one vault namespace/profile
to another, tracking which keys are replicated and when the last sync occurred.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

_REPLICATION_KEY = "__replication__"


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _load_replication(vault: Any) -> dict:
    """Load the replication registry from the vault."""
    raw = vault.get(_REPLICATION_KEY)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _save_replication(vault: Any, data: dict) -> None:
    """Persist the replication registry back to the vault."""
    vault.set(_REPLICATION_KEY, json.dumps(data))
    vault.save()


def add_replication(
    vault: Any,
    rule_name: str,
    source_keys: list[str],
    target_profile: str,
) -> dict:
    """Register a replication rule.

    Args:
        vault: The Vault instance to operate on.
        rule_name: A unique identifier for this replication rule.
        source_keys: List of secret keys to replicate.
        target_profile: Name of the target vault profile / deployment target.

    Returns:
        The newly created rule dict.
    """
    data = _load_replication(vault)
    rule = {
        "rule_name": rule_name,
        "source_keys": list(source_keys),
        "target_profile": target_profile,
        "created_at": _now_iso(),
        "last_synced": None,
    }
    data[rule_name] = rule
    _save_replication(vault, data)
    return rule


def remove_replication(vault: Any, rule_name: str) -> bool:
    """Remove a replication rule by name.

    Returns True if the rule existed and was removed, False otherwise.
    """
    data = _load_replication(vault)
    if rule_name not in data:
        return False
    del data[rule_name]
    _save_replication(vault, data)
    return True


def get_replication(vault: Any, rule_name: str) -> dict | None:
    """Retrieve a single replication rule, or None if not found."""
    return _load_replication(vault).get(rule_name)


def list_replications(vault: Any) -> list[dict]:
    """Return all registered replication rules as a list."""
    return list(_load_replication(vault).values())


def record_sync(vault: Any, rule_name: str) -> dict | None:
    """Mark a replication rule as synced right now.

    Returns the updated rule dict, or None if the rule does not exist.
    """
    data = _load_replication(vault)
    if rule_name not in data:
        return None
    data[rule_name]["last_synced"] = _now_iso()
    _save_replication(vault, data)
    return data[rule_name]


def update_source_keys(
    vault: Any, rule_name: str, source_keys: list[str]
) -> dict | None:
    """Replace the source_keys list for an existing replication rule.

    Returns the updated rule dict, or None if the rule does not exist.
    """
    data = _load_replication(vault)
    if rule_name not in data:
        return None
    data[rule_name]["source_keys"] = list(source_keys)
    _save_replication(vault, data)
    return data[rule_name]
