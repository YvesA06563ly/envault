"""Workflow: named sequences of CLI-style operations on vault secrets."""
from __future__ import annotations
import json
from typing import Any

_WORKFLOWS_KEY = "__workflows__"


def _load_workflows(vault) -> dict:
    raw = vault.get(_WORKFLOWS_KEY)
    if not raw:
        return {}
    return json.loads(raw)


def _save_workflows(vault, data: dict) -> None:
    vault.set(_WORKFLOWS_KEY, json.dumps(data))
    vault.save()


def create_workflow(vault, name: str, steps: list[dict[str, Any]]) -> None:
    """Create or replace a named workflow with a list of step dicts."""
    if not name:
        raise ValueError("Workflow name must not be empty.")
    if not steps:
        raise ValueError("Workflow must have at least one step.")
    data = _load_workflows(vault)
    data[name] = {"steps": steps}
    _save_workflows(vault, data)


def delete_workflow(vault, name: str) -> bool:
    data = _load_workflows(vault)
    if name not in data:
        return False
    del data[name]
    _save_workflows(vault, data)
    return True


def get_workflow(vault, name: str) -> dict | None:
    return _load_workflows(vault).get(name)


def list_workflows(vault) -> list[str]:
    return sorted(_load_workflows(vault).keys())


def run_workflow(vault, name: str) -> list[dict[str, Any]]:
    """Execute a workflow; returns list of result records."""
    wf = get_workflow(vault, name)
    if wf is None:
        raise KeyError(f"Workflow '{name}' not found.")
    results = []
    for step in wf["steps"]:
        action = step.get("action")
        key = step.get("key", "")
        value = step.get("value", "")
        if action == "set":
            vault.set(key, value)
            results.append({"action": "set", "key": key, "status": "ok"})
        elif action == "delete":
            vault.set(key, None)
            results.append({"action": "delete", "key": key, "status": "ok"})
        else:
            results.append({"action": action, "key": key, "status": "unknown_action"})
    vault.save()
    return results
