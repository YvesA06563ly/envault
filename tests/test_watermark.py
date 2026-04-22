"""Tests for envault.watermark."""

from __future__ import annotations

import json
import pytest

from envault.watermark import (
    set_watermark,
    get_watermark,
    remove_watermark,
    verify_watermark,
    list_watermarks,
    _WATERMARK_KEY,
    _fingerprint,
)


class _FakeVault:
    def __init__(self, data: dict | None = None):
        self._data: dict = data or {}
        self.saved = False

    def get(self, key: str):
        return self._data.get(key)

    def set(self, key: str, value: str):
        self._data[key] = value

    def save(self):
        self.saved = True


@pytest.fixture()
def vault():
    v = _FakeVault({"DB_PASS": "s3cr3t", "API_KEY": "abc123"})
    return v


def test_set_watermark_returns_mark(vault):
    mark = set_watermark(vault, "DB_PASS", "alice", note="initial")
    assert mark["author"] == "alice"
    assert mark["note"] == "initial"
    assert len(mark["fingerprint"]) == 16


def test_set_watermark_persists(vault):
    set_watermark(vault, "DB_PASS", "alice")
    assert vault.saved
    raw = vault.get(_WATERMARK_KEY)
    data = json.loads(raw)
    assert "DB_PASS" in data


def test_get_watermark_returns_none_when_absent(vault):
    assert get_watermark(vault, "MISSING") is None


def test_get_watermark_returns_stored(vault):
    set_watermark(vault, "API_KEY", "bob")
    mark = get_watermark(vault, "API_KEY")
    assert mark is not None
    assert mark["author"] == "bob"


def test_verify_watermark_valid(vault):
    set_watermark(vault, "DB_PASS", "alice")
    assert verify_watermark(vault, "DB_PASS") is True


def test_verify_watermark_invalid_after_value_change(vault):
    set_watermark(vault, "DB_PASS", "alice")
    # Tamper with the secret value directly
    vault._data["DB_PASS"] = "tampered!"
    assert verify_watermark(vault, "DB_PASS") is False


def test_verify_watermark_missing_returns_false(vault):
    assert verify_watermark(vault, "NO_MARK") is False


def test_remove_watermark_existing(vault):
    set_watermark(vault, "DB_PASS", "alice")
    result = remove_watermark(vault, "DB_PASS")
    assert result is True
    assert get_watermark(vault, "DB_PASS") is None


def test_remove_watermark_nonexistent(vault):
    result = remove_watermark(vault, "GHOST")
    assert result is False


def test_list_watermarks_empty(vault):
    assert list_watermarks(vault) == []


def test_list_watermarks_multiple(vault):
    set_watermark(vault, "DB_PASS", "alice")
    set_watermark(vault, "API_KEY", "bob", note="ci")
    marks = list_watermarks(vault)
    keys = [m["key"] for m in marks]
    assert "DB_PASS" in keys
    assert "API_KEY" in keys


def test_fingerprint_deterministic():
    fp1 = _fingerprint("KEY", "val", "user")
    fp2 = _fingerprint("KEY", "val", "user")
    assert fp1 == fp2


def test_fingerprint_differs_on_different_inputs():
    assert _fingerprint("K", "v", "a") != _fingerprint("K", "v", "b")
