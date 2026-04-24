"""Compliance checks: verify secrets meet regulatory/policy standards."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

_COMPLIANCE_KEY = "__compliance__"

_KNOWN_FRAMEWORKS = {"pci-dss", "hipaa", "soc2", "gdpr", "iso27001"}


def _load_compliance(vault) -> dict:
    raw = vault.get(_COMPLIANCE_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_compliance(vault, data: dict) -> None:
    vault.set(_COMPLIANCE_KEY, data)
    vault.save()


def assign_framework(vault, key: str, framework: str) -> None:
    """Assign a compliance framework tag to a secret."""
    framework = framework.lower()
    if framework not in _KNOWN_FRAMEWORKS:
        raise ValueError(f"Unknown framework '{framework}'. Known: {sorted(_KNOWN_FRAMEWORKS)}")
    data = _load_compliance(vault)
    entry = data.get(key, {})
    frameworks = set(entry.get("frameworks", []))
    frameworks.add(framework)
    entry["frameworks"] = sorted(frameworks)
    data[key] = entry
    _save_compliance(vault, data)


def remove_framework(vault, key: str, framework: str) -> None:
    """Remove a compliance framework tag from a secret."""
    data = _load_compliance(vault)
    entry = data.get(key, {})
    frameworks = set(entry.get("frameworks", []))
    frameworks.discard(framework.lower())
    entry["frameworks"] = sorted(frameworks)
    data[key] = entry
    _save_compliance(vault, data)


def get_frameworks(vault, key: str) -> List[str]:
    """Return frameworks assigned to a secret."""
    data = _load_compliance(vault)
    return data.get(key, {}).get("frameworks", [])


def list_by_framework(vault, framework: str) -> List[str]:
    """Return all secret keys tagged with the given framework."""
    framework = framework.lower()
    data = _load_compliance(vault)
    return sorted(k for k, v in data.items() if framework in v.get("frameworks", []))


@dataclass
class ComplianceReport:
    framework: str
    covered: List[str] = field(default_factory=list)
    uncovered: List[str] = field(default_factory=list)

    @property
    def coverage_pct(self) -> float:
        total = len(self.covered) + len(self.uncovered)
        if total == 0:
            return 100.0
        return round(100.0 * len(self.covered) / total, 1)


def compliance_report(vault, framework: str, all_keys: List[str]) -> ComplianceReport:
    """Produce a coverage report for a framework across given keys."""
    tagged = set(list_by_framework(vault, framework))
    covered = [k for k in all_keys if k in tagged]
    uncovered = [k for k in all_keys if k not in tagged]
    return ComplianceReport(framework=framework.lower(), covered=covered, uncovered=uncovered)
