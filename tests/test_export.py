"""Tests for envault.export."""

import json
import pytest

from envault.crypto import encrypt
from envault.export import (
    export_dotenv,
    export_json,
    export_shell,
    export_secrets,
    SUPPORTED_FORMATS,
)

PASSPHRASE = "test-passphrase-export"


class _FakeVault:
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        pass


def _make_vault(secrets: dict) -> _FakeVault:
    vault = _FakeVault()
    encrypted = {k: encrypt(v, PASSPHRASE) for k, v in secrets.items()}
    vault.set("__secrets__", encrypted)
    return vault


# --- unit tests for format helpers ---

def test_export_dotenv_basic():
    result = export_dotenv({"FOO": "bar", "BAZ": "qux"})
    assert 'FOO="bar"' in result
    assert 'BAZ="qux"' in result


def test_export_dotenv_escapes_double_quotes():
    result = export_dotenv({"KEY": 'say "hello"'})
    assert 'say \\"hello\\"' in result


def test_export_dotenv_empty_value():
    """Empty string values should produce an empty quoted assignment."""
    result = export_dotenv({"EMPTY": ""})
    assert 'EMPTY=""' in result


def test_export_json_valid():
    result = export_json({"A": "1", "B": "2"})
    parsed = json.loads(result)
    assert parsed == {"A": "1", "B": "2"}


def test_export_json_empty():
    """An empty dict should produce a valid empty JSON object."""
    result = export_json({})
    assert json.loads(result) == {}


def test_export_shell_basic():
    result = export_shell({"MY_VAR": "hello"})
    assert "export MY_VAR='hello'" in result


def test_export_shell_escapes_single_quotes():
    result = export_shell({"KEY": "it's alive"})
    assert "it'\\''s alive" in result


# --- integration tests via export_secrets ---

def test_export_secrets_dotenv():
    vault = _make_vault({"DB_URL": "postgres://localhost/db"})
    out = export_secrets(vault, PASSPHRASE, fmt="dotenv")
    assert 'DB_URL="postgres://localhost/db"' in out


def test_export_secrets_json():
    vault = _make_vault({"TOKEN": "abc123"})
    out = export_secrets(vault, PASSPHRASE, fmt="json")
    data = json.loads(out)
    assert data["TOKEN"] == "abc123"


def test_export_secrets_shell():
    vault = _make_vault({"API_KEY": "secret"})
    out = export_secrets(vault, PASSPHRASE, fmt="shell")
    assert "export API_KEY='secret'" in out


def test_export_secrets_filter_prefix():
    vault = _make_vault({"APP_HOST": "localhost", "APP_PORT": "8080", "DB_PASS": "x"})
    out = export_secrets(vault, PASSPHRASE, fmt="json", filter_prefix="APP_")
    data = json.loads(out)
    assert "APP_HOST" in data
    assert "APP_PORT" in data
    assert "DB_PASS" not in data


def test_export_secrets_filter_prefix_no_matches():
    """A prefix that matches no keys should produce an empty export."""
    vault = _make_vault({"APP_HOST": "localhost", "APP_PORT": "8080"})
    out = export_secrets(vault, PASSPHRASE, fmt="json", filter_prefix="DB_")
    data = json.loads(out)
    assert data == {}


def test_export_secrets_empty_vault():
    vault = _FakeVault()
    out = export_secrets(vault, PASSPHRASE, fmt="dotenv")
    assert out == ""


def test_export_secrets_unsupported_format():
    vault = _make_vault({"X": "y"})
    with pytest.raises(ValueError, match="Unsupported format"):
        export_secrets(vault, PASSPHRASE, fmt="yaml")


def test_supported_formats_constant():
    assert "dotenv" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS
    assert "shell" in SUPPORTED_FORMATS
