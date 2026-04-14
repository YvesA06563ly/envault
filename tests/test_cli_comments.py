"""Tests for envault.cli_comments CLI commands."""

from __future__ import annotations

import json
import pytest
from click.testing import CliRunner

from envault.cli_comments import comment_group
from envault.comments import COMMENTS_KEY


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


def invoke(runner, fv, *args):
    return runner.invoke(comment_group, args, obj={"vault": fv})


def test_set_comment_success(runner, fv):
    result = invoke(runner, fv, "set", "DB_PASS", "main db password")
    assert result.exit_code == 0
    assert "Comment set for 'DB_PASS'" in result.output


def test_set_comment_stored(runner, fv):
    invoke(runner, fv, "set", "API_KEY", "external api")
    data = json.loads(fv.get(COMMENTS_KEY))
    assert data["API_KEY"] == "external api"


def test_show_existing_comment(runner, fv):
    invoke(runner, fv, "set", "TOKEN", "auth token")
    result = invoke(runner, fv, "show", "TOKEN")
    assert "TOKEN: auth token" in result.output


def test_show_missing_comment(runner, fv):
    result = invoke(runner, fv, "show", "GHOST")
    assert "No comment for 'GHOST'" in result.output


def test_remove_existing_comment(runner, fv):
    invoke(runner, fv, "set", "KEY", "note")
    result = invoke(runner, fv, "remove", "KEY")
    assert "Comment removed for 'KEY'" in result.output


def test_remove_missing_comment(runner, fv):
    result = invoke(runner, fv, "remove", "NOPE")
    assert "No comment found for 'NOPE'" in result.output


def test_list_no_comments(runner, fv):
    result = invoke(runner, fv, "list")
    assert "No comments found" in result.output


def test_list_multiple_comments(runner, fv):
    invoke(runner, fv, "set", "A", "alpha")
    invoke(runner, fv, "set", "B", "beta")
    result = invoke(runner, fv, "list")
    assert "A: alpha" in result.output
    assert "B: beta" in result.output
