"""Tests for envault.lint."""
import pytest
from envault.lint import lint_secrets, LintReport, LintIssue


class _FakeVault:
    def __init__(self, secrets: dict):
        self._secrets = secrets

    def load(self) -> dict:
        return dict(self._secrets)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _severities(report: LintReport, key: str):
    return [i.severity for i in report.by_key(key)]


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_clean_vault_produces_no_issues():
    vault = _FakeVault({"DATABASE_URL": "postgres://user:s3cr3tP@ss!@localhost/db"})
    report = lint_secrets(vault)
    assert report.issues == []
    assert not report.has_errors
    assert not report.has_warnings


def test_empty_value_is_error():
    vault = _FakeVault({"API_KEY": ""})
    report = lint_secrets(vault)
    assert report.has_errors
    assert any(i.severity == "error" for i in report.by_key("API_KEY"))


def test_whitespace_only_value_is_error():
    vault = _FakeVault({"TOKEN": "   "})
    report = lint_secrets(vault)
    assert report.has_errors


def test_weak_value_is_error():
    vault = _FakeVault({"DB_PASS": "password"})
    report = lint_secrets(vault)
    assert "error" in _severities(report, "DB_PASS")


def test_short_value_is_warning():
    vault = _FakeVault({"SHORT_KEY": "abc"})
    report = lint_secrets(vault)
    assert "warning" in _severities(report, "SHORT_KEY")


def test_bad_naming_convention_is_warning():
    vault = _FakeVault({"mySecret": "some_long_value_here"})
    report = lint_secrets(vault)
    assert "warning" in _severities(report, "mySecret")


def test_good_naming_convention_no_warning():
    vault = _FakeVault({"MY_SECRET": "some_long_value_here"})
    report = lint_secrets(vault)
    naming_warnings = [
        i for i in report.by_key("MY_SECRET")
        if "convention" in i.message.lower()
    ]
    assert naming_warnings == []


def test_duplicate_values_produce_warning():
    shared = "shared_secret_value_123"
    vault = _FakeVault({"KEY_A": shared, "KEY_B": shared})
    report = lint_secrets(vault)
    dup_issues = [i for i in report.issues if "same value" in i.message]
    assert len(dup_issues) == 1
    assert dup_issues[0].severity == "warning"


def test_has_errors_property():
    vault = _FakeVault({"BAD": ""})
    report = lint_secrets(vault)
    assert report.has_errors is True


def test_has_warnings_property():
    vault = _FakeVault({"bad_name": "long_enough_value_here"})
    report = lint_secrets(vault)
    assert report.has_warnings is True


def test_multiple_issues_same_key():
    # short AND bad naming
    vault = _FakeVault({"badName": "hi"})
    report = lint_secrets(vault)
    issues_for_key = report.by_key("badName")
    assert len(issues_for_key) >= 2
