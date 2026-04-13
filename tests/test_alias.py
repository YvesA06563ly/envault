"""Tests for envault.alias."""

from __future__ import annotations

import json
import pytest

from envault.alias import (
    add_alias,
    remove_alias,
    resolve,
    list_aliases,
    aliases_for_key,
    _ALIAS_KEY,
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


def test_add_alias_creates_mapping(vault):
    add_alias(vault, "db", "DATABASE_URL")
    data = json.loads(vault.get(_ALIAS_KEY))
    assert data["db"] == "DATABASE_URL"


def test_add_alias_saves_vault(vault):
    add_alias(vault, "db", "DATABASE_URL")
    assert vault.saved


def test_add_alias_same_target_is_idempotent(vault):
    add_alias(vault, "db", "DATABASE_URL")
    add_alias(vault, "db", "DATABASE_URL")  # should not raise
    assert resolve(vault, "db") == "DATABASE_URL"


def test_add_alias_conflict_raises(vault):
    add_alias(vault, "db", "DATABASE_URL")
    with pytest.raises(ValueError, match="already points to"):
        add_alias(vault, "db", "OTHER_KEY")


def test_add_alias_same_name_raises(vault):
    with pytest.raises(ValueError, match="must differ"):
        add_alias(vault, "KEY", "KEY")


def test_remove_alias(vault):
    add_alias(vault, "db", "DATABASE_URL")
    remove_alias(vault, "db")
    assert resolve(vault, "db") == "db"


def test_remove_nonexistent_raises(vault):
    with pytest.raises(KeyError):
        remove_alias(vault, "ghost")


def test_resolve_returns_canonical(vault):
    add_alias(vault, "db", "DATABASE_URL")
    assert resolve(vault, "db") == "DATABASE_URL"


def test_resolve_unknown_returns_identity(vault):
    assert resolve(vault, "UNKNOWN") == "UNKNOWN"


def test_list_aliases_sorted(vault):
    add_alias(vault, "z_key", "Z")
    add_alias(vault, "a_key", "A")
    entries = list_aliases(vault)
    assert [e["alias"] for e in entries] == ["a_key", "z_key"]


def test_list_aliases_empty(vault):
    assert list_aliases(vault) == []


def test_aliases_for_key(vault):
    add_alias(vault, "db", "DATABASE_URL")
    add_alias(vault, "database", "DATABASE_URL")
    add_alias(vault, "redis", "REDIS_URL")
    names = aliases_for_key(vault, "DATABASE_URL")
    assert sorted(names) == ["database", "db"]


def test_aliases_for_key_none(vault):
    assert aliases_for_key(vault, "MISSING") == []
