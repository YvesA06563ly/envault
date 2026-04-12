"""Tests for envault.audit."""

from __future__ import annotations

import json
from typing import Any, Dict

import pytest

from envault.audit import (
    AUDIT_LOG_KEY,
    _MAX_ENTRIES,
    get_log,
    record_event,
)


class _FakeVault:
    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}
        self.save_called = 0

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def save(self) -> None:
        self.save_called += 1


@pytest.fixture()
def vault() -> _FakeVault:
    return _FakeVault()


def test_record_event_creates_entry(vault):
    record_event(vault, "set", "DB_PASSWORD")
    entries = get_log(vault)
    assert len(entries) == 1
    assert entries[0]["action"] == "set"
    assert entries[0]["key"] == "DB_PASSWORD"
    assert "timestamp" in entries[0]


def test_record_event_saves_vault(vault):
    record_event(vault, "get", "API_KEY")
    assert vault.save_called == 1


def test_record_event_with_actor_and_details(vault):
    record_event(vault, "rotate", "SECRET", actor="ci-bot", details="scheduled")
    entry = get_log(vault)[0]
    assert entry["actor"] == "ci-bot"
    assert entry["details"] == "scheduled"


def test_get_log_filter_by_key(vault):
    record_event(vault, "set", "KEY_A")
    record_event(vault, "set", "KEY_B")
    results = get_log(vault, key="KEY_A")
    assert all(e["key"] == "KEY_A" for e in results)
    assert len(results) == 1


def test_get_log_filter_by_action(vault):
    record_event(vault, "set", "X")
    record_event(vault, "get", "X")
    results = get_log(vault, action="get")
    assert all(e["action"] == "get" for e in results)


def test_get_log_limit(vault):
    for i in range(10):
        record_event(vault, "set", f"KEY_{i}")
    results = get_log(vault, limit=3)
    assert len(results) == 3


def test_log_trimmed_to_max_entries(vault):
    for i in range(_MAX_ENTRIES + 20):
        record_event(vault, "set", f"K{i}")
    raw = json.loads(vault.get(AUDIT_LOG_KEY))
    assert len(raw) == _MAX_ENTRIES


def test_get_log_empty_vault(vault):
    assert get_log(vault) == []


def test_get_log_corrupted_data(vault):
    vault.set(AUDIT_LOG_KEY, "not-valid-json")
    assert get_log(vault) == []
