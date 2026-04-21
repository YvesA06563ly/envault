"""Badge module: generate status badges for secrets (health, expiry, rotation, etc.)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from envault.expiry import get_expiry, is_expired
from envault.rotation import last_rotated, needs_rotation
from envault.checksum import verify_checksum


@dataclass
class Badge:
    key: str
    status: str        # "ok" | "warning" | "error" | "unknown"
    label: str
    detail: str

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "status": self.status,
            "label": self.label,
            "detail": self.detail,
        }


def _expiry_badge(vault, key: str) -> Badge:
    expiry = get_expiry(vault, key)
    if expiry is None:
        return Badge(key, "unknown", "expiry", "no expiry set")
    if is_expired(vault, key):
        return Badge(key, "error", "expiry", f"expired on {expiry}")
    return Badge(key, "ok", "expiry", f"expires {expiry}")


def _rotation_badge(vault, key: str, max_age_days: int = 90) -> Badge:
    rotated = last_rotated(vault, key)
    if rotated is None:
        return Badge(key, "unknown", "rotation", "never rotated")
    if needs_rotation(vault, key, max_age_days):
        return Badge(key, "warning", "rotation", f"last rotated {rotated}")
    return Badge(key, "ok", "rotation", f"last rotated {rotated}")


def _integrity_badge(vault, key: str) -> Badge:
    result = verify_checksum(vault, key)
    if result is None:
        return Badge(key, "unknown", "integrity", "no checksum recorded")
    if result:
        return Badge(key, "ok", "integrity", "checksum verified")
    return Badge(key, "error", "integrity", "checksum mismatch")


def get_badges(vault, key: str, max_age_days: int = 90) -> List[Badge]:
    """Return all status badges for a given secret key."""
    return [
        _expiry_badge(vault, key),
        _rotation_badge(vault, key, max_age_days),
        _integrity_badge(vault, key),
    ]


def summary_status(badges: List[Badge]) -> str:
    """Aggregate badge list into a single status string."""
    statuses = {b.status for b in badges}
    if "error" in statuses:
        return "error"
    if "warning" in statuses:
        return "warning"
    if "unknown" in statuses:
        return "unknown"
    return "ok"
