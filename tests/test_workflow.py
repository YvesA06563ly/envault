"""Tests for envault.workflow."""
import json
import pytest
from envault.workflow import (
    create_workflow, delete_workflow, get_workflow,
    list_workflows, run_workflow, _WORKFLOWS_KEY,
)


class _FakeVault:
    def __init__(self):
        self._store = {}
        self.saved = False

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        self.saved = True


@pytest.fixture
def vault():
    return _FakeVault()


STEPS = [{"action": "set", "key": "FOO", "value": "bar"}]


def test_create_and_get(vault):
    create_workflow(vault, "deploy", STEPS)
    wf = get_workflow(vault, "deploy")
    assert wf is not None
    assert wf["steps"] == STEPS


def test_list_workflows(vault):
    create_workflow(vault, "b", STEPS)
    create_workflow(vault, "a", STEPS)
    assert list_workflows(vault) == ["a", "b"]


def test_delete_existing(vault):
    create_workflow(vault, "wf", STEPS)
    assert delete_workflow(vault, "wf") is True
    assert get_workflow(vault, "wf") is None


def test_delete_missing(vault):
    assert delete_workflow(vault, "nope") is False


def test_create_empty_name_raises(vault):
    with pytest.raises(ValueError):
        create_workflow(vault, "", STEPS)


def test_create_empty_steps_raises(vault):
    with pytest.raises(ValueError):
        create_workflow(vault, "wf", [])


def test_run_workflow_set(vault):
    steps = [{"action": "set", "key": "X", "value": "42"}]
    create_workflow(vault, "setwf", steps)
    results = run_workflow(vault, "setwf")
    assert results[0]["status"] == "ok"
    assert vault.get("X") == "42"


def test_run_workflow_delete(vault):
    vault.set("Y", "old")
    steps = [{"action": "delete", "key": "Y"}]
    create_workflow(vault, "delwf", steps)
    results = run_workflow(vault, "delwf")
    assert results[0]["status"] == "ok"
    assert vault.get("Y") is None


def test_run_unknown_action(vault):
    steps = [{"action": "fly", "key": "Z"}]
    create_workflow(vault, "weird", steps)
    results = run_workflow(vault, "weird")
    assert results[0]["status"] == "unknown_action"


def test_run_missing_workflow_raises(vault):
    with pytest.raises(KeyError):
        run_workflow(vault, "ghost")


def test_vault_saved_after_create(vault):
    create_workflow(vault, "wf", STEPS)
    assert vault.saved
