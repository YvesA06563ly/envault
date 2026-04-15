"""CLI tests for quota commands."""

import json
import pytest
from click.testing import CliRunner
from envault.cli_quota import quota_group

_QUOTA_KEY = "__quota__"


class FV:
    def __init__(self):
        self._store: dict = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        pass


def _make_fake_vault():
    return FV()


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def fv():
    return _make_fake_vault()


def _ctx(fv):
    return {"vault": fv}


def test_set_quota_cmd(runner, fv):
    result = runner.invoke(quota_group, ["set", "prod", "100"], obj=_ctx(fv))
    assert result.exit_code == 0
    assert "100" in result.output


def test_show_quota_cmd(runner, fv):
    runner.invoke(quota_group, ["set", "prod", "100"], obj=_ctx(fv))
    result = runner.invoke(quota_group, ["show", "prod"], obj=_ctx(fv))
    assert "100" in result.output


def test_show_quota_missing(runner, fv):
    result = runner.invoke(quota_group, ["show", "ghost"], obj=_ctx(fv))
    assert "No quota" in result.output


def test_remove_quota_cmd(runner, fv):
    runner.invoke(quota_group, ["set", "dev", "5"], obj=_ctx(fv))
    result = runner.invoke(quota_group, ["remove", "dev"], obj=_ctx(fv))
    assert "removed" in result.output


def test_remove_quota_missing(runner, fv):
    result = runner.invoke(quota_group, ["remove", "ghost"], obj=_ctx(fv))
    assert "No quota" in result.output


def test_list_quotas_empty(runner, fv):
    result = runner.invoke(quota_group, ["list"], obj=_ctx(fv))
    assert "No quotas" in result.output


def test_list_quotas_populated(runner, fv):
    runner.invoke(quota_group, ["set", "a", "10"], obj=_ctx(fv))
    runner.invoke(quota_group, ["set", "b", "20"], obj=_ctx(fv))
    result = runner.invoke(quota_group, ["list"], obj=_ctx(fv))
    assert "a: 10" in result.output
    assert "b: 20" in result.output


def test_check_quota_ok(runner, fv):
    runner.invoke(quota_group, ["set", "ns", "10"], obj=_ctx(fv))
    result = runner.invoke(quota_group, ["check", "ns", "5"], obj=_ctx(fv))
    assert result.exit_code == 0
    assert "OK" in result.output


def test_check_quota_exceeded(runner, fv):
    runner.invoke(quota_group, ["set", "ns", "3"], obj=_ctx(fv))
    result = runner.invoke(quota_group, ["check", "ns", "5"], obj=_ctx(fv))
    assert "EXCEEDED" in result.output
