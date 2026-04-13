"""Tag management for envault secrets."""
from __future__ import annotations

from typing import Dict, List

_TAGS_KEY = "__tags__"


def _load_tags(vault) -> Dict[str, List[str]]:
    """Load the tags mapping {secret_key: [tag, ...]} from the vault."""
    raw = vault.get(_TAGS_KEY)
    if raw is None:
        return {}
    import json
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {}


def _save_tags(vault, tags: Dict[str, List[str]]) -> None:
    """Persist the tags mapping back to the vault."""
    import json
    vault.set(_TAGS_KEY, json.dumps(tags))
    vault.save()


def add_tag(vault, secret_key: str, tag: str) -> None:
    """Add *tag* to *secret_key*.  Duplicate tags are silently ignored."""
    tags = _load_tags(vault)
    bucket = tags.setdefault(secret_key, [])
    if tag not in bucket:
        bucket.append(tag)
    _save_tags(vault, tags)


def remove_tag(vault, secret_key: str, tag: str) -> None:
    """Remove *tag* from *secret_key*.  Raises KeyError if not present."""
    tags = _load_tags(vault)
    bucket = tags.get(secret_key, [])
    if tag not in bucket:
        raise KeyError(f"Tag '{tag}' not found on secret '{secret_key}'")
    bucket.remove(tag)
    if not bucket:
        tags.pop(secret_key, None)
    _save_tags(vault, tags)


def list_tags(vault, secret_key: str) -> List[str]:
    """Return all tags attached to *secret_key* (may be empty)."""
    return list(_load_tags(vault).get(secret_key, []))


def find_by_tag(vault, tag: str) -> List[str]:
    """Return all secret keys that carry *tag*."""
    tags = _load_tags(vault)
    return [key for key, bucket in tags.items() if tag in bucket]


def clear_tags(vault, secret_key: str) -> None:
    """Remove every tag from *secret_key*."""
    tags = _load_tags(vault)
    tags.pop(secret_key, None)
    _save_tags(vault, tags)
