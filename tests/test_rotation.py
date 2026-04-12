"""Tests for envault.rotation module."""

from __future__ import annotations

import datetime
import json

import pytest

from envault.rotation import (
    ROTATION_META_KEY,
    get_rotation_meta,
    last_rotated,
    needs_rotation,
    record_rotation,
    rotate_secret,
)


class _FakeVault:
    """Minimal vault stub for rotation tests."""

    def __init__(self):
        self.secrets: dict = {}
        self._saved = False

    def set(self, key: str, value: str) -> None:
        self.secrets[key] = value

    def get(self, key: str):
        return self.secrets.get(key)

    def save(self) -> None:
        self._saved = True


@pytest.fixture()
def vault():
    return _FakeVault()


def test_get_rotation_meta_empty(vault):
    assert get_rotation_meta(vault) == {}


def test_record_rotation_stores_timestamp(vault):
    record_rotation(vault, "DB_PASSWORD")
    meta = get_rotation_meta(vault)
    assert "DB_PASSWORD" in meta
    ts = datetime.datetime.fromisoformat(meta["DB_PASSWORD"])
    assert (datetime.datetime.utcnow() - ts).seconds < 5


def test_last_rotated_none_when_never_rotated(vault):
    assert last_rotated(vault, "API_KEY") is None


def test_last_rotated_returns_datetime_after_rotation(vault):
    record_rotation(vault, "API_KEY")
    ts = last_rotated(vault, "API_KEY")
    assert isinstance(ts, datetime.datetime)


def test_needs_rotation_true_when_never_rotated(vault):
    assert needs_rotation(vault, "SOME_KEY") is True


def test_needs_rotation_false_when_just_rotated(vault):
    record_rotation(vault, "FRESH_KEY")
    assert needs_rotation(vault, "FRESH_KEY", max_age_days=90) is False


def test_needs_rotation_true_when_old(vault):
    old_ts = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).isoformat()
    meta = {"OLD_KEY": old_ts}
    vault.secrets[ROTATION_META_KEY] = json.dumps(meta)
    assert needs_rotation(vault, "OLD_KEY", max_age_days=90) is True


def test_rotate_secret_updates_value_and_records_time(vault):
    vault.set("DB_PASS", "old_value")
    rotate_secret(vault, "DB_PASS", "new_value")
    assert vault.secrets["DB_PASS"] == "new_value"
    assert last_rotated(vault, "DB_PASS") is not None


def test_rotate_secret_raises_for_reserved_key(vault):
    with pytest.raises(ValueError, match="reserved key"):
        rotate_secret(vault, ROTATION_META_KEY, "anything")
