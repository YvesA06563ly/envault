"""Tests for envault.priority."""

from __future__ import annotations

import json
import pytest

from envault.priority import (
    set_priority,
    clear_priority,
    get_priority,
    list_priorities,
    filter_by_priority,
    LEVELS,
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


def test_set_and_get_priority(vault):
    set_priority(vault, "DB_PASS", "critical")
    assert get_priority(vault, "DB_PASS") == "critical"


def test_get_priority_unset_returns_none(vault):
    assert get_priority(vault, "MISSING_KEY") is None


def test_set_invalid_priority_raises(vault):
    with pytest.raises(ValueError, match="Invalid priority"):
        set_priority(vault, "API_KEY", "urgent")


def test_overwrite_priority(vault):
    set_priority(vault, "TOKEN", "low")
    set_priority(vault, "TOKEN", "high")
    assert get_priority(vault, "TOKEN") == "high"


def test_clear_existing_priority(vault):
    set_priority(vault, "SECRET", "normal")
    removed = clear_priority(vault, "SECRET")
    assert removed is True
    assert get_priority(vault, "SECRET") is None


def test_clear_missing_priority_returns_false(vault):
    assert clear_priority(vault, "GHOST") is False


def test_list_priorities_sorted_by_severity(vault):
    set_priority(vault, "A", "low")
    set_priority(vault, "B", "critical")
    set_priority(vault, "C", "normal")
    set_priority(vault, "D", "high")
    result = list_priorities(vault)
    levels = [level for _, level in result]
    assert levels == ["critical", "high", "normal", "low"]


def test_filter_by_priority(vault):
    set_priority(vault, "X", "high")
    set_priority(vault, "Y", "low")
    set_priority(vault, "Z", "high")
    highs = filter_by_priority(vault, "high")
    assert set(highs) == {"X", "Z"}


def test_filter_by_invalid_priority_raises(vault):
    with pytest.raises(ValueError, match="Invalid priority"):
        filter_by_priority(vault, "extreme")


def test_save_called_on_set(vault):
    set_priority(vault, "K", "normal")
    assert vault.saved is True


def test_all_levels_accepted(vault):
    for level in LEVELS:
        set_priority(vault, f"KEY_{level}", level)
        assert get_priority(vault, f"KEY_{level}") == level
