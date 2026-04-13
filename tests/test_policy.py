"""Tests for envault.policy module."""

import json
import pytest
from envault.policy import (
    PolicyRule, add_policy, remove_policy, list_policies, evaluate_policies,
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
def vault():
    return _FakeVault()


def test_add_and_list_policy(vault):
    rule = PolicyRule(name="min8", key_pattern=".*", min_length=8)
    add_policy(vault, rule)
    rules = list_policies(vault)
    assert len(rules) == 1
    assert rules[0].name == "min8"
    assert rules[0].min_length == 8


def test_add_policy_overwrites_same_name(vault):
    add_policy(vault, PolicyRule(name="len", key_pattern=".*", min_length=4))
    add_policy(vault, PolicyRule(name="len", key_pattern=".*", min_length=10))
    rules = list_policies(vault)
    assert len(rules) == 1
    assert rules[0].min_length == 10


def test_remove_existing_policy(vault):
    add_policy(vault, PolicyRule(name="p1", key_pattern=".*"))
    removed = remove_policy(vault, "p1")
    assert removed is True
    assert list_policies(vault) == []


def test_remove_nonexistent_policy_returns_false(vault):
    result = remove_policy(vault, "ghost")
    assert result is False


def test_evaluate_no_policies_passes(vault):
    report = evaluate_policies(vault, {"DB_PASS": "short"})
    assert report.passed


def test_evaluate_min_length_violation(vault):
    add_policy(vault, PolicyRule(name="min8", key_pattern=".*PASS.*", min_length=8))
    report = evaluate_policies(vault, {"DB_PASS": "abc"})
    assert not report.passed
    assert report.violations[0].key == "DB_PASS"
    assert "min" in report.violations[0].reason


def test_evaluate_max_length_ok(vault):
    add_policy(vault, PolicyRule(name="max20", key_pattern=".*", max_length=20))
    report = evaluate_policies(vault, {"TOKEN": "short"})
    assert report.passed


def test_evaluate_max_length_violation(vault):
    add_policy(vault, PolicyRule(name="max5", key_pattern=".*", max_length=5))
    report = evaluate_policies(vault, {"KEY": "toolongvalue"})
    assert not report.passed


def test_evaluate_value_pattern_violation(vault):
    add_policy(vault, PolicyRule(
        name="uppercase", key_pattern=".*",
        value_pattern="^[A-Z0-9_]+$"
    ))
    report = evaluate_policies(vault, {"MY_KEY": "lowercase_bad"})
    assert not report.passed
    assert "required pattern" in report.violations[0].reason


def test_evaluate_forbidden_pattern_violation(vault):
    add_policy(vault, PolicyRule(
        name="no_spaces", key_pattern=".*",
        forbidden_pattern=r"\s"
    ))
    report = evaluate_policies(vault, {"SECRET": "has space"})
    assert not report.passed
    assert "forbidden" in report.violations[0].reason


def test_evaluate_skips_internal_keys(vault):
    add_policy(vault, PolicyRule(name="min50", key_pattern=".*", min_length=50))
    report = evaluate_policies(vault, {"__envault_meta__": "x"})
    assert report.passed


def test_evaluate_key_pattern_filters_keys(vault):
    add_policy(vault, PolicyRule(name="db_min", key_pattern="^DB_", min_length=16))
    report = evaluate_policies(vault, {"API_KEY": "short", "DB_PASS": "short"})
    violations_keys = {v.key for v in report.violations}
    assert "DB_PASS" in violations_keys
    assert "API_KEY" not in violations_keys
