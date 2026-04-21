"""Secret quality rating — scores secrets based on strength, age, and policy compliance."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

_RATINGS_KEY = "__ratings__"


@dataclass
class RatingResult:
    key: str
    score: int          # 0-100
    grade: str          # A / B / C / D / F
    reasons: list[str]

    @property
    def passed(self) -> bool:
        return self.score >= 60


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _load_ratings(vault: Any) -> dict:
    raw = vault.get(_RATINGS_KEY)
    if not raw:
        return {}
    return json.loads(raw)


def _save_ratings(vault: Any, data: dict) -> None:
    vault.set(_RATINGS_KEY, json.dumps(data))
    vault.save()


def rate_secret(vault: Any, key: str, value: str) -> RatingResult:
    """Compute a quality score for *value* and persist it."""
    score = 100
    reasons: list[str] = []

    if len(value) < 8:
        score -= 40
        reasons.append("value is shorter than 8 characters")
    elif len(value) < 16:
        score -= 15
        reasons.append("value is shorter than 16 characters")

    if value.lower() == value:
        score -= 10
        reasons.append("no uppercase characters")
    if not any(c.isdigit() for c in value):
        score -= 10
        reasons.append("no numeric characters")
    if not any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/`~" for c in value):
        score -= 10
        reasons.append("no special characters")
    if len(set(value)) < 6:
        score -= 15
        reasons.append("low character diversity")

    score = max(0, score)
    result = RatingResult(key=key, score=score, grade=_grade(score), reasons=reasons)

    ratings = _load_ratings(vault)
    ratings[key] = {"score": score, "grade": result.grade, "reasons": reasons}
    _save_ratings(vault, ratings)
    return result


def get_rating(vault: Any, key: str) -> RatingResult | None:
    """Return the last persisted rating for *key*, or None."""
    ratings = _load_ratings(vault)
    entry = ratings.get(key)
    if entry is None:
        return None
    return RatingResult(
        key=key,
        score=entry["score"],
        grade=entry["grade"],
        reasons=entry["reasons"],
    )


def list_ratings(vault: Any) -> list[RatingResult]:
    """Return all stored ratings sorted by score ascending."""
    ratings = _load_ratings(vault)
    results = [
        RatingResult(key=k, score=v["score"], grade=v["grade"], reasons=v["reasons"])
        for k, v in ratings.items()
        if not k.startswith("__")
    ]
    return sorted(results, key=lambda r: r.score)


def clear_rating(vault: Any, key: str) -> bool:
    """Remove the stored rating for *key*. Returns True if it existed."""
    ratings = _load_ratings(vault)
    if key not in ratings:
        return False
    del ratings[key]
    _save_ratings(vault, ratings)
    return True
