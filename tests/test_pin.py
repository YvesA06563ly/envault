"""Tests for envault.pin."""

from __future__ import annotations

import json
import pytest

from envault.pin import (
    pin_secret,
    unpin_secret,
    is_pinned,
    list_pins,
    pin_info,
)

_PINS_KEY = "__pins__"


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


def test_pin_secret_marks_key(vault):
    pin_secret(vault, "DB_PASS", "critical prod secret")
    assert is_pinned(vault, "DB_PASS")


def test_pin_secret_saves_vault(vault):
    pin_secret(vault, "API_KEY")
    assert vault.saved


def test_pin_secret_stores_reason(vault):
    pin_secret(vault, "TOKEN", "do not rotate until Q3")
    info = pin_info(vault, "TOKEN")
    assert info is not None
    assert info["reason"] == "do not rotate until Q3"


def test_unpin_removes_key(vault):
    pin_secret(vault, "SECRET")
    result = unpin_secret(vault, "SECRET")
    assert result is True
    assert not is_pinned(vault, "SECRET")


def test_unpin_returns_false_when_not_pinned(vault):
    assert unpin_secret(vault, "NONEXISTENT") is False


def test_is_pinned_false_for_unknown_key(vault):
    assert not is_pinned(vault, "MISSING")


def test_list_pins_empty(vault):
    assert list_pins(vault) == []


def test_list_pins_returns_sorted(vault):
    pin_secret(vault, "Z_KEY", "last")
    pin_secret(vault, "A_KEY", "first")
    pins = list_pins(vault)
    assert [p["key"] for p in pins] == ["A_KEY", "Z_KEY"]


def test_list_pins_includes_reason(vault):
    pin_secret(vault, "MY_KEY", "important")
    pins = list_pins(vault)
    assert pins[0]["reason"] == "important"


def test_pin_info_returns_none_for_unpinned(vault):
    assert pin_info(vault, "GHOST") is None


def test_multiple_pins_coexist(vault):
    pin_secret(vault, "K1", "r1")
    pin_secret(vault, "K2", "r2")
    assert is_pinned(vault, "K1")
    assert is_pinned(vault, "K2")
    assert len(list_pins(vault)) == 2


def test_overwrite_pin_reason(vault):
    pin_secret(vault, "KEY", "old reason")
    pin_secret(vault, "KEY", "new reason")
    assert pin_info(vault, "KEY")["reason"] == "new reason"
    assert len(list_pins(vault)) == 1
