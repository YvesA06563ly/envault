"""Namespace support for grouping secrets under logical prefixes."""

from __future__ import annotations

from typing import Dict, List, Optional

_NS_KEY = "__namespaces__"
_SEP = "/"


def _load_namespaces(vault) -> Dict[str, str]:
    """Return mapping of secret_key -> namespace."""
    raw = vault.get(_NS_KEY)
    if raw is None:
        return {}
    import json
    return json.loads(raw)


def _save_namespaces(vault, data: Dict[str, str]) -> None:
    import json
    vault.set(_NS_KEY, json.dumps(data))
    vault.save()


def assign_namespace(vault, key: str, namespace: str) -> None:
    """Assign *key* to *namespace*."""
    if not namespace or _SEP in namespace:
        raise ValueError(f"Invalid namespace: {namespace!r}")
    data = _load_namespaces(vault)
    data[key] = namespace
    _save_namespaces(vault, data)


def remove_namespace(vault, key: str) -> bool:
    """Remove namespace assignment for *key*. Returns True if removed."""
    data = _load_namespaces(vault)
    if key not in data:
        return False
    del data[key]
    _save_namespaces(vault, data)
    return True


def get_namespace(vault, key: str) -> Optional[str]:
    """Return the namespace for *key*, or None."""
    return _load_namespaces(vault).get(key)


def list_namespaces(vault) -> Dict[str, List[str]]:
    """Return mapping of namespace -> list of keys."""
    data = _load_namespaces(vault)
    result: Dict[str, List[str]] = {}
    for key, ns in data.items():
        result.setdefault(ns, []).append(key)
    for keys in result.values():
        keys.sort()
    return result


def keys_in_namespace(vault, namespace: str) -> List[str]:
    """Return all keys assigned to *namespace*."""
    return list_namespaces(vault).get(namespace, [])


def qualified_name(key: str, namespace: str) -> str:
    """Return 'namespace/key' string."""
    return f"{namespace}{_SEP}{key}"
