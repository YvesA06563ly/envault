"""Tests for envault.retention module."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from envault.retention import (
    clear_retention,
    get_retention,
    is_expired,
    list_expired,
    list_retention,
    set_retention,
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


@pytest.fixture()
def vault():
    return _FakeVault()


def test_set_retention_stores_record(vault):
    set_retention(vault, "DB_PASS", 30)
    record = get_retention(vault, "DB_PASS")
    assert record is not None
    assert record["days"] == 30
    assert "expires_at" in record
    assert "set_at" in record
    assert vault.saved


def test_set_retention_invalid_days_raises(vault):
    with pytest.raises(ValueError):
        set_retention(vault, "DB_PASS", 0)
    with pytest.raises(ValueError):
        set_retention(vault, "DB_PASS", -5)


def test_get_retention_missing_key_returns_none(vault):
    assert get_retention(vault, "MISSING") is None


def test_clear_retention_removes_record(vault):
    set_retention(vault, "API_KEY", 10)
    removed = clear_retention(vault, "API_KEY")
    assert removed is True
    assert get_retention(vault, "API_KEY") is None


def test_clear_retention_missing_key_returns_false(vault):
    assert clear_retention(vault, "NOPE") is False


def test_is_expired_future_expiry_returns_false(vault):
    set_retention(vault, "TOKEN", 90)
    assert is_expired(vault, "TOKEN") is False


def test_is_expired_past_expiry_returns_true(vault):
    set_retention(vault, "OLD_KEY", 1)
    # Manually backdate the expires_at
    from envault.retention import RETENTION_KEY
    data = vault.get(RETENTION_KEY)
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    data["OLD_KEY"]["expires_at"] = past
    vault.set(RETENTION_KEY, data)
    assert is_expired(vault, "OLD_KEY") is True


def test_is_expired_no_record_returns_false(vault):
    assert is_expired(vault, "UNKNOWN") is False


def test_list_expired_returns_only_expired(vault):
    from envault.retention import RETENTION_KEY
    set_retention(vault, "FRESH", 30)
    set_retention(vault, "STALE", 1)
    data = vault.get(RETENTION_KEY)
    past = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    data["STALE"]["expires_at"] = past
    vault.set(RETENTION_KEY, data)
    expired = list_expired(vault)
    assert "STALE" in expired
    assert "FRESH" not in expired


def test_list_retention_includes_all_keys(vault):
    set_retention(vault, "A", 7)
    set_retention(vault, "B", 14)
    entries = list_retention(vault)
    keys = [e["key"] for e in entries]
    assert "A" in keys
    assert "B" in keys
    assert all("days" in e for e in entries)
