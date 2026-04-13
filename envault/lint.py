"""Lint secrets for common issues: weak values, naming conventions, duplicates."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import re

_WEAK_VALUES = {"password", "secret", "changeme", "admin", "12345", "test", "example", "placeholder"}
_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')
_MIN_SECRET_LEN = 8


@dataclass
class LintIssue:
    key: str
    severity: str  # "error" | "warning" | "info"
    message: str


@dataclass
class LintReport:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def by_key(self, key: str) -> List[LintIssue]:
        return [i for i in self.issues if i.key == key]


def lint_secrets(vault) -> LintReport:
    """Run all lint checks against secrets stored in *vault*.

    The vault object must expose a ``load()`` method that returns a dict
    mapping secret keys to their decrypted string values.
    """
    report = LintReport()
    secrets: dict = vault.load()

    seen_values: dict[str, str] = {}

    for key, value in secrets.items():
        # Naming convention check
        if not _KEY_PATTERN.match(key):
            report.issues.append(LintIssue(
                key=key,
                severity="warning",
                message=f"Key '{key}' does not follow UPPER_SNAKE_CASE convention.",
            ))

        # Empty value check
        if not value or not value.strip():
            report.issues.append(LintIssue(
                key=key,
                severity="error",
                message=f"Secret '{key}' has an empty value.",
            ))
            continue

        # Minimum length check
        if len(value) < _MIN_SECRET_LEN:
            report.issues.append(LintIssue(
                key=key,
                severity="warning",
                message=f"Secret '{key}' is shorter than {_MIN_SECRET_LEN} characters.",
            ))

        # Weak value check
        if value.strip().lower() in _WEAK_VALUES:
            report.issues.append(LintIssue(
                key=key,
                severity="error",
                message=f"Secret '{key}' uses a known-weak placeholder value.",
            ))

        # Duplicate value check
        if value in seen_values:
            report.issues.append(LintIssue(
                key=key,
                severity="warning",
                message=(
                    f"Secret '{key}' has the same value as '{seen_values[value]}'. "
                    "Consider using unique secrets."
                ),
            ))
        else:
            seen_values[value] = key

    return report
