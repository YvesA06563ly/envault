"""Notification hooks for secret events (rotation, expiry, access)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

_NOTIFY_KEY = "__notify_channels__"

SUPPORTED_EVENTS = {"rotation", "expiry", "access", "import", "delete"}


def _load_channels(vault) -> Dict[str, List[str]]:
    raw = vault.get(_NOTIFY_KEY)
    if raw is None:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _save_channels(vault, channels: Dict[str, List[str]]) -> None:
    vault.set(_NOTIFY_KEY, json.dumps(channels))
    vault.save()


def subscribe(vault, event: str, channel: str) -> None:
    """Subscribe a channel (e.g. email, webhook URL) to an event."""
    if event not in SUPPORTED_EVENTS:
        raise ValueError(f"Unsupported event '{event}'. Choose from: {sorted(SUPPORTED_EVENTS)}")
    channels = _load_channels(vault)
    subscribers = channels.setdefault(event, [])
    if channel not in subscribers:
        subscribers.append(channel)
    _save_channels(vault, channels)


def unsubscribe(vault, event: str, channel: str) -> bool:
    """Remove a channel from an event. Returns True if it was present."""
    channels = _load_channels(vault)
    subscribers = channels.get(event, [])
    if channel in subscribers:
        subscribers.remove(channel)
        channels[event] = subscribers
        _save_channels(vault, channels)
        return True
    return False


def list_subscriptions(vault) -> Dict[str, List[str]]:
    """Return all event -> channel mappings."""
    return _load_channels(vault)


def get_subscribers(vault, event: str) -> List[str]:
    """Return channels subscribed to a specific event."""
    return _load_channels(vault).get(event, [])


def dispatch(vault, event: str, payload: Optional[Dict[str, Any]] = None) -> List[str]:
    """Simulate dispatching a notification. Returns list of notified channels."""
    subscribers = get_subscribers(vault, event)
    notified = []
    for channel in subscribers:
        # In a real implementation, send HTTP POST, email, etc.
        # Here we record which channels would be notified.
        notified.append(channel)
    return notified
