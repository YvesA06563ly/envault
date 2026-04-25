"""Secret correlation: link related secrets together."""
from __future__ import annotations

from typing import Dict, List

_CORR_KEY = "__correlations__"


def _load_correlations(vault) -> Dict[str, List[str]]:
    raw = vault.get(_CORR_KEY)
    if not raw:
        return {}
    import json
    return json.loads(raw)


def _save_correlations(vault, data: Dict[str, List[str]]) -> None:
    import json
    vault.set(_CORR_KEY, json.dumps(data))
    vault.save()


def link(vault, key: str, related: str) -> None:
    """Link *related* as a correlate of *key* (bidirectional)."""
    if key == related:
        raise ValueError("A secret cannot be correlated with itself.")
    data = _load_correlations(vault)
    for a, b in ((key, related), (related, key)):
        peers = data.setdefault(a, [])
        if b not in peers:
            peers.append(b)
    _save_correlations(vault, data)


def unlink(vault, key: str, related: str) -> bool:
    """Remove correlation between *key* and *related*. Returns True if removed."""
    data = _load_correlations(vault)
    changed = False
    for a, b in ((key, related), (related, key)):
        if a in data and b in data[a]:
            data[a].remove(b)
            if not data[a]:
                del data[a]
            changed = True
    if changed:
        _save_correlations(vault, data)
    return changed


def get_correlates(vault, key: str) -> List[str]:
    """Return all secrets correlated with *key*."""
    data = _load_correlations(vault)
    return list(data.get(key, []))


def clear_correlates(vault, key: str) -> None:
    """Remove all correlations for *key*."""
    data = _load_correlations(vault)
    peers = data.pop(key, [])
    for peer in peers:
        if peer in data and key in data[peer]:
            data[peer].remove(key)
            if not data[peer]:
                del data[peer]
    _save_correlations(vault, data)


def list_all(vault) -> Dict[str, List[str]]:
    """Return the full correlation map."""
    return dict(_load_correlations(vault))
