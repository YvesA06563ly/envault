"""Cryptographic utilities for encrypting and decrypting secrets."""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


SALT_SIZE = 16
ITERATIONS = 480_000


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a passphrase and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    raw_key = kdf.derive(passphrase.encode())
    return base64.urlsafe_b64encode(raw_key)


def encrypt(plaintext: str, passphrase: str) -> str:
    """Encrypt plaintext using a passphrase. Returns a base64-encoded token."""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(passphrase, salt)
    token = Fernet(key).encrypt(plaintext.encode())
    payload = base64.urlsafe_b64encode(salt + base64.urlsafe_b64decode(token))
    return payload.decode()


def decrypt(payload: str, passphrase: str) -> str:
    """Decrypt a payload produced by encrypt(). Raises ValueError on failure."""
    try:
        raw = base64.urlsafe_b64decode(payload.encode())
        salt, token_bytes = raw[:SALT_SIZE], raw[SALT_SIZE:]
        key = derive_key(passphrase, salt)
        token = base64.urlsafe_b64encode(token_bytes)
        return Fernet(key).decrypt(token).decode()
    except (InvalidToken, Exception) as exc:
        raise ValueError("Decryption failed: invalid passphrase or corrupted data.") from exc
