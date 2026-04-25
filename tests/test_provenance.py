"""Tests for envault.provenance."""

from __future__ import annotations

import json
import pytest

from envault.provenance import (
    clear_provenance,
    get_provenance,
    has_provenance,
    list_provenance,
    set_provenance,
)

_KEY = "__provenance__"


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


def test_set_provenance_stores_record(vault):
    set_provenance(vault, "DB_PASS", "1password", author="alice", note="prod db")
    raw = vault.get(_KEY)
    data = json.loads(raw)
    assert "DB_PASS" in data
    assert data["DB_PASS"]["source"] == "1password"
    assert data["DB_PASS"]["author"] == "alice"
    assert data["DB_PASS"]["note"] == "prod db"
    assert "recorded_at" in data["DB_PASS"]


def test_set_provenance_calls_save(vault):
    set_provenance(vault, "API_KEY", "vault")
    assert vault.saved


def test_get_provenance_returns_record(vault):
    set_provenance(vault, "TOKEN", "env-file", author="bob")
    rec = get_provenance(vault, "TOKEN")
    assert rec is not None
    assert rec["source"] == "env-file"
    assert rec["author"] == "bob"


def test_get_provenance_missing_key_returns_none(vault):
    assert get_provenance(vault, "MISSING") is None


def test_has_provenance_true(vault):
    set_provenance(vault, "X", "ci")
    assert has_provenance(vault, "X") is True


def test_has_provenance_false(vault):
    assert has_provenance(vault, "NOPE") is False


def test_clear_provenance_removes_key(vault):
    set_provenance(vault, "SECRET", "manual")
    clear_provenance(vault, "SECRET")
    assert get_provenance(vault, "SECRET") is None


def test_clear_provenance_nonexistent_is_noop(vault):
    clear_provenance(vault, "GHOST")  # should not raise


def test_list_provenance_returns_all(vault):
    set_provenance(vault, "A", "src-a")
    set_provenance(vault, "B", "src-b")
    records = list_provenance(vault)
    assert set(records.keys()) == {"A", "B"}


def test_list_provenance_empty_vault(vault):
    assert list_provenance(vault) == {}


def test_set_provenance_overwrites_existing(vault):
    set_provenance(vault, "K", "old-source")
    set_provenance(vault, "K", "new-source", author="charlie")
    rec = get_provenance(vault, "K")
    assert rec["source"] == "new-source"
    assert rec["author"] == "charlie"


def test_provenance_optional_fields_default_none(vault):
    set_provenance(vault, "BARE", "direct")
    rec = get_provenance(vault, "BARE")
    assert rec["author"] is None
    assert rec["note"] is None
