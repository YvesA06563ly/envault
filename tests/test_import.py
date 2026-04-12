"""
tests/test_import.py

Tests for envault/import_.py
"""
from __future__ import annotations

import json
import pytest

from envault.import_ import import_secrets, import_secrets_from_file


# ---------------------------------------------------------------------------
# Fake vault
# ---------------------------------------------------------------------------

class _FakeVault:
    def __init__(self):
        self._data: dict = {}
        self.saved = False

    def get(self, key: str):
        return self._data.get(key)

    def set(self, key: str, value: str):
        self._data[key] = value

    def save(self):
        self.saved = True


# ---------------------------------------------------------------------------
# dotenv format
# ---------------------------------------------------------------------------

def test_import_dotenv_basic():
    vault = _FakeVault()
    src = "KEY1=value1\nKEY2=value2\n"
    imported, skipped = import_secrets(vault, src, fmt="dotenv")
    assert imported == 2
    assert skipped == 0
    assert vault._data == {"KEY1": "value1", "KEY2": "value2"}
    assert vault.saved


def test_import_dotenv_ignores_comments_and_blanks():
    vault = _FakeVault()
    src = "# comment\n\nKEY=hello\n"
    imported, _ = import_secrets(vault, src, fmt="dotenv")
    assert imported == 1
    assert vault._data == {"KEY": "hello"}


def test_import_dotenv_strips_quotes():
    vault = _FakeVault()
    src = 'KEY="quoted value"\nKEY2=\'single\'\n'
    import_secrets(vault, src, fmt="dotenv")
    assert vault._data["KEY"] == "quoted value"
    assert vault._data["KEY2"] == "single"


def test_import_dotenv_strips_export_prefix():
    vault = _FakeVault()
    src = "export FOO=bar\n"
    import_secrets(vault, src, fmt="dotenv")
    assert vault._data["FOO"] == "bar"


# ---------------------------------------------------------------------------
# JSON format
# ---------------------------------------------------------------------------

def test_import_json_basic():
    vault = _FakeVault()
    src = json.dumps({"A": "1", "B": "2"})
    imported, skipped = import_secrets(vault, src, fmt="json")
    assert imported == 2
    assert vault._data == {"A": "1", "B": "2"}


def test_import_json_non_dict_raises():
    vault = _FakeVault()
    with pytest.raises(ValueError, match="top-level object"):
        import_secrets(vault, "[1,2,3]", fmt="json")


# ---------------------------------------------------------------------------
# shell format
# ---------------------------------------------------------------------------

def test_import_shell_basic():
    vault = _FakeVault()
    src = 'export DB_URL="postgres://localhost/db"\nexport PORT=5432\n'
    imported, _ = import_secrets(vault, src, fmt="shell")
    assert imported == 2
    assert vault._data["DB_URL"] == "postgres://localhost/db"
    assert vault._data["PORT"] == "5432"


# ---------------------------------------------------------------------------
# overwrite / skip behaviour
# ---------------------------------------------------------------------------

def test_skip_existing_by_default():
    vault = _FakeVault()
    vault._data["KEY"] = "original"
    _, skipped = import_secrets(vault, "KEY=new", fmt="dotenv", overwrite=False)
    assert skipped == 1
    assert vault._data["KEY"] == "original"


def test_overwrite_existing_when_flag_set():
    vault = _FakeVault()
    vault._data["KEY"] = "original"
    imported, skipped = import_secrets(vault, "KEY=new", fmt="dotenv", overwrite=True)
    assert imported == 1
    assert skipped == 0
    assert vault._data["KEY"] == "new"


# ---------------------------------------------------------------------------
# unknown format
# ---------------------------------------------------------------------------

def test_unknown_format_raises():
    vault = _FakeVault()
    with pytest.raises(ValueError, match="Unknown import format"):
        import_secrets(vault, "KEY=val", fmt="xml")


# ---------------------------------------------------------------------------
# import_secrets_from_file
# ---------------------------------------------------------------------------

def test_import_from_file_json(tmp_path):
    vault = _FakeVault()
    p = tmp_path / "secrets.json"
    p.write_text(json.dumps({"X": "42"}))
    imported, _ = import_secrets_from_file(vault, p)
    assert imported == 1
    assert vault._data["X"] == "42"


def test_import_from_file_dotenv(tmp_path):
    vault = _FakeVault()
    p = tmp_path / ".env"
    p.write_text("HELLO=world\n")
    imported, _ = import_secrets_from_file(vault, p)
    assert imported == 1
    assert vault._data["HELLO"] == "world"
