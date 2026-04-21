"""Tests for envault.ownership module."""

import json
import pytest

from envault.ownership import (
    set_owner,
    clear_owner,
    get_owner,
    list_owned_by,
    list_all_ownership,
)

_OWNERSHIP_KEY = "__ownership__"


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


def test_get_owner_returns_none_when_unset(vault):
    assert get_owner(vault, "DB_PASS") is None


def test_set_owner_and_get(vault):
    set_owner(vault, "DB_PASS", "alice")
    assert get_owner(vault, "DB_PASS") == "alice"


def test_set_owner_persists_to_vault(vault):
    set_owner(vault, "API_KEY", "bob")
    assert vault.saved is True
    raw = json.loads(vault.get(_OWNERSHIP_KEY))
    assert raw["API_KEY"] == "bob"


def test_set_owner_strips_whitespace(vault):
    set_owner(vault, "TOKEN", "  carol  ")
    assert get_owner(vault, "TOKEN") == "carol"


def test_set_owner_empty_raises(vault):
    with pytest.raises(ValueError):
        set_owner(vault, "KEY", "")


def test_set_owner_whitespace_only_raises(vault):
    with pytest.raises(ValueError):
        set_owner(vault, "KEY", "   ")


def test_clear_owner_removes_key(vault):
    set_owner(vault, "DB_PASS", "alice")
    clear_owner(vault, "DB_PASS")
    assert get_owner(vault, "DB_PASS") is None


def test_clear_owner_nonexistent_is_noop(vault):
    clear_owner(vault, "NONEXISTENT")
    assert get_owner(vault, "NONEXISTENT") is None


def test_list_owned_by_returns_matching_keys(vault):
    set_owner(vault, "DB_PASS", "alice")
    set_owner(vault, "API_KEY", "bob")
    set_owner(vault, "SECRET", "alice")
    result = list_owned_by(vault, "alice")
    assert result == ["DB_PASS", "SECRET"]


def test_list_owned_by_returns_sorted(vault):
    set_owner(vault, "Z_KEY", "dave")
    set_owner(vault, "A_KEY", "dave")
    set_owner(vault, "M_KEY", "dave")
    assert list_owned_by(vault, "dave") == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_owned_by_no_match_returns_empty(vault):
    set_owner(vault, "KEY", "alice")
    assert list_owned_by(vault, "nobody") == []


def test_list_all_ownership_returns_full_map(vault):
    set_owner(vault, "A", "alice")
    set_owner(vault, "B", "bob")
    result = list_all_ownership(vault)
    assert result == {"A": "alice", "B": "bob"}


def test_list_all_ownership_empty_vault(vault):
    assert list_all_ownership(vault) == {}


def test_overwrite_owner(vault):
    set_owner(vault, "KEY", "alice")
    set_owner(vault, "KEY", "bob")
    assert get_owner(vault, "KEY") == "bob"
