"""Tests for envault.hooks."""
from __future__ import annotations

import json
import pytest

from envault.hooks import (
    _HOOKS_KEY,
    set_hook,
    remove_hook,
    list_hooks,
    run_hook,
)


class _FakeVault:
    def __init__(self):
        self._store: dict = {}
        self.saved = False

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        self.saved = True


@pytest.fixture
def fv():
    return _FakeVault()


def test_set_hook_stores_command(fv):
    set_hook(fv, "DB_PASS", "pre", "echo before")
    raw = json.loads(fv.get(_HOOKS_KEY))
    assert raw["DB_PASS"]["pre"] == "echo before"


def test_set_hook_invalid_stage_raises(fv):
    with pytest.raises(ValueError, match="stage must be"):
        set_hook(fv, "DB_PASS", "during", "echo hi")


def test_set_hook_saves_vault(fv):
    set_hook(fv, "API_KEY", "post", "echo after")
    assert fv.saved


def test_remove_hook_returns_true_when_found(fv):
    set_hook(fv, "TOKEN", "pre", "echo pre")
    fv.saved = False
    result = remove_hook(fv, "TOKEN", "pre")
    assert result is True
    assert fv.saved


def test_remove_hook_returns_false_when_missing(fv):
    result = remove_hook(fv, "GHOST", "post")
    assert result is False
    assert not fv.saved


def test_remove_hook_cleans_empty_key_entry(fv):
    set_hook(fv, "X", "pre", "ls")
    remove_hook(fv, "X", "pre")
    hooks = list_hooks(fv)
    assert "X" not in hooks


def test_list_hooks_empty(fv):
    assert list_hooks(fv) == {}


def test_list_hooks_returns_all(fv):
    set_hook(fv, "A", "pre", "cmd1")
    set_hook(fv, "A", "post", "cmd2")
    set_hook(fv, "B", "post", "cmd3")
    hooks = list_hooks(fv)
    assert hooks["A"]["pre"] == "cmd1"
    assert hooks["A"]["post"] == "cmd2"
    assert hooks["B"]["post"] == "cmd3"


def test_run_hook_returns_none_when_no_hook(fv):
    assert run_hook(fv, "MISSING", "pre") is None


def test_run_hook_executes_command(fv):
    set_hook(fv, "K", "post", "echo hello")
    result = run_hook(fv, "K", "post")
    assert result is not None
    assert result.returncode == 0
    assert "hello" in result.stdout


def test_run_hook_raises_on_failure(fv):
    import subprocess
    set_hook(fv, "K", "pre", "exit 1")
    with pytest.raises(subprocess.CalledProcessError):
        run_hook(fv, "K", "pre")
