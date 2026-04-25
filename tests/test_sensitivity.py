"""Tests for envault.sensitivity."""

from __future__ import annotations

import pytest

from envault.sensitivity import (
    VALID_LEVELS,
    clear_sensitivity,
    get_sensitivity,
    list_all,
    list_by_level,
    set_sensitivity,
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


def test_set_and_get_sensitivity(vault):
    set_sensitivity(vault, "DB_PASSWORD", "critical")
    assert get_sensitivity(vault, "DB_PASSWORD") == "critical"


def test_set_saves_vault(vault):
    set_sensitivity(vault, "API_KEY", "high")
    assert vault.saved


def test_get_returns_none_for_unknown(vault):
    assert get_sensitivity(vault, "MISSING") is None


def test_set_invalid_level_raises(vault):
    with pytest.raises(ValueError, match="Invalid sensitivity level"):
        set_sensitivity(vault, "KEY", "ultra")


def test_clear_sensitivity(vault):
    set_sensitivity(vault, "TOKEN", "high")
    clear_sensitivity(vault, "TOKEN")
    assert get_sensitivity(vault, "TOKEN") is None


def test_clear_nonexistent_is_noop(vault):
    clear_sensitivity(vault, "NOPE")  # should not raise


def test_list_by_level(vault):
    set_sensitivity(vault, "A", "low")
    set_sensitivity(vault, "B", "high")
    set_sensitivity(vault, "C", "low")
    result = list_by_level(vault, "low")
    assert result == ["A", "C"]


def test_list_by_level_empty(vault):
    assert list_by_level(vault, "critical") == []


def test_list_by_invalid_level_raises(vault):
    with pytest.raises(ValueError):
        list_by_level(vault, "unknown")


def test_list_all(vault):
    set_sensitivity(vault, "X", "medium")
    set_sensitivity(vault, "Y", "critical")
    data = list_all(vault)
    assert data == {"X": "medium", "Y": "critical"}


def test_list_all_empty(vault):
    assert list_all(vault) == {}


def test_all_valid_levels_accepted(vault):
    for level in VALID_LEVELS:
        set_sensitivity(vault, f"KEY_{level}", level)
        assert get_sensitivity(vault, f"KEY_{level}") == level


def test_overwrite_sensitivity(vault):
    set_sensitivity(vault, "SECRET", "low")
    set_sensitivity(vault, "SECRET", "critical")
    assert get_sensitivity(vault, "SECRET") == "critical"
