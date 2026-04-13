"""Tests for envault.namespace."""

from __future__ import annotations

import json
import pytest

from envault import namespace as ns_mod


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


def test_assign_and_get(vault):
    ns_mod.assign_namespace(vault, "DB_PASS", "database")
    assert ns_mod.get_namespace(vault, "DB_PASS") == "database"


def test_get_unassigned_returns_none(vault):
    assert ns_mod.get_namespace(vault, "MISSING") is None


def test_assign_invalid_namespace_raises(vault):
    with pytest.raises(ValueError):
        ns_mod.assign_namespace(vault, "KEY", "bad/namespace")


def test_assign_empty_namespace_raises(vault):
    with pytest.raises(ValueError):
        ns_mod.assign_namespace(vault, "KEY", "")


def test_remove_existing(vault):
    ns_mod.assign_namespace(vault, "API_KEY", "api")
    removed = ns_mod.remove_namespace(vault, "API_KEY")
    assert removed is True
    assert ns_mod.get_namespace(vault, "API_KEY") is None


def test_remove_nonexistent_returns_false(vault):
    assert ns_mod.remove_namespace(vault, "GHOST") is False


def test_list_namespaces_groups_keys(vault):
    ns_mod.assign_namespace(vault, "DB_PASS", "database")
    ns_mod.assign_namespace(vault, "DB_USER", "database")
    ns_mod.assign_namespace(vault, "API_KEY", "api")
    mapping = ns_mod.list_namespaces(vault)
    assert set(mapping["database"]) == {"DB_PASS", "DB_USER"}
    assert mapping["api"] == ["API_KEY"]


def test_list_namespaces_empty(vault):
    assert ns_mod.list_namespaces(vault) == {}


def test_keys_in_namespace(vault):
    ns_mod.assign_namespace(vault, "X", "ns1")
    ns_mod.assign_namespace(vault, "Y", "ns1")
    ns_mod.assign_namespace(vault, "Z", "ns2")
    assert set(ns_mod.keys_in_namespace(vault, "ns1")) == {"X", "Y"}
    assert ns_mod.keys_in_namespace(vault, "ns2") == ["Z"]
    assert ns_mod.keys_in_namespace(vault, "missing") == []


def test_qualified_name():
    assert ns_mod.qualified_name("DB_PASS", "database") == "database/DB_PASS"


def test_overwrite_namespace(vault):
    ns_mod.assign_namespace(vault, "KEY", "old")
    ns_mod.assign_namespace(vault, "KEY", "new")
    assert ns_mod.get_namespace(vault, "KEY") == "new"
    assert ns_mod.keys_in_namespace(vault, "old") == []


def test_vault_saved_on_assign(vault):
    ns_mod.assign_namespace(vault, "K", "ns")
    assert vault.saved is True


def test_vault_saved_on_remove(vault):
    ns_mod.assign_namespace(vault, "K", "ns")
    vault.saved = False
    ns_mod.remove_namespace(vault, "K")
    assert vault.saved is True
