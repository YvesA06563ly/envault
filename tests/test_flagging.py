"""Tests for envault.flagging."""

from __future__ import annotations

import json
import pytest

from envault.flagging import (
    VALID_FLAGS,
    add_flag,
    clear_flags,
    get_flags,
    has_flag,
    list_flagged,
    remove_flag,
)

_STORE_KEY = "__flagging__"


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


def test_add_flag_stores_flag(vault):
    add_flag(vault, "DB_PASS", "suspicious")
    assert get_flags(vault, "DB_PASS") == ["suspicious"]


def test_add_flag_saves_vault(vault):
    add_flag(vault, "DB_PASS", "stale")
    assert vault.saved


def test_add_duplicate_flag_is_idempotent(vault):
    add_flag(vault, "KEY", "reviewed")
    add_flag(vault, "KEY", "reviewed")
    assert get_flags(vault, "KEY").count("reviewed") == 1


def test_add_invalid_flag_raises(vault):
    with pytest.raises(ValueError, match="Unknown flag"):
        add_flag(vault, "KEY", "nonexistent")


def test_remove_flag_returns_true_when_present(vault):
    add_flag(vault, "KEY", "stale")
    result = remove_flag(vault, "KEY", "stale")
    assert result is True
    assert get_flags(vault, "KEY") == []


def test_remove_flag_returns_false_when_absent(vault):
    result = remove_flag(vault, "KEY", "stale")
    assert result is False


def test_remove_flag_leaves_other_flags(vault):
    add_flag(vault, "KEY", "stale")
    add_flag(vault, "KEY", "suspicious")
    remove_flag(vault, "KEY", "stale")
    assert get_flags(vault, "KEY") == ["suspicious"]


def test_has_flag_true(vault):
    add_flag(vault, "KEY", "deprecated")
    assert has_flag(vault, "KEY", "deprecated") is True


def test_has_flag_false(vault):
    assert has_flag(vault, "KEY", "deprecated") is False


def test_list_flagged_returns_all(vault):
    add_flag(vault, "A", "stale")
    add_flag(vault, "B", "suspicious")
    result = list_flagged(vault)
    assert "A" in result
    assert "B" in result


def test_list_flagged_filtered(vault):
    add_flag(vault, "A", "stale")
    add_flag(vault, "B", "suspicious")
    result = list_flagged(vault, flag="stale")
    assert "A" in result
    assert "B" not in result


def test_clear_flags_removes_all(vault):
    add_flag(vault, "KEY", "stale")
    add_flag(vault, "KEY", "reviewed")
    clear_flags(vault, "KEY")
    assert get_flags(vault, "KEY") == []


def test_get_flags_empty_vault(vault):
    assert get_flags(vault, "MISSING") == []


def test_valid_flags_set_is_non_empty():
    assert len(VALID_FLAGS) > 0
