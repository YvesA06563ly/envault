"""Tests for envault.comments."""

from __future__ import annotations

import json
import pytest

from envault.comments import (
    COMMENTS_KEY,
    get_comment,
    keys_with_comments,
    list_comments,
    remove_comment,
    set_comment,
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


@pytest.fixture
def vault():
    return _FakeVault()


def test_get_comment_missing(vault):
    assert get_comment(vault, "DB_PASS") is None


def test_set_and_get_comment(vault):
    set_comment(vault, "DB_PASS", "Primary database password")
    assert get_comment(vault, "DB_PASS") == "Primary database password"


def test_set_comment_persists_json(vault):
    set_comment(vault, "API_KEY", "Third-party API key")
    raw = vault.get(COMMENTS_KEY)
    data = json.loads(raw)
    assert data["API_KEY"] == "Third-party API key"


def test_set_comment_calls_save(vault):
    set_comment(vault, "X", "note")
    assert vault.saved


def test_overwrite_comment(vault):
    set_comment(vault, "KEY", "old")
    set_comment(vault, "KEY", "new")
    assert get_comment(vault, "KEY") == "new"


def test_remove_existing_comment(vault):
    set_comment(vault, "KEY", "some note")
    result = remove_comment(vault, "KEY")
    assert result is True
    assert get_comment(vault, "KEY") is None


def test_remove_nonexistent_comment(vault):
    result = remove_comment(vault, "MISSING")
    assert result is False


def test_list_comments_empty(vault):
    assert list_comments(vault) == {}


def test_list_comments_multiple(vault):
    set_comment(vault, "A", "alpha")
    set_comment(vault, "B", "beta")
    result = list_comments(vault)
    assert result == {"A": "alpha", "B": "beta"}


def test_keys_with_comments_sorted(vault):
    set_comment(vault, "Z_KEY", "z")
    set_comment(vault, "A_KEY", "a")
    set_comment(vault, "M_KEY", "m")
    assert keys_with_comments(vault) == ["A_KEY", "M_KEY", "Z_KEY"]


def test_keys_with_comments_empty(vault):
    assert keys_with_comments(vault) == []
