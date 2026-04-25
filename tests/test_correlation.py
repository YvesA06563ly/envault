"""Tests for envault.correlation."""
import json
import pytest

from envault.correlation import (
    link, unlink, get_correlates, clear_correlates, list_all,
)

_CORR_KEY = "__correlations__"


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


def test_link_creates_bidirectional(vault):
    link(vault, "DB_HOST", "DB_PORT")
    assert "DB_PORT" in get_correlates(vault, "DB_HOST")
    assert "DB_HOST" in get_correlates(vault, "DB_PORT")


def test_link_saves_vault(vault):
    link(vault, "A", "B")
    assert vault.saved


def test_link_self_raises(vault):
    with pytest.raises(ValueError):
        link(vault, "KEY", "KEY")


def test_link_idempotent(vault):
    link(vault, "A", "B")
    link(vault, "A", "B")
    assert get_correlates(vault, "A").count("B") == 1


def test_unlink_removes_both_directions(vault):
    link(vault, "X", "Y")
    removed = unlink(vault, "X", "Y")
    assert removed is True
    assert get_correlates(vault, "X") == []
    assert get_correlates(vault, "Y") == []


def test_unlink_nonexistent_returns_false(vault):
    assert unlink(vault, "A", "B") is False


def test_clear_correlates(vault):
    link(vault, "A", "B")
    link(vault, "A", "C")
    clear_correlates(vault, "A")
    assert get_correlates(vault, "A") == []
    assert "A" not in get_correlates(vault, "B")
    assert "A" not in get_correlates(vault, "C")


def test_get_correlates_empty(vault):
    assert get_correlates(vault, "MISSING") == []


def test_list_all_empty(vault):
    assert list_all(vault) == {}


def test_list_all_returns_full_map(vault):
    link(vault, "A", "B")
    link(vault, "A", "C")
    data = list_all(vault)
    assert set(data["A"]) == {"B", "C"}
    assert data["B"] == ["A"]
    assert data["C"] == ["A"]


def test_multiple_independent_pairs(vault):
    link(vault, "P", "Q")
    link(vault, "R", "S")
    assert get_correlates(vault, "P") == ["Q"]
    assert get_correlates(vault, "R") == ["S"]
