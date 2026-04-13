"""Tests for envault.tags."""
from __future__ import annotations

import json
import pytest

from envault.tags import (
    add_tag,
    remove_tag,
    list_tags,
    find_by_tag,
    clear_tags,
    _TAGS_KEY,
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


def test_add_tag_persists(vault):
    add_tag(vault, "DB_URL", "database")
    assert "database" in list_tags(vault, "DB_URL")
    assert vault.saved


def test_add_tag_no_duplicates(vault):
    add_tag(vault, "DB_URL", "database")
    add_tag(vault, "DB_URL", "database")
    assert list_tags(vault, "DB_URL").count("database") == 1


def test_add_multiple_tags(vault):
    add_tag(vault, "API_KEY", "prod")
    add_tag(vault, "API_KEY", "sensitive")
    tags = list_tags(vault, "API_KEY")
    assert "prod" in tags
    assert "sensitive" in tags


def test_remove_tag(vault):
    add_tag(vault, "TOKEN", "prod")
    remove_tag(vault, "TOKEN", "prod")
    assert list_tags(vault, "TOKEN") == []


def test_remove_tag_not_found_raises(vault):
    add_tag(vault, "TOKEN", "prod")
    with pytest.raises(KeyError, match="missing"):
        remove_tag(vault, "TOKEN", "missing")


def test_remove_tag_cleans_up_empty_key(vault):
    add_tag(vault, "X", "only")
    remove_tag(vault, "X", "only")
    raw = vault.get(_TAGS_KEY)
    data = json.loads(raw)
    assert "X" not in data


def test_list_tags_unknown_key(vault):
    assert list_tags(vault, "NONEXISTENT") == []


def test_find_by_tag(vault):
    add_tag(vault, "DB_URL", "prod")
    add_tag(vault, "API_KEY", "prod")
    add_tag(vault, "DEV_TOKEN", "dev")
    result = find_by_tag(vault, "prod")
    assert set(result) == {"DB_URL", "API_KEY"}


def test_find_by_tag_no_matches(vault):
    add_tag(vault, "X", "alpha")
    assert find_by_tag(vault, "beta") == []


def test_clear_tags(vault):
    add_tag(vault, "SECRET", "a")
    add_tag(vault, "SECRET", "b")
    clear_tags(vault, "SECRET")
    assert list_tags(vault, "SECRET") == []


def test_clear_tags_nonexistent_key_is_noop(vault):
    clear_tags(vault, "GHOST")  # should not raise
    assert list_tags(vault, "GHOST") == []
