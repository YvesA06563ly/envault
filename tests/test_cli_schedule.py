"""Tests for envault.cli_schedule CLI commands."""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

from click.testing import CliRunner
from envault.cli_schedule import schedule_group


def _make_fake_vault():
    store = {}

    class FV:
        def get(self, k):
            return store.get(k)

        def set(self, k, v):
            store[k] = v

        def save(self):
            pass

    return FV()


@patch("envault.cli_schedule._get_passphrase", return_value="pw")
@patch("envault.cli_schedule.Vault")
def test_set_schedule_cmd(MockVault, _mock_pp):
    fv = _make_fake_vault()
    MockVault.return_value = fv
    runner = CliRunner()
    result = runner.invoke(schedule_group, ["set", "DB_PASS", "30"])
    assert result.exit_code == 0
    assert "DB_PASS" in result.output
    assert "30" in result.output


@patch("envault.cli_schedule._get_passphrase", return_value="pw")
@patch("envault.cli_schedule.Vault")
def test_set_schedule_invalid_interval(MockVault, _mock_pp):
    fv = _make_fake_vault()
    MockVault.return_value = fv
    runner = CliRunner()
    result = runner.invoke(schedule_group, ["set", "KEY", "0"])
    assert result.exit_code != 0


@patch("envault.cli_schedule._get_passphrase", return_value="pw")
@patch("envault.cli_schedule.Vault")
def test_list_schedules_empty(MockVault, _mock_pp):
    fv = _make_fake_vault()
    MockVault.return_value = fv
    runner = CliRunner()
    result = runner.invoke(schedule_group, ["list"])
    assert result.exit_code == 0
    assert "No schedules" in result.output


@patch("envault.cli_schedule._get_passphrase", return_value="pw")
@patch("envault.cli_schedule.Vault")
def test_remove_schedule_cmd(MockVault, _mock_pp):
    fv = _make_fake_vault()
    MockVault.return_value = fv
    from envault import schedule as sched
    sched.set_schedule(fv, "TOKEN", 14)
    runner = CliRunner()
    result = runner.invoke(schedule_group, ["remove", "TOKEN"])
    assert result.exit_code == 0
    assert "removed" in result.output


@patch("envault.cli_schedule._get_passphrase", return_value="pw")
@patch("envault.cli_schedule.Vault")
@patch("envault.cli_schedule.last_rotated", return_value=None)
def test_due_cmd_shows_due_keys(mock_lr, MockVault, _mock_pp):
    fv = _make_fake_vault()
    MockVault.return_value = fv
    from envault import schedule as sched
    sched.set_schedule(fv, "OLD_KEY", 1)
    runner = CliRunner()
    result = runner.invoke(schedule_group, ["due"])
    assert result.exit_code == 0
    assert "OLD_KEY" in result.output
