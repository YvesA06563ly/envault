"""Secret health scoring — aggregates multiple signals into a single 0-100 score."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from envault.expiry import get_expiry, is_expired
from envault.rotation import last_rotated, needs_rotation
from envault.checksum import verify_checksum
from envault.policy import run_policy_checks

_WEIGHT_ROTATION = 30
_WEIGHT_EXPIRY = 25
_WEIGHT_INTEGRITY = 25
_WEIGHT_POLICY = 20


@dataclass
class ScoreBreakdown:
    rotation: int = 0
    expiry: int = 0
    integrity: int = 0
    policy: int = 0

    @property
    def total(self) -> int:
        return self.rotation + self.expiry + self.integrity + self.policy

    def as_dict(self) -> dict[str, Any]:
        return {
            "rotation": self.rotation,
            "expiry": self.expiry,
            "integrity": self.integrity,
            "policy": self.policy,
            "total": self.total,
        }


def score_secret(vault: Any, key: str) -> ScoreBreakdown:
    """Return a ScoreBreakdown for *key* stored in *vault*."""
    bd = ScoreBreakdown()

    # --- rotation score ---
    if not needs_rotation(vault, key):
        bd.rotation = _WEIGHT_ROTATION
    elif last_rotated(vault, key) is not None:
        bd.rotation = _WEIGHT_ROTATION // 2

    # --- expiry score ---
    expiry = get_expiry(vault, key)
    if expiry is None:
        bd.expiry = _WEIGHT_EXPIRY  # no expiry set → not a concern
    elif not is_expired(vault, key):
        bd.expiry = _WEIGHT_EXPIRY
    # else: expired → 0

    # --- integrity score ---
    try:
        ok = verify_checksum(vault, key)
        bd.integrity = _WEIGHT_INTEGRITY if ok else 0
    except Exception:
        bd.integrity = 0

    # --- policy score ---
    try:
        report = run_policy_checks(vault, key)
        if report.passed:
            bd.policy = _WEIGHT_POLICY
        else:
            errors = sum(1 for v in report.violations if v.severity == "error")
            bd.policy = 0 if errors else _WEIGHT_POLICY // 2
    except Exception:
        bd.policy = _WEIGHT_POLICY  # no policies defined → full marks

    return bd


def score_all(vault: Any) -> dict[str, ScoreBreakdown]:
    """Return scores for every secret key in *vault*."""
    data = vault.load()
    secrets: dict = data.get("secrets", {})
    return {key: score_secret(vault, key) for key in secrets}
