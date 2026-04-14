"""Checksum tracking for secret values — detects silent mutations."""

import hashlib
import json
from typing import Optional

_META_KEY = "__checksums__"


def _load_checksums(vault) -> dict:
    raw = vault.get(_META_KEY)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _save_checksums(vault, data: dict) -> None:
    vault.set(_META_KEY, json.dumps(data))
    vault.save()


def _hash(value: str) -> str:
    """Return a SHA-256 hex digest for the given value."""
    return hashlib.sha256(value.encode()).hexdigest()


def record_checksum(vault, key: str, value: str) -> str:
    """Store the checksum for *key* and return the digest."""
    checksums = _load_checksums(vault)
    digest = _hash(value)
    checksums[key] = digest
    _save_checksums(vault, checksums)
    return digest


def verify_checksum(vault, key: str, value: str) -> bool:
    """Return True if *value* matches the stored checksum for *key*."""
    checksums = _load_checksums(vault)
    stored = checksums.get(key)
    if stored is None:
        return False
    return stored == _hash(value)


def get_checksum(vault, key: str) -> Optional[str]:
    """Return the stored checksum digest for *key*, or None."""
    return _load_checksums(vault).get(key)


def remove_checksum(vault, key: str) -> bool:
    """Delete the checksum entry for *key*. Returns True if it existed."""
    checksums = _load_checksums(vault)
    if key not in checksums:
        return False
    del checksums[key]
    _save_checksums(vault, checksums)
    return True


def list_checksums(vault) -> dict:
    """Return a mapping of key -> digest for all tracked secrets."""
    return dict(_load_checksums(vault))
