"""Tests for envault.diff module."""

from __future__ import annotations

from typing import Dict

import pytest

from envault.diff import DiffEntry, diff_from_text, diff_secrets
from envault.crypto import encrypt

PASS = "test-passphrase"


class _FakeVault:
    def __init__(self, data: Dict[str, str] | None = None):
        self._data: Dict[str, str] = data or {}

    def get(self, key: str):
        return self._data.get(key)

    def set(self, key: str, value: str):
        self._data[key] = value

    def save(self):
        pass

    def all_keys(self):
        return list(self._data.keys())


def _vault_with(secrets: Dict[str, str]) -> _FakeVault:
    v = _FakeVault()
    for k, val in secrets.items():
        v.set(k, encrypt(val, PASS))
    return v


# ---------------------------------------------------------------------------
# diff_secrets
# ---------------------------------------------------------------------------

def test_diff_added_key():
    vault = _vault_with({"DB_URL": "postgres://localhost"})
    other = {"DB_URL": "postgres://localhost", "NEW_KEY": "new-value"}
    entries = diff_secrets(vault, PASS, other)
    assert any(e.key == "NEW_KEY" and e.status == "added" for e in entries)


def test_diff_removed_key():
    vault = _vault_with({"DB_URL": "postgres://localhost", "OLD_KEY": "old"})
    other = {"DB_URL": "postgres://localhost"}
    entries = diff_secrets(vault, PASS, other)
    assert any(e.key == "OLD_KEY" and e.status == "removed" for e in entries)


def test_diff_changed_key():
    vault = _vault_with({"SECRET": "old-secret"})
    other = {"SECRET": "new-secret"}
    entries = diff_secrets(vault, PASS, other)
    assert len(entries) == 1
    assert entries[0].status == "changed"
    assert entries[0].vault_value == "old-secret"
    assert entries[0].other_value == "new-secret"


def test_diff_unchanged_excluded_by_default():
    vault = _vault_with({"KEY": "value"})
    other = {"KEY": "value"}
    entries = diff_secrets(vault, PASS, other)
    assert entries == []


def test_diff_unchanged_included_when_requested():
    vault = _vault_with({"KEY": "value"})
    other = {"KEY": "value"}
    entries = diff_secrets(vault, PASS, other, include_unchanged=True)
    assert len(entries) == 1
    assert entries[0].status == "unchanged"


def test_diff_empty_vault_and_empty_other():
    vault = _vault_with({})
    entries = diff_secrets(vault, PASS, {})
    assert entries == []


# ---------------------------------------------------------------------------
# diff_from_text
# ---------------------------------------------------------------------------

def test_diff_from_dotenv_text():
    vault = _vault_with({"API_KEY": "abc123"})
    text = "API_KEY=xyz789\nNEW_VAR=hello\n"
    entries = diff_from_text(vault, PASS, text, fmt="dotenv")
    statuses = {e.key: e.status for e in entries}
    assert statuses["API_KEY"] == "changed"
    assert statuses["NEW_VAR"] == "added"


def test_diff_from_json_text():
    vault = _vault_with({"TOKEN": "t1"})
    import json
    text = json.dumps({"TOKEN": "t2", "EXTRA": "val"})
    entries = diff_from_text(vault, PASS, text, fmt="json")
    statuses = {e.key: e.status for e in entries}
    assert statuses["TOKEN"] == "changed"
    assert statuses["EXTRA"] == "added"


def test_diff_unsupported_format_raises():
    vault = _vault_with({})
    with pytest.raises(ValueError, match="Unsupported format"):
        diff_from_text(vault, PASS, "", fmt="yaml")
