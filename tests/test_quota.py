"""Tests for envault.quota."""

import json
import pytest

from envault.quota import (
    set_quota,
    remove_quota,
    get_quota,
    list_quotas,
    check_quota,
)

_QUOTA_KEY = "__quota__"


class _FakeVault:
    def __init__(self):
        self._store: dict = {}
        self.saved = False

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def save(self):
        self.saved = True


@pytest.fixture
def vault():
    return _FakeVault()


def test_set_and_get_quota(vault):
    set_quota(vault, "default", 50)
    assert get_quota(vault, "default") == 50


def test_get_quota_missing_returns_none(vault):
    assert get_quota(vault, "nonexistent") is None


def test_set_quota_invalid_limit_raises(vault):
    with pytest.raises(ValueError):
        set_quota(vault, "default", 0)
    with pytest.raises(ValueError):
        set_quota(vault, "default", -5)


def test_remove_existing_quota(vault):
    set_quota(vault, "prod", 100)
    result = remove_quota(vault, "prod")
    assert result is True
    assert get_quota(vault, "prod") is None


def test_remove_missing_quota_returns_false(vault):
    result = remove_quota(vault, "ghost")
    assert result is False


def test_list_quotas_empty(vault):
    assert list_quotas(vault) == {}


def test_list_quotas_multiple(vault):
    set_quota(vault, "dev", 10)
    set_quota(vault, "prod", 200)
    quotas = list_quotas(vault)
    assert quotas == {"dev": 10, "prod": 200}


def test_check_quota_within_limit(vault):
    set_quota(vault, "staging", 5)
    assert check_quota(vault, "staging", 4) is True


def test_check_quota_at_limit(vault):
    set_quota(vault, "staging", 5)
    assert check_quota(vault, "staging", 5) is False


def test_check_quota_exceeds_limit(vault):
    set_quota(vault, "staging", 5)
    assert check_quota(vault, "staging", 10) is False


def test_check_quota_no_limit_always_passes(vault):
    assert check_quota(vault, "unlimited", 9999) is True


def test_overwrite_quota(vault):
    set_quota(vault, "ns", 10)
    set_quota(vault, "ns", 20)
    assert get_quota(vault, "ns") == 20


def test_save_called_on_set(vault):
    set_quota(vault, "x", 1)
    assert vault.saved is True


def test_save_called_on_remove(vault):
    set_quota(vault, "x", 1)
    vault.saved = False
    remove_quota(vault, "x")
    assert vault.saved is True
