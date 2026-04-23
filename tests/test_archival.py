"""Tests for envault.archival."""

from __future__ import annotations

import pytest

from envault.archival import (
    archive_secret,
    unarchive_secret,
    is_archived,
    list_archived,
    filter_active,
)


class _FakeVault:
    def __init__(self):
        self._store: dict = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        pass


@pytest.fixture()
def vault():
    return _FakeVault()


def test_is_archived_default_false(vault):
    assert is_archived(vault, "MY_KEY") is False


def test_archive_secret_marks_key(vault):
    archive_secret(vault, "DB_PASS")
    assert is_archived(vault, "DB_PASS") is True


def test_unarchive_secret_clears_mark(vault):
    archive_secret(vault, "DB_PASS")
    unarchive_secret(vault, "DB_PASS")
    assert is_archived(vault, "DB_PASS") is False


def test_unarchive_nonexistent_is_safe(vault):
    unarchive_secret(vault, "MISSING")
    assert is_archived(vault, "MISSING") is False


def test_list_archived_empty(vault):
    assert list_archived(vault) == []


def test_list_archived_returns_all_marked(vault):
    archive_secret(vault, "A")
    archive_secret(vault, "B")
    result = list_archived(vault)
    assert set(result) == {"A", "B"}


def test_list_archived_excludes_unarchived(vault):
    archive_secret(vault, "A")
    archive_secret(vault, "B")
    unarchive_secret(vault, "A")
    assert list_archived(vault) == ["B"]


def test_filter_active_excludes_archived(vault):
    archive_secret(vault, "SECRET_A")
    result = filter_active(vault, ["SECRET_A", "SECRET_B", "SECRET_C"])
    assert result == ["SECRET_B", "SECRET_C"]


def test_filter_active_all_active(vault):
    keys = ["X", "Y", "Z"]
    assert filter_active(vault, keys) == keys


def test_filter_active_all_archived(vault):
    archive_secret(vault, "X")
    archive_secret(vault, "Y")
    assert filter_active(vault, ["X", "Y"]) == []


def test_archive_persists_across_calls(vault):
    archive_secret(vault, "PERSIST")
    # Simulate a second call reading from the same vault store
    assert is_archived(vault, "PERSIST") is True
    assert "PERSIST" in list_archived(vault)
