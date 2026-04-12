"""Tests for envault.snapshot."""

from __future__ import annotations

import json
import pytest

from envault import snapshot as snap


class _FakeVault:
    def __init__(self, initial: dict | None = None):
        self._store: dict[str, str] = initial or {}
        self.saved = False

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value: str):
        self._store[key] = value

    def save(self):
        self.saved = True


@pytest.fixture
def vault():
    return _FakeVault({"DB_URL": "postgres://localhost", "API_KEY": "abc123"})


def test_create_snapshot_captures_keys(vault):
    entry = snap.create_snapshot(vault, "v1", ["DB_URL", "API_KEY"])
    assert entry["secrets"]["DB_URL"] == "postgres://localhost"
    assert entry["secrets"]["API_KEY"] == "abc123"
    assert "created_at" in entry
    assert vault.saved


def test_create_snapshot_skips_missing_keys(vault):
    entry = snap.create_snapshot(vault, "v1", ["DB_URL", "MISSING_KEY"])
    assert "DB_URL" in entry["secrets"]
    assert "MISSING_KEY" not in entry["secrets"]


def test_list_snapshots_empty(vault):
    result = snap.list_snapshots(vault)
    assert result == []


def test_list_snapshots_returns_entries(vault):
    snap.create_snapshot(vault, "v1", ["DB_URL"])
    snap.create_snapshot(vault, "v2", ["API_KEY"])
    entries = snap.list_snapshots(vault)
    names = [e["name"] for e in entries]
    assert "v1" in names
    assert "v2" in names


def test_restore_snapshot(vault):
    snap.create_snapshot(vault, "backup", ["DB_URL", "API_KEY"])
    vault.set("DB_URL", "changed")
    restored = snap.restore_snapshot(vault, "backup")
    assert "DB_URL" in restored
    assert vault.get("DB_URL") == "postgres://localhost"


def test_restore_missing_snapshot_raises(vault):
    with pytest.raises(KeyError, match="no-such"):
        snap.restore_snapshot(vault, "no-such")


def test_delete_snapshot(vault):
    snap.create_snapshot(vault, "temp", ["DB_URL"])
    snap.delete_snapshot(vault, "temp")
    entries = snap.list_snapshots(vault)
    assert all(e["name"] != "temp" for e in entries)


def test_delete_missing_snapshot_raises(vault):
    with pytest.raises(KeyError, match="ghost"):
        snap.delete_snapshot(vault, "ghost")


def test_overwrite_snapshot(vault):
    snap.create_snapshot(vault, "v1", ["DB_URL"])
    vault.set("DB_URL", "new_url")
    snap.create_snapshot(vault, "v1", ["DB_URL"])
    entries = snap.list_snapshots(vault)
    v1 = next(e for e in entries if e["name"] == "v1")
    # restore should give new_url
    snap.restore_snapshot(vault, "v1")
    assert vault.get("DB_URL") == "new_url"
