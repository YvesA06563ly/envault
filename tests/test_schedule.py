"""Tests for envault.schedule."""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta

import pytest
from envault import schedule as sched


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
def vault():
    return _FakeVault()


def test_set_schedule_stores_entry(vault):
    sched.set_schedule(vault, "DB_PASS", 30)
    cfg = sched.get_schedule(vault, "DB_PASS")
    assert cfg is not None
    assert cfg["interval_days"] == 30
    assert cfg["notify"] is False


def test_set_schedule_with_notify(vault):
    sched.set_schedule(vault, "API_KEY", 7, notify=True)
    cfg = sched.get_schedule(vault, "API_KEY")
    assert cfg["notify"] is True


def test_set_schedule_invalid_interval(vault):
    with pytest.raises(ValueError):
        sched.set_schedule(vault, "KEY", 0)


def test_remove_existing_schedule(vault):
    sched.set_schedule(vault, "TOKEN", 14)
    removed = sched.remove_schedule(vault, "TOKEN")
    assert removed is True
    assert sched.get_schedule(vault, "TOKEN") is None


def test_remove_nonexistent_schedule(vault):
    removed = sched.remove_schedule(vault, "GHOST")
    assert removed is False


def test_list_schedules_empty(vault):
    assert sched.list_schedules(vault) == {}


def test_list_schedules_multiple(vault):
    sched.set_schedule(vault, "A", 1)
    sched.set_schedule(vault, "B", 90)
    result = sched.list_schedules(vault)
    assert set(result.keys()) == {"A", "B"}


def test_due_keys_no_rotation_history(vault):
    sched.set_schedule(vault, "NEW_KEY", 30)
    due = sched.due_keys(vault, lambda k: None)
    assert "NEW_KEY" in due


def test_due_keys_recently_rotated(vault):
    sched.set_schedule(vault, "FRESH", 30)
    recent = datetime.now(timezone.utc) - timedelta(days=1)
    due = sched.due_keys(vault, lambda k: recent)
    assert "FRESH" not in due


def test_due_keys_overdue(vault):
    sched.set_schedule(vault, "OLD", 7)
    old_ts = datetime.now(timezone.utc) - timedelta(days=10)
    due = sched.due_keys(vault, lambda k: old_ts)
    assert "OLD" in due


def test_save_called_on_set(vault):
    sched.set_schedule(vault, "X", 5)
    assert vault.saved is True
