"""Tests for envault.checksum."""

import json
import pytest

from envault.checksum import (
    record_checksum,
    verify_checksum,
    get_checksum,
    remove_checksum,
    list_checksums,
    _hash,
    _META_KEY,
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
def fv():
    return _FakeVault()


def test_record_checksum_returns_hex_digest(fv):
    digest = record_checksum(fv, "DB_PASS", "s3cr3t")
    assert digest == _hash("s3cr3t")
    assert len(digest) == 64  # SHA-256 hex


def test_record_checksum_persists(fv):
    record_checksum(fv, "API_KEY", "abc123")
    stored = json.loads(fv._store[_META_KEY])
    assert "API_KEY" in stored
    assert stored["API_KEY"] == _hash("abc123")


def test_verify_checksum_correct_value(fv):
    record_checksum(fv, "TOKEN", "mytoken")
    assert verify_checksum(fv, "TOKEN", "mytoken") is True


def test_verify_checksum_wrong_value(fv):
    record_checksum(fv, "TOKEN", "mytoken")
    assert verify_checksum(fv, "TOKEN", "wrongtoken") is False


def test_verify_checksum_missing_key(fv):
    assert verify_checksum(fv, "NONEXISTENT", "value") is False


def test_get_checksum_returns_digest(fv):
    record_checksum(fv, "SECRET", "val")
    assert get_checksum(fv, "SECRET") == _hash("val")


def test_get_checksum_missing_returns_none(fv):
    assert get_checksum(fv, "MISSING") is None


def test_remove_checksum_returns_true_when_exists(fv):
    record_checksum(fv, "K", "v")
    assert remove_checksum(fv, "K") is True
    assert get_checksum(fv, "K") is None


def test_remove_checksum_returns_false_when_missing(fv):
    assert remove_checksum(fv, "NOPE") is False


def test_list_checksums_empty(fv):
    assert list_checksums(fv) == {}


def test_list_checksums_multiple(fv):
    record_checksum(fv, "A", "1")
    record_checksum(fv, "B", "2")
    result = list_checksums(fv)
    assert set(result.keys()) == {"A", "B"}
    assert result["A"] == _hash("1")
    assert result["B"] == _hash("2")


def test_vault_save_called(fv):
    record_checksum(fv, "X", "y")
    assert fv.saved is True
