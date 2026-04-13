"""Tests for envault.env_check."""

from __future__ import annotations

from typing import Dict, Optional
import pytest

from envault.crypto import encrypt
from envault.env_check import check_secrets, check_from_file, CheckReport

PASS = "test-passphrase"


class _FakeVault:
    def __init__(self, data: Dict[str, str]):
        self._data = data

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def save(self) -> None:
        pass


def _vault_with(**secrets) -> _FakeVault:
    data = {k: encrypt(v, PASS) for k, v in secrets.items()}
    return _FakeVault(data)


def test_all_present_and_non_empty():
    vault = _vault_with(DB_URL="postgres://localhost/db", API_KEY="abc123")
    report = check_secrets(vault, ["DB_URL", "API_KEY"], PASS)
    assert report.passed
    assert report.missing == []
    assert report.empty == []


def test_missing_key():
    vault = _vault_with(DB_URL="postgres://localhost/db")
    report = check_secrets(vault, ["DB_URL", "API_KEY"], PASS)
    assert not report.passed
    assert "API_KEY" in report.missing


def test_empty_value():
    vault = _vault_with(DB_URL="postgres://localhost/db", API_KEY="")
    report = check_secrets(vault, ["DB_URL", "API_KEY"], PASS)
    assert not report.passed
    assert "API_KEY" in report.empty


def test_whitespace_only_value():
    vault = _vault_with(TOKEN="   ")
    report = check_secrets(vault, ["TOKEN"], PASS)
    assert not report.passed
    assert "TOKEN" in report.empty


def test_wrong_passphrase_marks_non_empty_false():
    vault = _vault_with(SECRET="value")
    report = check_secrets(vault, ["SECRET"], "wrong-pass")
    assert not report.passed
    result = report.results[0]
    assert result.present is True
    assert result.non_empty is False


def test_empty_required_list():
    vault = _vault_with(FOO="bar")
    report = check_secrets(vault, [], PASS)
    assert report.passed
    assert report.results == []


def test_check_from_file(tmp_path):
    keys_file = tmp_path / "required.txt"
    keys_file.write_text("DB_URL\n# comment\nAPI_KEY\n")
    vault = _vault_with(DB_URL="postgres://x", API_KEY="key")
    report = check_from_file(vault, str(keys_file), PASS)
    assert report.passed


def test_check_from_file_missing(tmp_path):
    keys_file = tmp_path / "required.txt"
    keys_file.write_text("DB_URL\nMISSING_KEY\n")
    vault = _vault_with(DB_URL="postgres://x")
    report = check_from_file(vault, str(keys_file), PASS)
    assert not report.passed
    assert "MISSING_KEY" in report.missing
