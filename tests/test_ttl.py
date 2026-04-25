"""Tests for envault.ttl."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta

import pytest

from envault.ttl import (
    set_ttl,
    clear_ttl,
    get_ttl,
    is_stale,
    list_ttls,
)

_TTL_KEY = "__ttl__"


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


def test_set_and_get_ttl(vault):
    set_ttl(vault, "API_KEY", 3600)
    assert get_ttl(vault, "API_KEY") == 3600


def test_set_ttl_persists(vault):
    set_ttl(vault, "TOKEN", 60)
    assert vault.saved is True
    raw = json.loads(vault.get(_TTL_KEY))
    assert raw["TOKEN"] == 60


def test_set_ttl_zero_raises(vault):
    with pytest.raises(ValueError):
        set_ttl(vault, "KEY", 0)


def test_set_ttl_negative_raises(vault):
    with pytest.raises(ValueError):
        set_ttl(vault, "KEY", -10)


def test_clear_ttl(vault):
    set_ttl(vault, "DB_PASS", 120)
    clear_ttl(vault, "DB_PASS")
    assert get_ttl(vault, "DB_PASS") is None


def test_clear_missing_key_is_noop(vault):
    clear_ttl(vault, "NONEXISTENT")  # should not raise


def test_get_ttl_missing_returns_none(vault):
    assert get_ttl(vault, "MISSING") is None


def test_list_ttls(vault):
    set_ttl(vault, "A", 100)
    set_ttl(vault, "B", 200)
    result = list_ttls(vault)
    assert result == {"A": 100, "B": 200}


def test_list_ttls_empty_vault(vault):
    """list_ttls should return an empty dict when no TTLs have been set."""
    result = list_ttls(vault)
    assert result == {}


def test_is_stale_when_exceeded(vault):
    set_ttl(vault, "OLD_KEY", 60)
    last_written = datetime.now(tz=timezone.utc) - timedelta(seconds=120)
    assert is_stale(vault, "OLD_KEY", last_written) is True


def test_is_not_stale_within_ttl(vault):
    set_ttl(vault, "FRESH", 3600)
    last_written = datetime.now(tz=timezone.utc) - timedelta(seconds=10)
    assert is_stale(vault, "FRESH", last_written) is False


def test_is_stale_no_ttl_returns_false(vault):
    last_written = datetime.now(tz=timezone.utc) - timedelta(days=999)
    assert is_stale(vault, "NO_TTL", last_written) is False


def test_is_stale_no_last_written_returns_false(vault):
    set_ttl(vault, "KEY", 1)
    assert is_stale(vault, "KEY", None) is False


def test_is_stale_naive_datetime(vault):
    set_ttl(vault, "KEY", 30)
    last_written = datetime.utcnow() - timedelta(seconds=60)
    assert is_stale(vault, "KEY", last_written) is True


def test_set_ttl_overwrites_existing(vault):
    """Setting a TTL for a key that already has one replaces the old value."""
    set_ttl(vault, "API_KEY", 3600)
    set_ttl(vault, "API_KEY", 7200)
    assert get_ttl(vault, "API_KEY") == 7200
