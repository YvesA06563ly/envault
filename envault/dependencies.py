"""Dependency tracking between secrets.

Allows marking that one secret depends on another, so that
rotation or change events can propagate warnings or triggers.
"""

from __future__ import annotations

from typing import Dict, List

_DEPS_KEY = "__dependencies__"


def _load_deps(vault) -> Dict[str, List[str]]:
    raw = vault.get(_DEPS_KEY)
    if not raw:
        return {}
    import json
    return json.loads(raw)


def _save_deps(vault, deps: Dict[str, List[str]]) -> None:
    import json
    vault.set(_DEPS_KEY, json.dumps(deps))
    vault.save()


def add_dependency(vault, secret_key: str, depends_on: str) -> None:
    """Record that *secret_key* depends on *depends_on*."""
    if secret_key == depends_on:
        raise ValueError("A secret cannot depend on itself.")
    deps = _load_deps(vault)
    deps.setdefault(secret_key, [])
    if depends_on not in deps[secret_key]:
        deps[secret_key].append(depends_on)
    _save_deps(vault, deps)


def remove_dependency(vault, secret_key: str, depends_on: str) -> bool:
    """Remove a dependency edge. Returns True if it existed."""
    deps = _load_deps(vault)
    if secret_key in deps and depends_on in deps[secret_key]:
        deps[secret_key].remove(depends_on)
        if not deps[secret_key]:
            del deps[secret_key]
        _save_deps(vault, deps)
        return True
    return False


def list_dependencies(vault, secret_key: str) -> List[str]:
    """Return all keys that *secret_key* directly depends on."""
    return _load_deps(vault).get(secret_key, [])


def dependents_of(vault, depends_on: str) -> List[str]:
    """Return all keys that declare a dependency on *depends_on*."""
    deps = _load_deps(vault)
    return [k for k, v in deps.items() if depends_on in v]


def all_dependencies(vault) -> Dict[str, List[str]]:
    """Return the full dependency map."""
    return dict(_load_deps(vault))
