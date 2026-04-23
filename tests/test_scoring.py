"""Tests for envault.scoring."""
from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest

from envault.scoring import ScoreBreakdown, score_secret, score_all


class _FakeVault:
    def __init__(self, secrets: dict[str, str] | None = None):
        self._data: dict[str, Any] = {"secrets": secrets or {}}

    def load(self) -> dict[str, Any]:
        return self._data

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def save(self, data: dict[str, Any]) -> None:
        self._data = data


# ---------------------------------------------------------------------------
# ScoreBreakdown
# ---------------------------------------------------------------------------

def test_breakdown_total():
    bd = ScoreBreakdown(rotation=30, expiry=25, integrity=25, policy=20)
    assert bd.total == 100


def test_breakdown_as_dict_contains_total():
    bd = ScoreBreakdown(rotation=15, expiry=10, integrity=20, policy=10)
    d = bd.as_dict()
    assert d["total"] == 55
    assert "rotation" in d and "expiry" in d


# ---------------------------------------------------------------------------
# score_secret — happy path (all checks pass)
# ---------------------------------------------------------------------------

def test_score_secret_perfect_score():
    vault = _FakeVault(secrets={"MY_KEY": "enc_value"})
    with (
        patch("envault.scoring.needs_rotation", return_value=False),
        patch("envault.scoring.last_rotated", return_value="2024-01-01T00:00:00"),
        patch("envault.scoring.get_expiry", return_value=None),
        patch("envault.scoring.is_expired", return_value=False),
        patch("envault.scoring.verify_checksum", return_value=True),
        patch("envault.scoring.run_policy_checks") as mock_policy,
    ):
        mock_policy.return_value.passed = True
        mock_policy.return_value.violations = []
        bd = score_secret(vault, "MY_KEY")
    assert bd.total == 100


def test_score_secret_rotation_overdue():
    vault = _FakeVault(secrets={"K": "v"})
    with (
        patch("envault.scoring.needs_rotation", return_value=True),
        patch("envault.scoring.last_rotated", return_value=None),
        patch("envault.scoring.get_expiry", return_value=None),
        patch("envault.scoring.is_expired", return_value=False),
        patch("envault.scoring.verify_checksum", return_value=True),
        patch("envault.scoring.run_policy_checks") as mock_policy,
    ):
        mock_policy.return_value.passed = True
        mock_policy.return_value.violations = []
        bd = score_secret(vault, "K")
    assert bd.rotation == 0
    assert bd.total == 70


def test_score_secret_expired_key():
    vault = _FakeVault(secrets={"K": "v"})
    with (
        patch("envault.scoring.needs_rotation", return_value=False),
        patch("envault.scoring.last_rotated", return_value="2024-01-01"),
        patch("envault.scoring.get_expiry", return_value="2023-01-01"),
        patch("envault.scoring.is_expired", return_value=True),
        patch("envault.scoring.verify_checksum", return_value=True),
        patch("envault.scoring.run_policy_checks") as mock_policy,
    ):
        mock_policy.return_value.passed = True
        mock_policy.return_value.violations = []
        bd = score_secret(vault, "K")
    assert bd.expiry == 0


def test_score_secret_checksum_fails():
    vault = _FakeVault(secrets={"K": "v"})
    with (
        patch("envault.scoring.needs_rotation", return_value=False),
        patch("envault.scoring.last_rotated", return_value="2024-01-01"),
        patch("envault.scoring.get_expiry", return_value=None),
        patch("envault.scoring.is_expired", return_value=False),
        patch("envault.scoring.verify_checksum", return_value=False),
        patch("envault.scoring.run_policy_checks") as mock_policy,
    ):
        mock_policy.return_value.passed = True
        mock_policy.return_value.violations = []
        bd = score_secret(vault, "K")
    assert bd.integrity == 0


def test_score_all_returns_entry_per_secret():
    vault = _FakeVault(secrets={"A": "1", "B": "2", "C": "3"})
    with (
        patch("envault.scoring.needs_rotation", return_value=False),
        patch("envault.scoring.last_rotated", return_value="2024-01-01"),
        patch("envault.scoring.get_expiry", return_value=None),
        patch("envault.scoring.is_expired", return_value=False),
        patch("envault.scoring.verify_checksum", return_value=True),
        patch("envault.scoring.run_policy_checks") as mock_policy,
    ):
        mock_policy.return_value.passed = True
        mock_policy.return_value.violations = []
        results = score_all(vault)
    assert set(results.keys()) == {"A", "B", "C"}
    for bd in results.values():
        assert isinstance(bd, ScoreBreakdown)


def test_score_all_empty_vault():
    vault = _FakeVault(secrets={})
    results = score_all(vault)
    assert results == {}
