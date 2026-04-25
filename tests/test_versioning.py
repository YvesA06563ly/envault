"""Tests for envault.versioning."""
from __future__ import annotations

import pytest
from envault.versioning import (
    get_version,
    get_versions,
    latest_version,
    list_versioned_keys,
    purge_versions,
    record_version,
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


@pytest.fixture()
def vault():
    return _FakeVault()


def test_record_version_returns_version_number(vault):
    n = record_version(vault, "DB_PASS", "secret1")
    assert n == 1
    n2 = record_version(vault, "DB_PASS", "secret2")
    assert n2 == 2


def test_get_versions_empty_for_unknown_key(vault):
    assert get_versions(vault, "MISSING") == []


def test_get_versions_returns_history(vault):
    record_version(vault, "API_KEY", "v1")
    record_version(vault, "API_KEY", "v2")
    assert get_versions(vault, "API_KEY") == ["v1", "v2"]


def test_get_version_specific(vault):
    record_version(vault, "TOKEN", "alpha")
    record_version(vault, "TOKEN", "beta")
    assert get_version(vault, "TOKEN", 1) == "alpha"
    assert get_version(vault, "TOKEN", 2) == "beta"


def test_get_version_out_of_range_returns_none(vault):
    record_version(vault, "TOKEN", "only")
    assert get_version(vault, "TOKEN", 0) is None
    assert get_version(vault, "TOKEN", 2) is None


def test_latest_version_zero_when_no_history(vault):
    assert latest_version(vault, "NOTHING") == 0


def test_latest_version_tracks_count(vault):
    record_version(vault, "X", "a")
    record_version(vault, "X", "b")
    record_version(vault, "X", "c")
    assert latest_version(vault, "X") == 3


def test_purge_versions_keep_zero_removes_all(vault):
    record_version(vault, "K", "v1")
    record_version(vault, "K", "v2")
    removed = purge_versions(vault, "K", keep=0)
    assert removed == 2
    assert get_versions(vault, "K") == []


def test_purge_versions_keep_one_retains_latest(vault):
    record_version(vault, "K", "old")
    record_version(vault, "K", "new")
    removed = purge_versions(vault, "K", keep=1)
    assert removed == 1
    assert get_versions(vault, "K") == ["new"]


def test_purge_versions_keep_larger_than_history_removes_nothing(vault):
    record_version(vault, "K", "only")
    removed = purge_versions(vault, "K", keep=10)
    assert removed == 0
    assert get_versions(vault, "K") == ["only"]


def test_list_versioned_keys(vault):
    record_version(vault, "A", "1")
    record_version(vault, "B", "2")
    keys = list_versioned_keys(vault)
    assert set(keys) == {"A", "B"}


def test_vault_save_called_on_record(vault):
    record_version(vault, "S", "val")
    assert vault.saved
