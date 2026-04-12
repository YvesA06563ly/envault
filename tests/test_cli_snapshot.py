"""CLI-level tests for snapshot commands."""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.cli_snapshot import snapshot_group
from envault import snapshot as snap


def _make_fake_vault(store=None):
    class FV:
        _store = store or {"KEY": "val"}

        def get(self, k):
            return self._store.get(k)

        def set(self, k, v):
            self._store[k] = v

        def save(self):
            pass

    return FV()


@pytest.fixture
def runner():
    return CliRunner()


def test_create_command(runner):
    fv = _make_fake_vault()
    with patch("envault.cli_snapshot._get_passphrase", return_value="pw"), \
         patch("envault.cli_snapshot.Vault", return_value=fv):
        result = runner.invoke(snapshot_group, ["create", "snap1", "KEY"])
    assert result.exit_code == 0
    assert "snap1" in result.output


def test_list_command_no_snapshots(runner):
    fv = _make_fake_vault({})
    with patch("envault.cli_snapshot._get_passphrase", return_value="pw"), \
         patch("envault.cli_snapshot.Vault", return_value=fv):
        result = runner.invoke(snapshot_group, ["list"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_restore_command(runner):
    fv = _make_fake_vault({"KEY": "original"})
    snap.create_snapshot(fv, "s1", ["KEY"])
    fv.set("KEY", "modified")
    with patch("envault.cli_snapshot._get_passphrase", return_value="pw"), \
         patch("envault.cli_snapshot.Vault", return_value=fv):
        result = runner.invoke(snapshot_group, ["restore", "s1"])
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_delete_command(runner):
    fv = _make_fake_vault({"KEY": "v"})
    snap.create_snapshot(fv, "del_me", ["KEY"])
    with patch("envault.cli_snapshot._get_passphrase", return_value="pw"), \
         patch("envault.cli_snapshot.Vault", return_value=fv):
        result = runner.invoke(snapshot_group, ["delete", "del_me"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_restore_missing_shows_error(runner):
    fv = _make_fake_vault({})
    with patch("envault.cli_snapshot._get_passphrase", return_value="pw"), \
         patch("envault.cli_snapshot.Vault", return_value=fv):
        result = runner.invoke(snapshot_group, ["restore", "ghost"])
    assert result.exit_code != 0
    assert "ghost" in result.output
