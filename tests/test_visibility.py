"""Tests for envault.visibility."""

from __future__ import annotations

import pytest

from envault.visibility import (
    set_visibility,
    clear_visibility,
    get_visibility,
    list_visibility,
    find_by_visibility,
    DEFAULT_LEVEL,
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


def test_get_visibility_default(vault):
    assert get_visibility(vault, "MY_KEY") == DEFAULT_LEVEL


def test_set_and_get_visibility(vault):
    set_visibility(vault, "API_KEY", "public")
    assert get_visibility(vault, "API_KEY") == "public"


def test_set_visibility_saves(vault):
    set_visibility(vault, "DB_PASS", "restricted")
    assert vault.saved


def test_set_invalid_level_raises(vault):
    with pytest.raises(ValueError, match="Invalid visibility level"):
        set_visibility(vault, "KEY", "top_secret")


def test_clear_visibility_restores_default(vault):
    set_visibility(vault, "TOKEN", "public")
    clear_visibility(vault, "TOKEN")
    assert get_visibility(vault, "TOKEN") == DEFAULT_LEVEL


def test_clear_nonexistent_key_is_safe(vault):
    clear_visibility(vault, "NONEXISTENT")
    assert get_visibility(vault, "NONEXISTENT") == DEFAULT_LEVEL


def test_list_visibility_empty(vault):
    assert list_visibility(vault) == {}


def test_list_visibility_multiple(vault):
    set_visibility(vault, "A", "public")
    set_visibility(vault, "B", "restricted")
    result = list_visibility(vault)
    assert result == {"A": "public", "B": "restricted"}


def test_find_by_visibility(vault):
    set_visibility(vault, "PUB1", "public")
    set_visibility(vault, "PUB2", "public")
    set_visibility(vault, "PRIV", "private")
    found = find_by_visibility(vault, "public")
    assert sorted(found) == ["PUB1", "PUB2"]


def test_find_by_visibility_invalid_level_raises(vault):
    with pytest.raises(ValueError, match="Invalid visibility level"):
        find_by_visibility(vault, "unknown")


def test_overwrite_visibility(vault):
    set_visibility(vault, "KEY", "public")
    set_visibility(vault, "KEY", "restricted")
    assert get_visibility(vault, "KEY") == "restricted"
