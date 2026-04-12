"""Tests for envault.search module."""

from __future__ import annotations

import pytest

from envault.crypto import encrypt
from envault.search import search_secrets, SearchResult

PASSPHRASE = "test-passphrase"


class _FakeVault:
    def __init__(self, secrets: dict):
        self._data = {"secrets": secrets}

    def load(self):
        return dict(self._data)

    def save(self, data):
        self._data = data


def _make_vault(plain_secrets: dict) -> _FakeVault:
    """Build a FakeVault with encrypted values."""
    encrypted = {k: encrypt(v, PASSPHRASE) for k, v in plain_secrets.items()}
    return _FakeVault(encrypted)


@pytest.fixture
def vault():
    return _make_vault({
        "DB_HOST": "localhost",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "API_SECRET": "xyz789",
        "APP_ENV": "production",
    })


def test_search_by_key_pattern(vault):
    results = search_secrets(vault, PASSPHRASE, key_pattern="DB_*")
    keys = {r.key for r in results}
    assert keys == {"DB_HOST", "DB_PASSWORD"}
    assert all(r.match_type == "key" for r in results)


def test_search_by_value_substring(vault):
    results = search_secrets(vault, PASSPHRASE, value_substring="123")
    keys = {r.key for r in results}
    assert keys == {"API_KEY"}
    assert all(r.match_type == "value" for r in results)


def test_search_by_both_key_and_value(vault):
    results = search_secrets(vault, PASSPHRASE, key_pattern="API_*", value_substring="abc")
    both = [r for r in results if r.match_type == "both"]
    key_only = [r for r in results if r.match_type == "key"]
    assert any(r.key == "API_KEY" for r in both)
    assert any(r.key == "API_SECRET" for r in key_only)


def test_search_case_insensitive_key(vault):
    results = search_secrets(vault, PASSPHRASE, key_pattern="db_*", case_sensitive=False)
    keys = {r.key for r in results}
    assert keys == {"DB_HOST", "DB_PASSWORD"}


def test_search_case_sensitive_key_no_match(vault):
    results = search_secrets(vault, PASSPHRASE, key_pattern="db_*", case_sensitive=True)
    assert results == []


def test_search_value_case_insensitive(vault):
    results = search_secrets(vault, PASSPHRASE, value_substring="LOCALHOST", case_sensitive=False)
    assert any(r.key == "DB_HOST" for r in results)


def test_search_no_match_returns_empty(vault):
    results = search_secrets(vault, PASSPHRASE, key_pattern="NONEXISTENT_*")
    assert results == []


def test_search_results_sorted_by_key(vault):
    results = search_secrets(vault, PASSPHRASE, key_pattern="*")
    keys = [r.key for r in results]
    assert keys == sorted(keys)


def test_search_raises_without_criteria(vault):
    with pytest.raises(ValueError, match="At least one"):
        search_secrets(vault, PASSPHRASE)


def test_search_result_contains_decrypted_value(vault):
    results = search_secrets(vault, PASSPHRASE, key_pattern="APP_ENV")
    assert len(results) == 1
    assert results[0].value == "production"
