"""Tests for envault.access access-control module."""

import json
import pytest

from envault.access import (
    _ACCESS_KEY,
    grant,
    revoke,
    can,
    list_permissions,
    list_profile_grants,
)


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


@pytest.fixture()
def vault():
    return _FakeVault()


def test_grant_read(vault):
    grant(vault, "DB_PASSWORD", "dev", "read")
    assert can(vault, "DB_PASSWORD", "dev", "read")


def test_grant_write(vault):
    grant(vault, "API_KEY", "admin", "write")
    assert can(vault, "API_KEY", "admin", "write")


def test_grant_idempotent(vault):
    grant(vault, "DB_PASSWORD", "dev", "read")
    grant(vault, "DB_PASSWORD", "dev", "read")
    perms = list_permissions(vault, "DB_PASSWORD")
    assert perms["read"].count("dev") == 1


def test_revoke_removes_permission(vault):
    grant(vault, "DB_PASSWORD", "dev", "read")
    revoke(vault, "DB_PASSWORD", "dev", "read")
    assert not can(vault, "DB_PASSWORD", "dev", "read")


def test_revoke_nonexistent_is_safe(vault):
    revoke(vault, "MISSING_KEY", "dev", "read")  # should not raise


def test_can_returns_false_for_unknown(vault):
    assert not can(vault, "UNKNOWN", "nobody", "read")


def test_invalid_permission_raises(vault):
    with pytest.raises(ValueError, match="Invalid permission"):
        grant(vault, "KEY", "dev", "execute")
    with pytest.raises(ValueError, match="Invalid permission"):
        revoke(vault, "KEY", "dev", "execute")


def test_list_permissions_none_when_missing(vault):
    assert list_permissions(vault, "NO_SUCH_KEY") is None


def test_list_permissions_returns_dict(vault):
    grant(vault, "TOKEN", "ci", "read")
    grant(vault, "TOKEN", "admin", "write")
    perms = list_permissions(vault, "TOKEN")
    assert "ci" in perms["read"]
    assert "admin" in perms["write"]


def test_list_profile_grants(vault):
    grant(vault, "DB_URL", "dev", "read")
    grant(vault, "DB_URL", "dev", "write")
    grant(vault, "API_KEY", "dev", "read")
    grants = list_profile_grants(vault, "dev")
    assert set(grants["DB_URL"]) == {"read", "write"}
    assert grants["API_KEY"] == ["read"]


def test_vault_save_called(vault):
    grant(vault, "X", "p", "read")
    assert vault.saved


def test_acl_persisted_as_json(vault):
    grant(vault, "SECRET", "ops", "read")
    raw = vault.get(_ACCESS_KEY)
    data = json.loads(raw)
    assert "ops" in data["SECRET"]["read"]
