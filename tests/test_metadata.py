"""Tests for envault.metadata."""
from __future__ import annotations

import pytest

from envault.metadata import (
    clear_metadata,
    get_field,
    get_metadata,
    list_metadata,
    remove_metadata,
    set_metadata,
)

_STORE_KEY = "__metadata__"


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


def test_set_and_get_field(vault):
    set_metadata(vault, "DB_PASS", "owner", "alice")
    assert get_field(vault, "DB_PASS", "owner") == "alice"


def test_get_metadata_returns_all_fields(vault):
    set_metadata(vault, "API_KEY", "env", "prod")
    set_metadata(vault, "API_KEY", "team", "backend")
    meta = get_metadata(vault, "API_KEY")
    assert meta == {"env": "prod", "team": "backend"}


def test_get_metadata_missing_key_returns_empty(vault):
    assert get_metadata(vault, "NONEXISTENT") == {}


def test_get_field_missing_returns_default(vault):
    assert get_field(vault, "X", "y") is None
    assert get_field(vault, "X", "y", "fallback") == "fallback"


def test_remove_existing_field(vault):
    set_metadata(vault, "TOKEN", "source", "manual")
    set_metadata(vault, "TOKEN", "critical", True)
    removed = remove_metadata(vault, "TOKEN", "source")
    assert removed is True
    assert get_field(vault, "TOKEN", "source") is None
    assert get_field(vault, "TOKEN", "critical") is True


def test_remove_cleans_up_empty_entry(vault):
    set_metadata(vault, "SOLO", "field", "val")
    remove_metadata(vault, "SOLO", "field")
    assert "SOLO" not in list_metadata(vault)


def test_remove_nonexistent_field_returns_false(vault):
    assert remove_metadata(vault, "GHOST", "nothing") is False


def test_clear_metadata(vault):
    set_metadata(vault, "SEC", "a", 1)
    set_metadata(vault, "SEC", "b", 2)
    clear_metadata(vault, "SEC")
    assert get_metadata(vault, "SEC") == {}


def test_list_metadata_multiple_keys(vault):
    set_metadata(vault, "K1", "x", 10)
    set_metadata(vault, "K2", "y", 20)
    listing = list_metadata(vault)
    assert listing["K1"] == {"x": 10}
    assert listing["K2"] == {"y": 20}


def test_save_called_on_mutation(vault):
    set_metadata(vault, "A", "f", "v")
    assert vault.saved is True


def test_overwrite_field(vault):
    set_metadata(vault, "KEY", "env", "staging")
    set_metadata(vault, "KEY", "env", "production")
    assert get_field(vault, "KEY", "env") == "production"
