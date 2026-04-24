"""Secret grouping — assign secrets to named groups and query by group."""

from __future__ import annotations

from typing import Dict, List

_GROUPING_KEY = "__grouping__"


def _load_groups(vault) -> Dict[str, List[str]]:
    raw = vault.get(_GROUPING_KEY)
    if not raw:
        return {}
    import json
    return json.loads(raw)


def _save_groups(vault, data: Dict[str, List[str]]) -> None:
    import json
    vault.set(_GROUPING_KEY, json.dumps(data))
    vault.save()


def assign_group(vault, key: str, group: str) -> None:
    """Assign *key* to *group*. A key may belong to multiple groups."""
    data = _load_groups(vault)
    members = data.setdefault(group, [])
    if key not in members:
        members.append(key)
    _save_groups(vault, data)


def remove_from_group(vault, key: str, group: str) -> bool:
    """Remove *key* from *group*. Returns True if the key was present."""
    data = _load_groups(vault)
    members = data.get(group, [])
    if key not in members:
        return False
    members.remove(key)
    if not members:
        del data[group]
    _save_groups(vault, data)
    return True


def list_groups(vault) -> List[str]:
    """Return all group names."""
    return sorted(_load_groups(vault).keys())


def members_of(vault, group: str) -> List[str]:
    """Return all secret keys belonging to *group*."""
    return list(_load_groups(vault).get(group, []))


def groups_of(vault, key: str) -> List[str]:
    """Return all groups that *key* belongs to."""
    data = _load_groups(vault)
    return sorted(g for g, members in data.items() if key in members)


def delete_group(vault, group: str) -> bool:
    """Delete an entire group. Returns True if it existed."""
    data = _load_groups(vault)
    if group not in data:
        return False
    del data[group]
    _save_groups(vault, data)
    return True
