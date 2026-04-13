"""Tests for envault.notify."""

from __future__ import annotations

import json
import pytest

from envault.notify import (
    _NOTIFY_KEY,
    dispatch,
    get_subscribers,
    list_subscriptions,
    subscribe,
    unsubscribe,
)


class _FakeVault:
    def __init__(self):
        self._store: dict = {}
        self.saved = False

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        self.saved = True


@pytest.fixture
def fv():
    return _FakeVault()


def test_subscribe_adds_channel(fv):
    subscribe(fv, "rotation", "https://hooks.example.com/1")
    subs = get_subscribers(fv, "rotation")
    assert "https://hooks.example.com/1" in subs


def test_subscribe_persists(fv):
    subscribe(fv, "expiry", "admin@example.com")
    assert fv.saved


def test_subscribe_no_duplicates(fv):
    subscribe(fv, "rotation", "chan")
    subscribe(fv, "rotation", "chan")
    assert get_subscribers(fv, "rotation").count("chan") == 1


def test_subscribe_invalid_event_raises(fv):
    with pytest.raises(ValueError, match="Unsupported event"):
        subscribe(fv, "unknown_event", "chan")


def test_unsubscribe_removes_channel(fv):
    subscribe(fv, "import", "slack://channel")
    removed = unsubscribe(fv, "import", "slack://channel")
    assert removed is True
    assert "slack://channel" not in get_subscribers(fv, "import")


def test_unsubscribe_returns_false_if_missing(fv):
    result = unsubscribe(fv, "delete", "nonexistent")
    assert result is False


def test_list_subscriptions_all_events(fv):
    subscribe(fv, "rotation", "a")
    subscribe(fv, "expiry", "b")
    subs = list_subscriptions(fv)
    assert "rotation" in subs
    assert "expiry" in subs


def test_get_subscribers_empty(fv):
    assert get_subscribers(fv, "access") == []


def test_dispatch_returns_notified_channels(fv):
    subscribe(fv, "rotation", "ch1")
    subscribe(fv, "rotation", "ch2")
    notified = dispatch(fv, "rotation")
    assert set(notified) == {"ch1", "ch2"}


def test_dispatch_no_subscribers_returns_empty(fv):
    notified = dispatch(fv, "delete")
    assert notified == []


def test_multiple_events_independent(fv):
    subscribe(fv, "rotation", "r-chan")
    subscribe(fv, "expiry", "e-chan")
    assert get_subscribers(fv, "rotation") == ["r-chan"]
    assert get_subscribers(fv, "expiry") == ["e-chan"]
