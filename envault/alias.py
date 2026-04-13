"""Secret aliasing — map short names to canonical secret keys."""

from __future__ import annotations

from typing import Dict, List, Optional

_ALIAS_KEY = "__meta__:aliases"


def _load_aliases(vault) -> Dict[str, str]:
    """Return {alias: canonical_key} mapping stored in the vault."""
    raw = vault.get(_ALIAS_KEY)
    if not raw:
        return {}
    import json
    return json.loads(raw)


def _save_aliases(vault, aliases: Dict[str, str]) -> None:
    import json
    vault.set(_ALIAS_KEY, json.dumps(aliases))
    vault.save()


def add_alias(vault, alias: str, key: str) -> None:
    """Create *alias* pointing to *key*. Raises ValueError on conflict."""
    if alias == key:
        raise ValueError("Alias and key must differ.")
    aliases = _load_aliases(vault)
    if alias in aliases and aliases[alias] != key:
        raise ValueError(
            f"Alias '{alias}' already points to '{aliases[alias]}'. "
            "Remove it first."
        )
    aliases[alias] = key
    _save_aliases(vault, aliases)


def remove_alias(vault, alias: str) -> None:
    """Delete *alias*. Raises KeyError if not found."""
    aliases = _load_aliases(vault)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' does not exist.")
    del aliases[alias]
    _save_aliases(vault, aliases)


def resolve(vault, name: str) -> str:
    """Return the canonical key for *name* (identity if not an alias)."""
    aliases = _load_aliases(vault)
    return aliases.get(name, name)


def list_aliases(vault) -> List[Dict[str, str]]:
    """Return a list of {alias, key} dicts sorted by alias."""
    aliases = _load_aliases(vault)
    return [
        {"alias": a, "key": k}
        for a, k in sorted(aliases.items())
    ]


def aliases_for_key(vault, key: str) -> List[str]:
    """Return all aliases that point to *key*."""
    aliases = _load_aliases(vault)
    return [a for a, k in aliases.items() if k == key]
