"""Vault storage: read and write encrypted secret files."""

import json
from pathlib import Path
from typing import Dict

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_PATH = Path(".envault/vault.enc")


class Vault:
    """Manages a single encrypted vault file containing key-value secrets."""

    def __init__(self, path: Path = DEFAULT_VAULT_PATH) -> None:
        self.path = path

    def _ensure_dir(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, passphrase: str) -> Dict[str, str]:
        """Load and decrypt secrets. Returns empty dict if vault doesn't exist."""
        if not self.path.exists():
            return {}
        payload = self.path.read_text(encoding="utf-8").strip()
        plaintext = decrypt(payload, passphrase)
        return json.loads(plaintext)

    def save(self, secrets: Dict[str, str], passphrase: str) -> None:
        """Encrypt and persist secrets to disk."""
        self._ensure_dir()
        plaintext = json.dumps(secrets, indent=2)
        payload = encrypt(plaintext, passphrase)
        self.path.write_text(payload, encoding="utf-8")

    def set_secret(self, key: str, value: str, passphrase: str) -> None:
        """Add or update a single secret."""
        secrets = self.load(passphrase)
        secrets[key] = value
        self.save(secrets, passphrase)

    def delete_secret(self, key: str, passphrase: str) -> bool:
        """Remove a secret by key. Returns True if it existed."""
        secrets = self.load(passphrase)
        existed = key in secrets
        if existed:
            del secrets[key]
            self.save(secrets, passphrase)
        return existed
