"""Tests for envault.targets deployment target management."""

import json
import pytest

from envault.targets import (
    add_target,
    get_target,
    list_targets,
    remove_target,
    TARGETS_KEY,
)


class _FakeVault:
    """Minimal in-memory vault stub."""

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


def test_add_target_stores_entry(vault):
    add_target(vault, "production", "https://prod.example.com", "Live environment")
    raw = vault.get(TARGETS_KEY)
    data = json.loads(raw)
    assert "production" in data
    assert data["production"]["url"] == "https://prod.example.com"
    assert data["production"]["description"] == "Live environment"


def test_add_target_calls_save(vault):
    add_target(vault, "staging", "https://staging.example.com")
    assert vault.saved


def test_add_duplicate_target_raises(vault):
    add_target(vault, "staging", "https://staging.example.com")
    with pytest.raises(ValueError, match="already exists"):
        add_target(vault, "staging", "https://other.example.com")


def test_list_targets_empty(vault):
    assert list_targets(vault) == []


def test_list_targets_returns_all(vault):
    add_target(vault, "prod", "https://prod.example.com")
    add_target(vault, "dev", "https://dev.example.com")
    result = list_targets(vault)
    names = {t["name"] for t in result}
    assert names == {"prod", "dev"}


def test_get_target_existing(vault):
    add_target(vault, "prod", "https://prod.example.com", "Production")
    target = get_target(vault, "prod")
    assert target == {
        "name": "prod",
        "url": "https://prod.example.com",
        "description": "Production",
    }


def test_get_target_missing_returns_none(vault):
    assert get_target(vault, "nonexistent") is None


def test_remove_target(vault):
    add_target(vault, "staging", "https://staging.example.com")
    remove_target(vault, "staging")
    assert get_target(vault, "staging") is None


def test_remove_nonexistent_target_raises(vault):
    with pytest.raises(KeyError, match="not found"):
        remove_target(vault, "ghost")
