"""Tests for envault.trustlevel."""

from __future__ import annotations

import pytest

from envault.trustlevel import (
    all_trust_levels,
    clear_trust,
    get_trust,
    list_by_trust,
    set_trust,
)

_KEY = "__trustlevels__"


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
def vault():
    return _FakeVault()


def test_set_and_get_trust(vault):
    set_trust(vault, "DB_PASS", "high")
    assert get_trust(vault, "DB_PASS") == "high"


def test_get_trust_unset_returns_none(vault):
    assert get_trust(vault, "MISSING_KEY") is None


def test_set_invalid_level_raises(vault):
    with pytest.raises(ValueError, match="Invalid trust level"):
        set_trust(vault, "API_KEY", "ultra")


def test_clear_trust(vault):
    set_trust(vault, "TOKEN", "verified")
    clear_trust(vault, "TOKEN")
    assert get_trust(vault, "TOKEN") is None


def test_clear_nonexistent_key_is_noop(vault):
    clear_trust(vault, "GHOST")  # should not raise
    assert vault.saved is True


def test_list_by_trust(vault):
    set_trust(vault, "DB_PASS", "high")
    set_trust(vault, "API_KEY", "medium")
    set_trust(vault, "ADMIN_TOKEN", "high")
    result = list_by_trust(vault, "high")
    assert result == ["ADMIN_TOKEN", "DB_PASS"]


def test_list_by_trust_empty(vault):
    assert list_by_trust(vault, "verified") == []


def test_list_by_trust_invalid_level_raises(vault):
    with pytest.raises(ValueError, match="Invalid trust level"):
        list_by_trust(vault, "unknown")


def test_all_trust_levels(vault):
    set_trust(vault, "X", "low")
    set_trust(vault, "Y", "verified")
    result = all_trust_levels(vault)
    assert result == {"X": "low", "Y": "verified"}


def test_overwrite_trust_level(vault):
    set_trust(vault, "SECRET", "low")
    set_trust(vault, "SECRET", "verified")
    assert get_trust(vault, "SECRET") == "verified"


def test_save_is_called(vault):
    vault.saved = False
    set_trust(vault, "K", "medium")
    assert vault.saved is True
