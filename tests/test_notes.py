"""Tests for envault.notes."""

from __future__ import annotations

import pytest
from envault import notes as notes_mod


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


def test_set_and_get_note(vault):
    notes_mod.set_note(vault, "DB_PASS", "Rotated monthly.")
    assert notes_mod.get_note(vault, "DB_PASS") == "Rotated monthly."


def test_get_missing_note_returns_none(vault):
    assert notes_mod.get_note(vault, "MISSING") is None


def test_set_note_saves_vault(vault):
    notes_mod.set_note(vault, "KEY", "some text")
    assert vault.saved


def test_overwrite_note(vault):
    notes_mod.set_note(vault, "KEY", "first")
    notes_mod.set_note(vault, "KEY", "second")
    assert notes_mod.get_note(vault, "KEY") == "second"


def test_remove_existing_note(vault):
    notes_mod.set_note(vault, "KEY", "hello")
    result = notes_mod.remove_note(vault, "KEY")
    assert result is True
    assert notes_mod.get_note(vault, "KEY") is None


def test_remove_missing_note_returns_false(vault):
    result = notes_mod.remove_note(vault, "GHOST")
    assert result is False


def test_list_notes_empty(vault):
    assert notes_mod.list_notes(vault) == {}


def test_list_notes_multiple(vault):
    notes_mod.set_note(vault, "A", "note a")
    notes_mod.set_note(vault, "B", "note b")
    result = notes_mod.list_notes(vault)
    assert result == {"A": "note a", "B": "note b"}


def test_list_notes_returns_copy(vault):
    notes_mod.set_note(vault, "X", "text")
    result = notes_mod.list_notes(vault)
    result["Y"] = "injected"
    assert notes_mod.get_note(vault, "Y") is None
