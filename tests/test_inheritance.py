"""Tests for envault.inheritance."""

from __future__ import annotations

import pytest

from envault.inheritance import (
    set_inherit,
    clear_inherit,
    get_parent,
    resolve_value,
    list_inheriting,
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


def test_set_and_get_parent(vault):
    set_inherit(vault, "DB_URL", "BASE_DB_URL")
    assert get_parent(vault, "DB_URL") == "BASE_DB_URL"


def test_set_saves_vault(vault):
    set_inherit(vault, "A", "B")
    assert vault.saved


def test_clear_removes_rule(vault):
    set_inherit(vault, "A", "B")
    clear_inherit(vault, "A")
    assert get_parent(vault, "A") is None


def test_clear_nonexistent_is_noop(vault):
    clear_inherit(vault, "MISSING")  # should not raise


def test_self_inherit_raises(vault):
    with pytest.raises(ValueError, match="cannot inherit from itself"):
        set_inherit(vault, "KEY", "KEY")


def test_list_inheriting(vault):
    set_inherit(vault, "A", "B")
    set_inherit(vault, "C", "D")
    rules = list_inheriting(vault)
    assert rules == {"A": "B", "C": "D"}


def test_resolve_value_no_inheritance(vault):
    secrets = {"X": "hello"}
    assert resolve_value(vault, "X", secrets) == "hello"


def test_resolve_value_follows_parent(vault):
    set_inherit(vault, "CHILD", "PARENT")
    secrets = {"PARENT": "parent_value"}
    assert resolve_value(vault, "CHILD", secrets) == "parent_value"


def test_resolve_value_chain(vault):
    set_inherit(vault, "C", "B")
    set_inherit(vault, "B", "A")
    secrets = {"A": "root"}
    assert resolve_value(vault, "C", secrets) == "root"


def test_resolve_value_circular_raises(vault):
    set_inherit(vault, "A", "B")
    set_inherit(vault, "B", "A")
    with pytest.raises(ValueError, match="Circular inheritance"):
        resolve_value(vault, "A", {})


def test_resolve_missing_key_returns_none(vault):
    assert resolve_value(vault, "GHOST", {}) is None
