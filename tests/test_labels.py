"""Tests for envault.labels."""

from __future__ import annotations

import json
import pytest

from envault.labels import (
    set_label,
    remove_label,
    get_labels,
    find_by_label,
    clear_labels,
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


def test_set_and_get_label(vault):
    set_label(vault, "DB_PASS", "env", "production")
    labels = get_labels(vault, "DB_PASS")
    assert labels == {"env": "production"}


def test_set_multiple_labels(vault):
    set_label(vault, "API_KEY", "env", "staging")
    set_label(vault, "API_KEY", "team", "backend")
    labels = get_labels(vault, "API_KEY")
    assert labels["env"] == "staging"
    assert labels["team"] == "backend"


def test_overwrite_label(vault):
    set_label(vault, "TOKEN", "env", "dev")
    set_label(vault, "TOKEN", "env", "prod")
    assert get_labels(vault, "TOKEN")["env"] == "prod"


def test_remove_existing_label(vault):
    set_label(vault, "SECRET", "tier", "gold")
    result = remove_label(vault, "SECRET", "tier")
    assert result is True
    assert get_labels(vault, "SECRET") == {}


def test_remove_nonexistent_label(vault):
    result = remove_label(vault, "MISSING", "nope")
    assert result is False


def test_get_labels_empty(vault):
    assert get_labels(vault, "UNKNOWN") == {}


def test_find_by_label_key_only(vault):
    set_label(vault, "A", "env", "prod")
    set_label(vault, "B", "env", "dev")
    set_label(vault, "C", "team", "ops")
    result = find_by_label(vault, "env")
    assert set(result) == {"A", "B"}


def test_find_by_label_key_and_value(vault):
    set_label(vault, "A", "env", "prod")
    set_label(vault, "B", "env", "dev")
    result = find_by_label(vault, "env", "prod")
    assert result == ["A"]


def test_find_by_label_no_match(vault):
    set_label(vault, "X", "region", "us-east")
    result = find_by_label(vault, "region", "eu-west")
    assert result == []


def test_clear_labels(vault):
    set_label(vault, "KEY", "a", "1")
    set_label(vault, "KEY", "b", "2")
    clear_labels(vault, "KEY")
    assert get_labels(vault, "KEY") == {}


def test_clear_labels_nonexistent(vault):
    clear_labels(vault, "GHOST")  # should not raise
    assert get_labels(vault, "GHOST") == {}


def test_save_called_on_mutation(vault):
    set_label(vault, "K", "x", "y")
    assert vault.saved
