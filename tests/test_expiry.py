"""Tests for envault.expiry module."""

from __future__ import annotations

import json
import pytest
from datetime import datetime, timezone, timedelta
from envault import expiry as exp


class _FakeVault:
    def __init__(self):
        self._store: dict[str, str] = {}
        self.saved = False

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        self.saved = True


@pytest.fixture
def vault():
    return _FakeVault()


def test_set_expiry_stores_iso_date(vault):
    result = exp.set_expiry(vault, "DB_PASS", 30)
    assert isinstance(result, datetime)
    stored = json.loads(vault.get("__expiry_meta__"))
    assert "DB_PASS" in stored
    assert vault.saved


def test_set_expiry_negative_days_raises(vault):
    with pytest.raises(ValueError):
        exp.set_expiry(vault, "KEY", -1)


def test_set_expiry_zero_days_raises(vault):
    with pytest.raises(ValueError):
        exp.set_expiry(vault, "KEY", 0)


def test_get_expiry_none_when_not_set(vault):
    assert exp.get_expiry(vault, "MISSING") is None


def test_get_expiry_returns_datetime(vault):
    exp.set_expiry(vault, "API_KEY", 10)
    result = exp.get_expiry(vault, "API_KEY")
    assert isinstance(result, datetime)


def test_is_expired_false_for_future(vault):
    exp.set_expiry(vault, "TOKEN", 5)
    assert exp.is_expired(vault, "TOKEN") is False


def test_is_expired_true_for_past(vault):
    data = {"OLD_KEY": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()}
    vault.set("__expiry_meta__", json.dumps(data))
    assert exp.is_expired(vault, "OLD_KEY") is True


def test_is_expired_false_when_no_expiry(vault):
    assert exp.is_expired(vault, "NO_EXPIRY") is False


def test_clear_expiry_removes_key(vault):
    exp.set_expiry(vault, "DB_PASS", 10)
    removed = exp.clear_expiry(vault, "DB_PASS")
    assert removed is True
    assert exp.get_expiry(vault, "DB_PASS") is None


def test_clear_expiry_returns_false_when_missing(vault):
    assert exp.clear_expiry(vault, "GHOST") is False


def test_list_expiring_returns_sorted(vault):
    now = datetime.now(timezone.utc)
    data = {
        "B": (now + timedelta(days=3)).isoformat(),
        "A": (now + timedelta(days=1)).isoformat(),
        "C": (now + timedelta(days=10)).isoformat(),
    }
    vault.set("__expiry_meta__", json.dumps(data))
    results = exp.list_expiring(vault, within_days=7)
    keys = [r["key"] for r in results]
    assert keys == ["A", "B"]


def test_list_expiring_marks_expired(vault):
    now = datetime.now(timezone.utc)
    data = {"OLD": (now - timedelta(days=2)).isoformat()}
    vault.set("__expiry_meta__", json.dumps(data))
    results = exp.list_expiring(vault, within_days=7)
    assert results[0]["expired"] is True
