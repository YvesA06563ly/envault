"""CLI tests for envault.cli_compliance."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_compliance import compliance_group
from envault.compliance import assign_framework


class FV:
    def __init__(self):
        self._store: dict = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        pass

    def load(self):
        return dict(self._store)


def _run(vault, *args):
    runner = CliRunner()
    return runner.invoke(compliance_group, list(args), obj={"vault": vault})


def test_assign_cmd(tmp_path):
    vault = FV()
    result = _run(vault, "assign", "DB_PASS", "pci-dss")
    assert result.exit_code == 0
    assert "Assigned" in result.output


def test_assign_unknown_framework(tmp_path):
    vault = FV()
    result = _run(vault, "assign", "KEY", "bad-fw")
    assert result.exit_code != 0
    assert "Unknown framework" in result.output


def test_remove_cmd():
    vault = FV()
    assign_framework(vault, "API_KEY", "gdpr")
    result = _run(vault, "remove", "API_KEY", "gdpr")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_show_cmd_with_frameworks():
    vault = FV()
    assign_framework(vault, "SECRET", "soc2")
    result = _run(vault, "show", "SECRET")
    assert result.exit_code == 0
    assert "soc2" in result.output


def test_show_cmd_no_frameworks():
    vault = FV()
    result = _run(vault, "show", "MISSING")
    assert result.exit_code == 0
    assert "No frameworks" in result.output


def test_list_cmd():
    vault = FV()
    assign_framework(vault, "KEY_A", "hipaa")
    assign_framework(vault, "KEY_B", "hipaa")
    result = _run(vault, "list", "hipaa")
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output


def test_report_cmd():
    vault = FV()
    vault._store["DB_PASS"] = "encrypted"
    vault._store["API_KEY"] = "encrypted"
    assign_framework(vault, "DB_PASS", "iso27001")
    result = _run(vault, "report", "iso27001")
    assert result.exit_code == 0
    assert "Coverage" in result.output
