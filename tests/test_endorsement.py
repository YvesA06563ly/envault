"""Tests for envault.endorsement."""

from __future__ import annotations

import pytest
from envault import endorsement as endr


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
def fv():
    return _FakeVault()


def test_endorse_adds_user(fv):
    endr.endorse(fv, "DB_PASS", "alice")
    assert "alice" in endr.get_endorsers(fv, "DB_PASS")


def test_endorse_multiple_users(fv):
    endr.endorse(fv, "DB_PASS", "alice")
    endr.endorse(fv, "DB_PASS", "bob")
    endorsers = endr.get_endorsers(fv, "DB_PASS")
    assert "alice" in endorsers
    assert "bob" in endorsers


def test_endorse_idempotent(fv):
    endr.endorse(fv, "API_KEY", "alice")
    endr.endorse(fv, "API_KEY", "alice")
    assert endr.endorsement_count(fv, "API_KEY") == 1


def test_revoke_endorsement_removes_user(fv):
    endr.endorse(fv, "SECRET", "alice")
    result = endr.revoke_endorsement(fv, "SECRET", "alice")
    assert result is True
    assert "alice" not in endr.get_endorsers(fv, "SECRET")


def test_revoke_nonexistent_returns_false(fv):
    result = endr.revoke_endorsement(fv, "SECRET", "ghost")
    assert result is False


def test_revoke_last_endorser_removes_key(fv):
    endr.endorse(fv, "TOKEN", "alice")
    endr.revoke_endorsement(fv, "TOKEN", "alice")
    assert endr.get_endorsers(fv, "TOKEN") == []


def test_is_endorsed_by(fv):
    endr.endorse(fv, "X", "carol")
    assert endr.is_endorsed_by(fv, "X", "carol") is True
    assert endr.is_endorsed_by(fv, "X", "dave") is False


def test_endorsement_count(fv):
    assert endr.endorsement_count(fv, "EMPTY") == 0
    endr.endorse(fv, "EMPTY", "u1")
    endr.endorse(fv, "EMPTY", "u2")
    assert endr.endorsement_count(fv, "EMPTY") == 2


def test_list_endorsed_returns_only_endorsed(fv):
    endr.endorse(fv, "KEY_A", "alice")
    endr.endorse(fv, "KEY_B", "bob")
    result = endr.list_endorsed(fv)
    assert "KEY_A" in result
    assert "KEY_B" in result


def test_list_endorsed_empty(fv):
    assert endr.list_endorsed(fv) == {}


def test_save_called_on_endorse(fv):
    endr.endorse(fv, "K", "u")
    assert fv.saved is True


def test_endorsers_sorted(fv):
    endr.endorse(fv, "K", "zara")
    endr.endorse(fv, "K", "alice")
    endr.endorse(fv, "K", "mike")
    assert endr.get_endorsers(fv, "K") == ["alice", "mike", "zara"]
