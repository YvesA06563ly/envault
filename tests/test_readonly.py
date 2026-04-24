"""Tests for envault.readonly."""

from __future__ import annotations

import json
import pytest

from envault.readonly import (
    protect,
    unprotect,
    is_protected,
    list_protected,
    assert_writable,
    _READONLY_KEY,
)


class _FakeVault:
    def __init__(self):
        self._store: dict = {}
        self.saved = False

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value: str):
        self._store[key] = value

    def save(self):
        self.saved = True


@pytest.fixture
def vault():
    return _FakeVault()


def test_protect_marks_key(vault):
    protect(vault, "DB_PASSWORD")
    assert is_protected(vault, "DB_PASSWORD") is True


def test_unprotect_removes_key(vault):
    protect(vault, "API_KEY")
    unprotect(vault, "API_KEY")
    assert is_protected(vault, "API_KEY") is False


def test_unprotect_nonexistent_key_is_noop(vault):
    unprotect(vault, "NONEXISTENT")
    assert is_protected(vault, "NONEXISTENT") is False


def test_is_protected_returns_false_for_unknown(vault):
    assert is_protected(vault, "UNKNOWN_KEY") is False


def test_list_protected_empty(vault):
    assert list_protected(vault) == []


def test_list_protected_returns_sorted(vault):
    protect(vault, "Z_KEY")
    protect(vault, "A_KEY")
    protect(vault, "M_KEY")
    assert list_protected(vault) == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_protected_excludes_unprotected(vault):
    protect(vault, "KEEP")
    protect(vault, "REMOVE")
    unprotect(vault, "REMOVE")
    assert list_protected(vault) == ["KEEP"]


def test_assert_writable_raises_for_protected(vault):
    protect(vault, "SECRET")
    with pytest.raises(PermissionError, match="read-only"):
        assert_writable(vault, "SECRET")


def test_assert_writable_passes_for_unprotected(vault):
    assert_writable(vault, "OPEN_SECRET")  # should not raise


def test_protect_saves_vault(vault):
    protect(vault, "KEY")
    assert vault.saved is True


def test_corrupted_readonly_store_returns_empty(vault):
    vault.set(_READONLY_KEY, "not-valid-json")
    assert list_protected(vault) == []
    assert is_protected(vault, "ANY") is False
