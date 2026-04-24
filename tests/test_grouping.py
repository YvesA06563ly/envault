"""Tests for envault.grouping."""

from __future__ import annotations

import json
import pytest

from envault.grouping import (
    assign_group,
    remove_from_group,
    list_groups,
    members_of,
    groups_of,
    delete_group,
)

_GROUPING_KEY = "__grouping__"


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


def test_assign_group_adds_key(vault):
    assign_group(vault, "DB_PASS", "database")
    assert "DB_PASS" in members_of(vault, "database")


def test_assign_group_no_duplicates(vault):
    assign_group(vault, "DB_PASS", "database")
    assign_group(vault, "DB_PASS", "database")
    assert members_of(vault, "database").count("DB_PASS") == 1


def test_assign_multiple_keys_to_group(vault):
    assign_group(vault, "DB_PASS", "database")
    assign_group(vault, "DB_HOST", "database")
    members = members_of(vault, "database")
    assert "DB_PASS" in members
    assert "DB_HOST" in members


def test_key_in_multiple_groups(vault):
    assign_group(vault, "API_KEY", "external")
    assign_group(vault, "API_KEY", "sensitive")
    groups = groups_of(vault, "API_KEY")
    assert "external" in groups
    assert "sensitive" in groups


def test_remove_from_group_returns_true(vault):
    assign_group(vault, "DB_PASS", "database")
    result = remove_from_group(vault, "DB_PASS", "database")
    assert result is True
    assert "DB_PASS" not in members_of(vault, "database")


def test_remove_from_group_deletes_empty_group(vault):
    assign_group(vault, "DB_PASS", "database")
    remove_from_group(vault, "DB_PASS", "database")
    assert "database" not in list_groups(vault)


def test_remove_nonexistent_key_returns_false(vault):
    assign_group(vault, "DB_PASS", "database")
    result = remove_from_group(vault, "MISSING", "database")
    assert result is False


def test_list_groups_sorted(vault):
    assign_group(vault, "K", "zebra")
    assign_group(vault, "K", "alpha")
    assert list_groups(vault) == ["alpha", "zebra"]


def test_list_groups_empty(vault):
    assert list_groups(vault) == []


def test_groups_of_unknown_key(vault):
    assert groups_of(vault, "UNKNOWN") == []


def test_delete_group_returns_true(vault):
    assign_group(vault, "X", "temp")
    assert delete_group(vault, "temp") is True
    assert "temp" not in list_groups(vault)


def test_delete_nonexistent_group_returns_false(vault):
    assert delete_group(vault, "ghost") is False


def test_save_called_on_mutation(vault):
    assign_group(vault, "K", "g")
    assert vault.saved
