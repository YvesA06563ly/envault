"""Tests for envault.delegation."""

import json
import pytest

from envault.delegation import (
    delegate,
    revoke_delegation,
    get_delegations,
    can_delegate,
    list_all_delegations,
    _DELEGATION_KEY,
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


def test_delegate_creates_entry(vault):
    delegate(vault, "DB_PASS", "alice", "bob", ["read"])
    entries = get_delegations(vault, "DB_PASS")
    assert len(entries) == 1
    assert entries[0]["delegator"] == "alice"
    assert entries[0]["delegate"] == "bob"
    assert entries[0]["permissions"] == ["read"]


def test_delegate_default_permission_is_read(vault):
    delegate(vault, "API_KEY", "alice", "charlie")
    entries = get_delegations(vault, "API_KEY")
    assert entries[0]["permissions"] == ["read"]


def test_delegate_overwrites_existing_pair(vault):
    delegate(vault, "DB_PASS", "alice", "bob", ["read"])
    delegate(vault, "DB_PASS", "alice", "bob", ["read", "write"])
    entries = get_delegations(vault, "DB_PASS")
    assert len(entries) == 1
    assert entries[0]["permissions"] == ["read", "write"]


def test_multiple_delegates_for_same_secret(vault):
    delegate(vault, "DB_PASS", "alice", "bob", ["read"])
    delegate(vault, "DB_PASS", "alice", "carol", ["read", "write"])
    entries = get_delegations(vault, "DB_PASS")
    assert len(entries) == 2


def test_revoke_delegation_removes_entry(vault):
    delegate(vault, "DB_PASS", "alice", "bob", ["read"])
    removed = revoke_delegation(vault, "DB_PASS", "alice", "bob")
    assert removed is True
    assert get_delegations(vault, "DB_PASS") == []


def test_revoke_delegation_returns_false_when_not_found(vault):
    removed = revoke_delegation(vault, "DB_PASS", "alice", "nobody")
    assert removed is False


def test_revoke_cleans_up_empty_key(vault):
    delegate(vault, "DB_PASS", "alice", "bob", ["read"])
    revoke_delegation(vault, "DB_PASS", "alice", "bob")
    data = json.loads(vault.get(_DELEGATION_KEY) or "{}")
    assert "DB_PASS" not in data


def test_can_delegate_returns_true_for_granted_permission(vault):
    delegate(vault, "SECRET", "owner", "agent", ["read", "rotate"])
    assert can_delegate(vault, "SECRET", "agent", "read") is True
    assert can_delegate(vault, "SECRET", "agent", "rotate") is True


def test_can_delegate_returns_false_for_missing_permission(vault):
    delegate(vault, "SECRET", "owner", "agent", ["read"])
    assert can_delegate(vault, "SECRET", "agent", "write") is False


def test_can_delegate_returns_false_for_unknown_identity(vault):
    assert can_delegate(vault, "SECRET", "stranger", "read") is False


def test_list_all_delegations(vault):
    delegate(vault, "A", "alice", "bob", ["read"])
    delegate(vault, "B", "carol", "dave", ["write"])
    all_d = list_all_delegations(vault)
    assert "A" in all_d
    assert "B" in all_d


def test_save_is_called(vault):
    delegate(vault, "KEY", "x", "y")
    assert vault.saved is True
