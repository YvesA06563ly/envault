"""Tests for envault.vault Vault class."""

import pytest
from pathlib import Path
from envault.vault import Vault


PASS = "vault-pass-phrase"


@pytest.fixture
def vault(tmp_path: Path) -> Vault:
    return Vault(tmp_path / "vault.enc")


def test_load_empty_vault(vault: Vault):
    secrets = vault.load(PASS)
    assert secrets == {}


def test_set_and_load(vault: Vault):
    vault.set_secret("DB_URL", "postgres://localhost/db", PASS)
    secrets = vault.load(PASS)
    assert secrets["DB_URL"] == "postgres://localhost/db"


def test_set_multiple_secrets(vault: Vault):
    vault.set_secret("KEY_A", "value_a", PASS)
    vault.set_secret("KEY_B", "value_b", PASS)
    secrets = vault.load(PASS)
    assert len(secrets) == 2
    assert secrets["KEY_A"] == "value_a"
    assert secrets["KEY_B"] == "value_b"


def test_overwrite_existing_key(vault: Vault):
    vault.set_secret("TOKEN", "old", PASS)
    vault.set_secret("TOKEN", "new", PASS)
    assert vault.load(PASS)["TOKEN"] == "new"


def test_delete_existing_key(vault: Vault):
    vault.set_secret("REMOVE_ME", "bye", PASS)
    removed = vault.delete_secret("REMOVE_ME", PASS)
    assert removed is True
    assert "REMOVE_ME" not in vault.load(PASS)


def test_delete_nonexistent_key(vault: Vault):
    removed = vault.delete_secret("GHOST", PASS)
    assert removed is False


def test_wrong_passphrase_raises(vault: Vault):
    vault.set_secret("X", "y", PASS)
    with pytest.raises(ValueError):
        vault.load("wrong-pass")
