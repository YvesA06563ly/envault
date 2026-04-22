"""Watermark module: embed and verify secret provenance metadata."""

from __future__ import annotations

import hashlib
import json
from typing import Any

_WATERMARK_KEY = "__watermarks__"


def _load_watermarks(vault: Any) -> dict:
    raw = vault.get(_WATERMARK_KEY)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _save_watermarks(vault: Any, data: dict) -> None:
    vault.set(_WATERMARK_KEY, json.dumps(data))
    vault.save()


def _fingerprint(key: str, value: str, author: str) -> str:
    payload = f"{key}:{value}:{author}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def set_watermark(vault: Any, key: str, author: str, note: str = "") -> dict:
    """Attach a provenance watermark to a secret."""
    value = vault.get(key) or ""
    marks = _load_watermarks(vault)
    mark = {
        "author": author,
        "note": note,
        "fingerprint": _fingerprint(key, value, author),
    }
    marks[key] = mark
    _save_watermarks(vault, marks)
    return mark


def get_watermark(vault: Any, key: str) -> dict | None:
    """Return the watermark for a secret, or None if not set."""
    return _load_watermarks(vault).get(key)


def remove_watermark(vault: Any, key: str) -> bool:
    """Remove the watermark for a secret. Returns True if it existed."""
    marks = _load_watermarks(vault)
    if key not in marks:
        return False
    del marks[key]
    _save_watermarks(vault, marks)
    return True


def verify_watermark(vault: Any, key: str) -> bool:
    """Verify that the stored fingerprint matches the current secret value."""
    mark = get_watermark(vault, key)
    if not mark:
        return False
    value = vault.get(key) or ""
    expected = _fingerprint(key, value, mark["author"])
    return mark["fingerprint"] == expected


def list_watermarks(vault: Any) -> list[dict]:
    """Return all watermarks as a list of records."""
    marks = _load_watermarks(vault)
    return [
        {"key": k, **v}
        for k, v in sorted(marks.items())
    ]
