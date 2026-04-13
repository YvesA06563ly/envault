"""Policy enforcement for secrets: define and evaluate rules on secret keys and values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import re

_POLICY_KEY = "__envault_policies__"


@dataclass
class PolicyRule:
    name: str
    key_pattern: str          # regex applied to secret key
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    value_pattern: Optional[str] = None  # regex applied to value
    forbidden_pattern: Optional[str] = None


@dataclass
class PolicyViolation:
    rule_name: str
    key: str
    reason: str


@dataclass
class PolicyReport:
    violations: List[PolicyViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def _load_policies(vault) -> List[dict]:
    raw = vault.get(_POLICY_KEY)
    if not raw:
        return []
    import json
    return json.loads(raw)


def _save_policies(vault, policies: List[dict]) -> None:
    import json
    vault.set(_POLICY_KEY, json.dumps(policies))
    vault.save()


def add_policy(vault, rule: PolicyRule) -> None:
    policies = _load_policies(vault)
    policies = [p for p in policies if p["name"] != rule.name]
    policies.append({
        "name": rule.name,
        "key_pattern": rule.key_pattern,
        "min_length": rule.min_length,
        "max_length": rule.max_length,
        "value_pattern": rule.value_pattern,
        "forbidden_pattern": rule.forbidden_pattern,
    })
    _save_policies(vault, policies)


def remove_policy(vault, name: str) -> bool:
    policies = _load_policies(vault)
    new_policies = [p for p in policies if p["name"] != name]
    if len(new_policies) == len(policies):
        return False
    _save_policies(vault, new_policies)
    return True


def list_policies(vault) -> List[PolicyRule]:
    return [
        PolicyRule(
            name=p["name"],
            key_pattern=p["key_pattern"],
            min_length=p.get("min_length"),
            max_length=p.get("max_length"),
            value_pattern=p.get("value_pattern"),
            forbidden_pattern=p.get("forbidden_pattern"),
        )
        for p in _load_policies(vault)
    ]


def evaluate_policies(vault, secrets: dict) -> PolicyReport:
    """Check all secrets against all stored policies."""
    report = PolicyReport()
    rules = list_policies(vault)
    for key, value in secrets.items():
        if key.startswith("__envault_"):
            continue
        for rule in rules:
            if not re.search(rule.key_pattern, key):
                continue
            if rule.min_length is not None and len(value) < rule.min_length:
                report.violations.append(PolicyViolation(
                    rule.name, key,
                    f"value length {len(value)} < min {rule.min_length}"
                ))
            if rule.max_length is not None and len(value) > rule.max_length:
                report.violations.append(PolicyViolation(
                    rule.name, key,
                    f"value length {len(value)} > max {rule.max_length}"
                ))
            if rule.value_pattern and not re.search(rule.value_pattern, value):
                report.violations.append(PolicyViolation(
                    rule.name, key,
                    f"value does not match required pattern '{rule.value_pattern}'"
                ))
            if rule.forbidden_pattern and re.search(rule.forbidden_pattern, value):
                report.violations.append(PolicyViolation(
                    rule.name, key,
                    f"value matches forbidden pattern '{rule.forbidden_pattern}'"
                ))
    return report
