"""Integration tests for the namespace CLI commands."""

from __future__ import annotations

import json
import pytest
from click.testing import CliRunner

from envault.cli_namespace import namespace_group
from envault import namespace as ns_mod

_NS_KEY = "__namespaces__"


class FV:
    """Minimal fake vault used by CLI tests."""
    def __init__(self):
        self._store: dict = {}
        self.saved = False

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        self.saved = True

    def load(self):
        pass


def _make_fake_vault(monkeypatch):
    fv = FV()

    def _fake_vault(path, passphrase):
        return fv

    monkeypatch.setattr("envault.cli_namespace.Vault", _fake_vault)
    monkeypatch.setattr("envault.cli_namespace._get_passphrase", lambda: "s")
    return fv


def test_assign_cmd(monkeypatch):
    fv = _make_fake_vault(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(namespace_group, ["assign", "DB_PASS", "database"])
    assert result.exit_code == 0
    assert "database" in result.output
    assert ns_mod.get_namespace(fv, "DB_PASS") == "database"


def test_assign_invalid_namespace(monkeypatch):
    _make_fake_vault(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(namespace_group, ["assign", "KEY", "bad/ns"])
    assert result.exit_code != 0


def test_remove_cmd_existing(monkeypatch):
    fv = _make_fake_vault(monkeypatch)
    ns_mod.assign_namespace(fv, "API_KEY", "api")
    runner = CliRunner()
    result = runner.invoke(namespace_group, ["remove", "API_KEY"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_cmd_missing(monkeypatch):
    _make_fake_vault(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(namespace_group, ["remove", "GHOST"])
    assert result.exit_code == 0
    assert "no namespace" in result.output.lower()


def test_show_cmd_assigned(monkeypatch):
    fv = _make_fake_vault(monkeypatch)
    ns_mod.assign_namespace(fv, "DB_PASS", "database")
    runner = CliRunner()
    result = runner.invoke(namespace_group, ["show", "DB_PASS"])
    assert result.exit_code == 0
    assert "database" in result.output


def test_show_cmd_unassigned(monkeypatch):
    _make_fake_vault(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(namespace_group, ["show", "MISSING"])
    assert result.exit_code == 0
    assert "not assigned" in result.output


def test_list_cmd_all(monkeypatch):
    fv = _make_fake_vault(monkeypatch)
    ns_mod.assign_namespace(fv, "DB_PASS", "database")
    ns_mod.assign_namespace(fv, "API_KEY", "api")
    runner = CliRunner()
    result = runner.invoke(namespace_group, ["list"])
    assert result.exit_code == 0
    assert "database" in result.output
    assert "api" in result.output


def test_list_cmd_filtered(monkeypatch):
    fv = _make_fake_vault(monkeypatch)
    ns_mod.assign_namespace(fv, "DB_PASS", "database")
    ns_mod.assign_namespace(fv, "API_KEY", "api")
    runner = CliRunner()
    result = runner.invoke(namespace_group, ["list", "--namespace", "database"])
    assert result.exit_code == 0
    assert "DB_PASS" in result.output
    assert "API_KEY" not in result.output
