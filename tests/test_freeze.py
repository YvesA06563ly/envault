"""Tests for envault.freeze."""

from __future__ import annotations

import pytest

from envault.freeze import (
    assert_not_frozen,
    freeze,
    is_frozen,
    list_frozen,
    unfreeze,
)


class _FakeVault:
    def __init__(self, secrets: dict | None = None):
        self._secrets = dict(secrets or {})
        self._store: dict = {}
        self.saved = False

    def load(self) -> dict:
        return dict(self._secrets)

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value) -> None:
        self._store[key] = value

    def save(self) -> None:
        self.saved = True


@pytest.fixture()
def vault():
    return _FakeVault(secrets={"DB_PASS": "secret", "API_KEY": "abc123"})


def test_freeze_marks_key(vault):
    freeze(vault, "DB_PASS")
    assert is_frozen(vault, "DB_PASS") is True


def test_freeze_persists(vault):
    freeze(vault, "DB_PASS")
    assert vault.saved is True


def test_freeze_unknown_key_raises(vault):
    with pytest.raises(KeyError, match="MISSING"):
        freeze(vault, "MISSING")


def test_unfreeze_removes_mark(vault):
    freeze(vault, "DB_PASS")
    unfreeze(vault, "DB_PASS")
    assert is_frozen(vault, "DB_PASS") is False


def test_unfreeze_nonexistent_is_noop(vault):
    unfreeze(vault, "NEVER_FROZEN")  # should not raise


def test_is_frozen_default_false(vault):
    assert is_frozen(vault, "API_KEY") is False


def test_list_frozen_empty(vault):
    assert list_frozen(vault) == []


def test_list_frozen_multiple(vault):
    freeze(vault, "DB_PASS")
    freeze(vault, "API_KEY")
    result = list_frozen(vault)
    assert result == ["API_KEY", "DB_PASS"]


def test_list_frozen_excludes_unfrozen(vault):
    freeze(vault, "DB_PASS")
    freeze(vault, "API_KEY")
    unfreeze(vault, "API_KEY")
    assert list_frozen(vault) == ["DB_PASS"]


def test_assert_not_frozen_raises_when_frozen(vault):
    freeze(vault, "DB_PASS")
    with pytest.raises(PermissionError, match="frozen"):
        assert_not_frozen(vault, "DB_PASS")


def test_assert_not_frozen_passes_when_clear(vault):
    assert_not_frozen(vault, "API_KEY")  # should not raise
