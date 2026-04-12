"""Audit log for secret access and modifications."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

AUDIT_LOG_KEY = "__audit_log__"
_MAX_ENTRIES = 500


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_log(vault) -> List[Dict[str, Any]]:
    raw = vault.get(AUDIT_LOG_KEY)
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []


def _save_log(vault, entries: List[Dict[str, Any]]) -> None:
    trimmed = entries[-_MAX_ENTRIES:]
    vault.set(AUDIT_LOG_KEY, json.dumps(trimmed))
    vault.save()


def record_event(
    vault,
    action: str,
    key: str,
    actor: Optional[str] = None,
    details: Optional[str] = None,
) -> None:
    """Append an audit event for *action* on *key*."""
    entries = _load_log(vault)
    entry: Dict[str, Any] = {
        "timestamp": _now_iso(),
        "action": action,
        "key": key,
    }
    if actor:
        entry["actor"] = actor
    if details:
        entry["details"] = details
    entries.append(entry)
    _save_log(vault, entries)


def get_log(
    vault,
    key: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Return audit entries, optionally filtered by *key* or *action*."""
    entries = _load_log(vault)
    if key:
        entries = [e for e in entries if e.get("key") == key]
    if action:
        entries = [e for e in entries if e.get("action") == action]
    return entries[-limit:]
