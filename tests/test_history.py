"""Tests for envault.history."""
from __future__ import annotations

import pytest
from envault.history import (
    clear_history,
    get_history,
    list_keys_with_history,
    record_history,
    _MAX_ENTRIES,
)


class _FakeVault:
    def __init__(self):
        self._data: dict = {}
        self.saved = False

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value

    def save(self):
        self.saved = True


@pytest.fixture()
def vault():
    return _FakeVault()


def test_get_history_empty(vault):
    assert get_history(vault, "MY_KEY") == []


def test_record_creates_entry(vault):
    record_history(vault, "DB_PASS", None, "secret1")
    history = get_history(vault, "DB_PASS")
    assert len(history) == 1
    assert history[0]["value"] == "secret1"
    assert history[0]["previous"] is None
    assert "timestamp" in history[0]


def test_record_tracks_previous(vault):
    record_history(vault, "DB_PASS", None, "v1")
    record_history(vault, "DB_PASS", "v1", "v2")
    history = get_history(vault, "DB_PASS")
    assert len(history) == 2
    assert history[1]["previous"] == "v1"
    assert history[1]["value"] == "v2"


def test_history_capped_at_max_entries(vault):
    for i in range(_MAX_ENTRIES + 5):
        record_history(vault, "KEY", str(i - 1) if i else None, str(i))
    history = get_history(vault, "KEY")
    assert len(history) == _MAX_ENTRIES
    # Most recent entries are kept
    assert history[-1]["value"] == str(_MAX_ENTRIES + 4)


def test_clear_history_removes_entries(vault):
    record_history(vault, "API_KEY", None, "abc")
    removed = clear_history(vault, "API_KEY")
    assert removed is True
    assert get_history(vault, "API_KEY") == []


def test_clear_history_missing_key_returns_false(vault):
    assert clear_history(vault, "NONEXISTENT") is False


def test_list_keys_with_history(vault):
    record_history(vault, "A", None, "1")
    record_history(vault, "B", None, "2")
    keys = list_keys_with_history(vault)
    assert set(keys) == {"A", "B"}


def test_save_called_after_record(vault):
    record_history(vault, "X", None, "val")
    assert vault.saved is True


def test_multiple_keys_independent(vault):
    record_history(vault, "K1", None, "a")
    record_history(vault, "K2", None, "b")
    assert get_history(vault, "K1")[0]["value"] == "a"
    assert get_history(vault, "K2")[0]["value"] == "b"
