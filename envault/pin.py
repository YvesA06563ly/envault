"""Secret pinning — mark a secret version as pinned to prevent accidental rotation."""

from __future__ import annotations

from typing import Dict, List

_PINS_KEY = "__pins__"


def _load_pins(vault) -> Dict[str, str]:
    """Return {key: reason} for all pinned secrets."""
    raw = vault.get(_PINS_KEY)
    if not raw:
        return {}
    import json
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {}


def _save_pins(vault, pins: Dict[str, str]) -> None:
    import json
    vault.set(_PINS_KEY, json.dumps(pins))
    vault.save()


def pin_secret(vault, key: str, reason: str = "") -> None:
    """Pin *key* so rotation tools will skip it."""
    pins = _load_pins(vault)
    pins[key] = reason
    _save_pins(vault, pins)


def unpin_secret(vault, key: str) -> bool:
    """Remove pin from *key*. Returns True if it was pinned."""
    pins = _load_pins(vault)
    if key not in pins:
        return False
    del pins[key]
    _save_pins(vault, pins)
    return True


def is_pinned(vault, key: str) -> bool:
    """Return True if *key* is currently pinned."""
    return key in _load_pins(vault)


def list_pins(vault) -> List[Dict[str, str]]:
    """Return a list of dicts with 'key' and 'reason'."""
    pins = _load_pins(vault)
    return [{"key": k, "reason": r} for k, r in sorted(pins.items())]


def pin_info(vault, key: str) -> Dict[str, str] | None:
    """Return pin info for *key*, or None if not pinned."""
    pins = _load_pins(vault)
    if key not in pins:
        return None
    return {"key": key, "reason": pins[key]}
