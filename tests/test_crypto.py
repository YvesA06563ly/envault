"""Tests for envault.crypto encryption/decryption."""

import pytest
from envault.crypto import encrypt, decrypt


PASSPHRASE = "super-secret-passphrase"
PLAINTEXT = "my_secret_value_123"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSPHRASE)
    assert isinstance(result, str)
    assert result != PLAINTEXT


def test_encrypt_decrypt_roundtrip():
    payload = encrypt(PLAINTEXT, PASSPHRASE)
    recovered = decrypt(payload, PASSPHRASE)
    assert recovered == PLAINTEXT


def test_decrypt_wrong_passphrase_raises():
    payload = encrypt(PLAINTEXT, PASSPHRASE)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(payload, "wrong-passphrase")


def test_encrypt_produces_unique_ciphertexts():
    """Each encryption should produce a different ciphertext (random salt)."""
    a = encrypt(PLAINTEXT, PASSPHRASE)
    b = encrypt(PLAINTEXT, PASSPHRASE)
    assert a != b


def test_decrypt_corrupted_payload_raises():
    with pytest.raises(ValueError):
        decrypt("notvalidbase64!!", PASSPHRASE)
