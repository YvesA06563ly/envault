"""Deployment target management for envault.

Targets represent named deployment environments (e.g. production, staging)
that secrets can be pushed to or synced with.
"""

from __future__ import annotations

from typing import Dict, List, Optional

TARGETS_KEY = "__targets__"


def _get_targets(vault) -> Dict[str, dict]:
    """Retrieve the targets registry from the vault."""
    raw = vault.get(TARGETS_KEY)
    if raw is None:
        return {}
    import json
    return json.loads(raw)


def _save_targets(vault, targets: Dict[str, dict]) -> None:
    """Persist the targets registry back to the vault."""
    import json
    vault.set(TARGETS_KEY, json.dumps(targets))
    vault.save()


def add_target(vault, name: str, url: str, description: str = "") -> None:
    """Register a new deployment target.

    Args:
        vault: Vault instance.
        name: Unique target identifier (e.g. 'production').
        url: Target endpoint or identifier string.
        description: Optional human-readable description.

    Raises:
        ValueError: If a target with the given name already exists.
    """
    targets = _get_targets(vault)
    if name in targets:
        raise ValueError(f"Target '{name}' already exists.")
    targets[name] = {"url": url, "description": description}
    _save_targets(vault, targets)


def remove_target(vault, name: str) -> None:
    """Remove a registered deployment target.

    Raises:
        KeyError: If the target does not exist.
    """
    targets = _get_targets(vault)
    if name not in targets:
        raise KeyError(f"Target '{name}' not found.")
    del targets[name]
    _save_targets(vault, targets)


def list_targets(vault) -> List[Dict[str, str]]:
    """Return all registered targets as a list of dicts with 'name' included."""
    targets = _get_targets(vault)
    return [{"name": k, **v} for k, v in targets.items()]


def get_target(vault, name: str) -> Optional[Dict[str, str]]:
    """Fetch a single target by name, or None if not found."""
    targets = _get_targets(vault)
    entry = targets.get(name)
    if entry is None:
        return None
    return {"name": name, **entry}
