"""Pre/post rotation hooks for envault.

Allows registering shell commands to run before or after a secret is rotated.
Hooks are stored per-key in the vault under a reserved metadata key.
"""
from __future__ import annotations

import subprocess
from typing import Any

_HOOKS_KEY = "__envault_hooks__"


def _load_hooks(vault: Any) -> dict:
    raw = vault.get(_HOOKS_KEY)
    if raw is None:
        return {}
    import json
    return json.loads(raw)


def _save_hooks(vault: Any, hooks: dict) -> None:
    import json
    vault.set(_HOOKS_KEY, json.dumps(hooks))
    vault.save()


def set_hook(vault: Any, key: str, stage: str, command: str) -> None:
    """Register *command* to run at *stage* ('pre' or 'post') for *key*."""
    if stage not in ("pre", "post"):
        raise ValueError(f"stage must be 'pre' or 'post', got {stage!r}")
    hooks = _load_hooks(vault)
    hooks.setdefault(key, {})[stage] = command
    _save_hooks(vault, hooks)


def remove_hook(vault: Any, key: str, stage: str) -> bool:
    """Remove the hook for *stage* on *key*. Returns True if removed."""
    hooks = _load_hooks(vault)
    removed = hooks.get(key, {}).pop(stage, None) is not None
    if removed:
        if not hooks[key]:
            del hooks[key]
        _save_hooks(vault, hooks)
    return removed


def list_hooks(vault: Any) -> dict:
    """Return all registered hooks keyed by secret name."""
    return _load_hooks(vault)


def run_hook(vault: Any, key: str, stage: str) -> subprocess.CompletedProcess | None:
    """Execute the hook command for *stage* on *key*, if one exists.

    Returns the CompletedProcess result or None if no hook is registered.
    Raises subprocess.CalledProcessError on non-zero exit.
    """
    hooks = _load_hooks(vault)
    command = hooks.get(key, {}).get(stage)
    if command is None:
        return None
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    return result
