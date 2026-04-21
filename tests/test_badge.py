"""Tests for envault.badge."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from envault.badge import Badge, get_badges, summary_status


# ---------------------------------------------------------------------------
# Minimal fake vault
# ---------------------------------------------------------------------------

class _FakeVault:
    def __init__(self, data: dict | None = None):
        self._data: dict = data or {}

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value

    def save(self):
        pass


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _future(days: int = 30) -> str:
    return _iso(datetime.now(timezone.utc) + timedelta(days=days))


def _past(days: int = 10) -> str:
    return _iso(datetime.now(timezone.utc) - timedelta(days=days))


# ---------------------------------------------------------------------------
# Badge dataclass
# ---------------------------------------------------------------------------

def test_badge_as_dict():
    b = Badge("DB_PASS", "ok", "expiry", "expires soon")
    d = b.as_dict()
    assert d["key"] == "DB_PASS"
    assert d["status"] == "ok"
    assert d["label"] == "expiry"
    assert d["detail"] == "expires soon"


# ---------------------------------------------------------------------------
# get_badges returns three badges per key
# ---------------------------------------------------------------------------

def test_get_badges_returns_three_entries():
    vault = _FakeVault()
    badges = get_badges(vault, "MY_KEY")
    assert len(badges) == 3
    labels = {b.label for b in badges}
    assert labels == {"expiry", "rotation", "integrity"}


def test_get_badges_unknown_when_no_metadata():
    vault = _FakeVault()
    badges = get_badges(vault, "EMPTY_KEY")
    for b in badges:
        assert b.status == "unknown"


# ---------------------------------------------------------------------------
# summary_status aggregation
# ---------------------------------------------------------------------------

def test_summary_all_ok():
    badges = [Badge("k", "ok", l, "") for l in ("expiry", "rotation", "integrity")]
    assert summary_status(badges) == "ok"


def test_summary_error_dominates():
    badges = [
        Badge("k", "ok", "expiry", ""),
        Badge("k", "warning", "rotation", ""),
        Badge("k", "error", "integrity", ""),
    ]
    assert summary_status(badges) == "error"


def test_summary_warning_over_unknown():
    badges = [
        Badge("k", "unknown", "expiry", ""),
        Badge("k", "warning", "rotation", ""),
        Badge("k", "ok", "integrity", ""),
    ]
    assert summary_status(badges) == "warning"


def test_summary_unknown_when_no_error_or_warning():
    badges = [
        Badge("k", "ok", "expiry", ""),
        Badge("k", "unknown", "rotation", ""),
        Badge("k", "ok", "integrity", ""),
    ]
    assert summary_status(badges) == "unknown"
