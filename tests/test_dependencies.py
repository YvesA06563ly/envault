"""Tests for envault.dependencies."""

import json
import pytest

from envault.dependencies import (
    add_dependency,
    remove_dependency,
    list_dependencies,
    dependents_of,
    all_dependencies,
)

_DEPS_KEY = "__dependencies__"


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


def test_add_dependency_stores_edge(fv):
    add_dependency(fv, "DB_URL", "DB_PASSWORD")
    deps = json.loads(fv.get(_DEPS_KEY))
    assert "DB_URL" in deps
    assert "DB_PASSWORD" in deps["DB_URL"]


def test_add_dependency_no_duplicates(fv):
    add_dependency(fv, "DB_URL", "DB_PASSWORD")
    add_dependency(fv, "DB_URL", "DB_PASSWORD")
    deps = json.loads(fv.get(_DEPS_KEY))
    assert deps["DB_URL"].count("DB_PASSWORD") == 1


def test_add_dependency_self_raises(fv):
    with pytest.raises(ValueError, match="cannot depend on itself"):
        add_dependency(fv, "KEY", "KEY")


def test_remove_dependency_returns_true_when_exists(fv):
    add_dependency(fv, "A", "B")
    result = remove_dependency(fv, "A", "B")
    assert result is True
    assert list_dependencies(fv, "A") == []


def test_remove_dependency_returns_false_when_missing(fv):
    result = remove_dependency(fv, "A", "B")
    assert result is False


def test_remove_dependency_cleans_empty_key(fv):
    add_dependency(fv, "A", "B")
    remove_dependency(fv, "A", "B")
    deps = all_dependencies(fv)
    assert "A" not in deps


def test_list_dependencies_empty(fv):
    assert list_dependencies(fv, "MISSING") == []


def test_list_dependencies_multiple(fv):
    add_dependency(fv, "APP_KEY", "DB_PASS")
    add_dependency(fv, "APP_KEY", "REDIS_PASS")
    result = list_dependencies(fv, "APP_KEY")
    assert set(result) == {"DB_PASS", "REDIS_PASS"}


def test_dependents_of(fv):
    add_dependency(fv, "A", "SHARED")
    add_dependency(fv, "B", "SHARED")
    add_dependency(fv, "C", "OTHER")
    result = dependents_of(fv, "SHARED")
    assert set(result) == {"A", "B"}


def test_all_dependencies_returns_full_map(fv):
    add_dependency(fv, "X", "Y")
    add_dependency(fv, "X", "Z")
    mapping = all_dependencies(fv)
    assert mapping == {"X": ["Y", "Z"]}


def test_vault_saved_after_add(fv):
    add_dependency(fv, "A", "B")
    assert fv.saved is True


def test_vault_saved_after_remove(fv):
    add_dependency(fv, "A", "B")
    fv.saved = False
    remove_dependency(fv, "A", "B")
    assert fv.saved is True
