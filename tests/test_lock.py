"""Tests for envault.lock."""

from __future__ import annotations

import time
import pytest
from envault.lock import acquire_lock, release_lock, lock_status, _LOCK_KEY


class _FakeVault:
    def __init__(self):
        self._data: dict = {}
        self.saved = 0

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        if value is None:
            self._data.pop(key, None)
        else:
            self._data[key] = value

    def save(self):
        self.saved += 1


@pytest.fixture
def vault():
    return _FakeVault()


def test_acquire_lock_succeeds_when_free(vault):
    assert acquire_lock(vault, "alice") is True
    assert vault.saved == 1


def test_acquire_lock_fails_when_held_by_other(vault):
    acquire_lock(vault, "alice", ttl=60)
    assert acquire_lock(vault, "bob", ttl=60) is False


def test_acquire_lock_same_owner_refreshes(vault):
    acquire_lock(vault, "alice", ttl=60)
    assert acquire_lock(vault, "alice", ttl=60) is True


def test_acquire_lock_succeeds_after_expiry(vault):
    acquire_lock(vault, "alice", ttl=0)  # TTL=0 expires immediately
    time.sleep(0.01)
    assert acquire_lock(vault, "bob", ttl=60) is True


def test_release_lock_by_owner(vault):
    acquire_lock(vault, "alice", ttl=60)
    assert release_lock(vault, "alice") is True
    assert vault.get(_LOCK_KEY) is None


def test_release_lock_by_non_owner_fails(vault):
    acquire_lock(vault, "alice", ttl=60)
    assert release_lock(vault, "bob") is False
    assert vault.get(_LOCK_KEY) is not None


def test_release_lock_when_not_locked(vault):
    assert release_lock(vault, "alice") is False


def test_lock_status_when_locked(vault):
    acquire_lock(vault, "alice", ttl=60)
    status = lock_status(vault)
    assert status is not None
    assert status["owner"] == "alice"
    assert status["ttl_remaining"] > 0


def test_lock_status_when_free(vault):
    assert lock_status(vault) is None


def test_lock_status_after_expiry(vault):
    acquire_lock(vault, "alice", ttl=0)
    time.sleep(0.01)
    assert lock_status(vault) is None


def test_save_called_on_acquire_and_release(vault):
    acquire_lock(vault, "alice", ttl=60)
    release_lock(vault, "alice")
    assert vault.saved == 2
