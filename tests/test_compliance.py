"""Tests for envault.compliance."""

from __future__ import annotations

import pytest

from envault.compliance import (
    assign_framework,
    remove_framework,
    get_frameworks,
    list_by_framework,
    compliance_report,
    ComplianceReport,
)


class _FakeVault:
    def __init__(self):
        self._store: dict = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        pass

    def load(self):
        return {k: v for k, v in self._store.items()}


@pytest.fixture
def vault():
    return _FakeVault()


def test_assign_framework(vault):
    assign_framework(vault, "DB_PASS", "pci-dss")
    assert "pci-dss" in get_frameworks(vault, "DB_PASS")


def test_assign_multiple_frameworks(vault):
    assign_framework(vault, "API_KEY", "soc2")
    assign_framework(vault, "API_KEY", "gdpr")
    fw = get_frameworks(vault, "API_KEY")
    assert "soc2" in fw
    assert "gdpr" in fw


def test_assign_unknown_framework_raises(vault):
    with pytest.raises(ValueError, match="Unknown framework"):
        assign_framework(vault, "KEY", "unknown-fw")


def test_remove_framework(vault):
    assign_framework(vault, "SECRET", "hipaa")
    remove_framework(vault, "SECRET", "hipaa")
    assert "hipaa" not in get_frameworks(vault, "SECRET")


def test_remove_nonexistent_framework_is_noop(vault):
    remove_framework(vault, "SECRET", "gdpr")  # should not raise
    assert get_frameworks(vault, "SECRET") == []


def test_get_frameworks_empty(vault):
    assert get_frameworks(vault, "MISSING") == []


def test_list_by_framework(vault):
    assign_framework(vault, "KEY_A", "iso27001")
    assign_framework(vault, "KEY_B", "iso27001")
    assign_framework(vault, "KEY_C", "gdpr")
    result = list_by_framework(vault, "iso27001")
    assert "KEY_A" in result
    assert "KEY_B" in result
    assert "KEY_C" not in result


def test_list_by_framework_case_insensitive(vault):
    assign_framework(vault, "KEY_D", "soc2")
    assert "KEY_D" in list_by_framework(vault, "SOC2")


def test_compliance_report_full_coverage(vault):
    assign_framework(vault, "A", "gdpr")
    assign_framework(vault, "B", "gdpr")
    report = compliance_report(vault, "gdpr", ["A", "B"])
    assert report.coverage_pct == 100.0
    assert report.uncovered == []


def test_compliance_report_partial_coverage(vault):
    assign_framework(vault, "A", "hipaa")
    report = compliance_report(vault, "hipaa", ["A", "B", "C"])
    assert report.covered == ["A"]
    assert set(report.uncovered) == {"B", "C"}
    assert report.coverage_pct == pytest.approx(33.3, 0.1)


def test_compliance_report_empty_keys(vault):
    report = compliance_report(vault, "pci-dss", [])
    assert report.coverage_pct == 100.0
