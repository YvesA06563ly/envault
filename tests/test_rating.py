"""Tests for envault.rating."""

from __future__ import annotations

import json
import pytest

from envault.rating import (
    rate_secret,
    get_rating,
    list_ratings,
    clear_rating,
    RatingResult,
)

_RATINGS_KEY = "__ratings__"


class _FakeVault:
    def __init__(self):
        self._store: dict = {}
        self.saved = False

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value: str):
        self._store[key] = value

    def save(self):
        self.saved = True


@pytest.fixture()
def vault():
    return _FakeVault()


def test_rate_strong_secret_gives_high_score(vault):
    result = rate_secret(vault, "DB_PASS", "Tr0ub4dor&3XqZ!")
    assert result.score >= 80
    assert result.grade in ("A", "B")
    assert result.key == "DB_PASS"


def test_rate_weak_short_secret_gives_low_score(vault):
    result = rate_secret(vault, "TOKEN", "abc")
    assert result.score < 60
    assert result.grade == "F"
    assert any("shorter" in r for r in result.reasons)


def test_rate_no_special_chars_penalised(vault):
    result = rate_secret(vault, "KEY", "Abcdefgh1234")
    assert any("special" in r for r in result.reasons)


def test_rate_no_digits_penalised(vault):
    result = rate_secret(vault, "KEY", "Abcdefgh!@#$")
    assert any("numeric" in r for r in result.reasons)


def test_rate_persists_to_vault(vault):
    rate_secret(vault, "MY_KEY", "Sup3r$ecret!XYZ")
    assert vault.saved
    raw = vault.get(_RATINGS_KEY)
    data = json.loads(raw)
    assert "MY_KEY" in data


def test_get_rating_returns_none_for_unknown(vault):
    assert get_rating(vault, "MISSING") is None


def test_get_rating_returns_stored_result(vault):
    rate_secret(vault, "API_KEY", "Str0ng!Pass#99")
    result = get_rating(vault, "API_KEY")
    assert isinstance(result, RatingResult)
    assert result.key == "API_KEY"


def test_list_ratings_sorted_by_score_ascending(vault):
    rate_secret(vault, "WEAK", "abc")
    rate_secret(vault, "STRONG", "Tr0ub4dor&3XqZ!")
    results = list_ratings(vault)
    assert results[0].key == "WEAK"
    assert results[-1].key == "STRONG"


def test_list_ratings_empty_vault(vault):
    assert list_ratings(vault) == []


def test_clear_rating_removes_entry(vault):
    rate_secret(vault, "OLD_KEY", "Tr0ub4dor&3XqZ!")
    removed = clear_rating(vault, "OLD_KEY")
    assert removed is True
    assert get_rating(vault, "OLD_KEY") is None


def test_clear_rating_returns_false_for_missing(vault):
    assert clear_rating(vault, "NONEXISTENT") is False


def test_low_diversity_penalised(vault):
    result = rate_secret(vault, "KEY", "aaaaaaaa")
    assert any("diversity" in r for r in result.reasons)


def test_score_clamped_to_zero(vault):
    result = rate_secret(vault, "K", "a")
    assert result.score >= 0
