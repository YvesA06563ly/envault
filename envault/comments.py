"""Per-secret comments/annotations stored in the vault."""

from __future__ import annotations

from typing import Optional

COMMENTS_KEY = "__comments__"


def _load_comments(vault) -> dict:
    raw = vault.get(COMMENTS_KEY)
    if not raw:
        return {}
    import json
    return json.loads(raw)


def _save_comments(vault, data: dict) -> None:
    import json
    vault.set(COMMENTS_KEY, json.dumps(data))
    vault.save()


def set_comment(vault, key: str, comment: str) -> None:
    """Attach a comment/annotation to a secret key."""
    data = _load_comments(vault)
    data[key] = comment
    _save_comments(vault, data)


def remove_comment(vault, key: str) -> bool:
    """Remove the comment for a secret key. Returns True if it existed."""
    data = _load_comments(vault)
    if key not in data:
        return False
    del data[key]
    _save_comments(vault, data)
    return True


def get_comment(vault, key: str) -> Optional[str]:
    """Return the comment for a secret key, or None."""
    return _load_comments(vault).get(key)


def list_comments(vault) -> dict:
    """Return all key -> comment mappings."""
    return dict(_load_comments(vault))


def keys_with_comments(vault) -> list:
    """Return sorted list of keys that have comments."""
    return sorted(_load_comments(vault).keys())
