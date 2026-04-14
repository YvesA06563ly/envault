"""Label management for envault secrets.

Labels are free-form key=value metadata attached to secrets,
distinct from tags (which are plain strings).
"""

from __future__ import annotations

from typing import Dict, List, Optional

_LABELS_KEY = "__labels__"


def _load_labels(vault) -> Dict[str, Dict[str, str]]:
    raw = vault.get(_LABELS_KEY)
    if not raw:
        return {}
    import json
    return json.loads(raw)


def _save_labels(vault, data: Dict[str, Dict[str, str]]) -> None:
    import json
    vault.set(_LABELS_KEY, json.dumps(data))
    vault.save()


def set_label(vault, secret_key: str, label_key: str, label_value: str) -> None:
    """Attach a label key=value to a secret."""
    data = _load_labels(vault)
    data.setdefault(secret_key, {})[label_key] = label_value
    _save_labels(vault, data)


def remove_label(vault, secret_key: str, label_key: str) -> bool:
    """Remove a label from a secret. Returns True if it existed."""
    data = _load_labels(vault)
    labels = data.get(secret_key, {})
    if label_key not in labels:
        return False
    del labels[label_key]
    if not labels:
        data.pop(secret_key, None)
    else:
        data[secret_key] = labels
    _save_labels(vault, data)
    return True


def get_labels(vault, secret_key: str) -> Dict[str, str]:
    """Return all labels for a secret."""
    return dict(_load_labels(vault).get(secret_key, {}))


def find_by_label(vault, label_key: str, label_value: Optional[str] = None) -> List[str]:
    """Return secret keys that have the given label (optionally matching value)."""
    data = _load_labels(vault)
    results = []
    for secret_key, labels in data.items():
        if label_key in labels:
            if label_value is None or labels[label_key] == label_value:
                results.append(secret_key)
    return sorted(results)


def clear_labels(vault, secret_key: str) -> None:
    """Remove all labels from a secret."""
    data = _load_labels(vault)
    data.pop(secret_key, None)
    _save_labels(vault, data)
