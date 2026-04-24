"""Tests for envault.cascade."""

from __future__ import annotations

import json
import pytest

from envault.cascade import (
    add_cascade,
    remove_cascade,
    list_cascade,
    list_all_cascades,
    resolve_cascade,
)


class _FakeVault:
    def __init__(self):
        self._store: dict[str, str] = {}
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


def test_add_cascade_single(vault):
    add_cascade(vault, "DB_PASS", "DB_URL")
    assert list_cascade(vault, "DB_PASS") == ["DB_URL"]


def test_add_cascade_multiple_targets(vault):
    add_cascade(vault, "DB_PASS", "DB_URL")
    add_cascade(vault, "DB_PASS", "DB_REPLICA_URL")
    targets = list_cascade(vault, "DB_PASS")
    assert "DB_URL" in targets
    assert "DB_REPLICA_URL" in targets
    assert len(targets) == 2


def test_add_cascade_idempotent(vault):
    add_cascade(vault, "A", "B")
    add_cascade(vault, "A", "B")
    assert list_cascade(vault, "A") == ["B"]


def test_remove_cascade_existing(vault):
    add_cascade(vault, "A", "B")
    result = remove_cascade(vault, "A", "B")
    assert result is True
    assert list_cascade(vault, "A") == []


def test_remove_cascade_nonexistent(vault):
    result = remove_cascade(vault, "A", "B")
    assert result is False


def test_remove_cascade_partial(vault):
    add_cascade(vault, "A", "B")
    add_cascade(vault, "A", "C")
    remove_cascade(vault, "A", "B")
    assert list_cascade(vault, "A") == ["C"]


def test_list_all_cascades(vault):
    add_cascade(vault, "A", "B")
    add_cascade(vault, "X", "Y")
    all_c = list_all_cascades(vault)
    assert "A" in all_c
    assert "X" in all_c


def test_resolve_cascade_direct(vault):
    add_cascade(vault, "A", "B")
    assert resolve_cascade(vault, "A") == ["B"]


def test_resolve_cascade_transitive(vault):
    add_cascade(vault, "A", "B")
    add_cascade(vault, "B", "C")
    resolved = resolve_cascade(vault, "A")
    assert resolved == ["B", "C"]


def test_resolve_cascade_cycle_safe(vault):
    add_cascade(vault, "A", "B")
    add_cascade(vault, "B", "A")  # cycle
    resolved = resolve_cascade(vault, "A")
    assert "B" in resolved
    assert resolved.count("A") == 0  # cycle not re-entered


def test_vault_saved_after_add(vault):
    add_cascade(vault, "A", "B")
    assert vault.saved is True


def test_list_cascade_empty(vault):
    assert list_cascade(vault, "NONEXISTENT") == []
