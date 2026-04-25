"""Secret inheritance — allow a secret to inherit its value from another key."""

from __future__ import annotations

from typing import Optional

_INHERIT_KEY = "__inheritance__"


def _load_inheritance(vault) -> dict:
    raw = vault.get(_INHERIT_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_inheritance(vault, data: dict) -> None:
    vault.set(_INHERIT_KEY, data)
    vault.save()


def set_inherit(vault, key: str, parent: str) -> None:
    """Make *key* inherit its value from *parent*."""
    if key == parent:
        raise ValueError("A secret cannot inherit from itself.")
    data = _load_inheritance(vault)
    data[key] = parent
    _save_inheritance(vault, data)


def clear_inherit(vault, key: str) -> None:
    """Remove inheritance for *key*."""
    data = _load_inheritance(vault)
    data.pop(key, None)
    _save_inheritance(vault, data)


def get_parent(vault, key: str) -> Optional[str]:
    """Return the parent key that *key* inherits from, or None."""
    return _load_inheritance(vault).get(key)


def resolve_value(vault, key: str, secrets: dict, *, _seen: frozenset = frozenset()) -> Optional[str]:
    """Return the effective value for *key*, following inheritance chains.

    *secrets* is a plain ``{key: value}`` mapping of already-decrypted secrets.
    Raises ``ValueError`` on circular inheritance.
    """
    if key in _seen:
        raise ValueError(f"Circular inheritance detected involving '{key}'.")
    parent = get_parent(vault, key)
    if parent is None:
        return secrets.get(key)
    return resolve_value(vault, parent, secrets, _seen=_seen | {key})


def list_inheriting(vault) -> dict:
    """Return a mapping of {child: parent} for all defined inheritance rules."""
    return dict(_load_inheritance(vault))
