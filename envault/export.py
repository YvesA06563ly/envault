"""Export secrets from a vault to various formats."""

import json
from typing import Optional

SUPPORTED_FORMATS = ("dotenv", "json", "shell")


def _collect_secrets(vault, passphrase: str) -> dict:
    """Retrieve all non-metadata secrets from the vault."""
    raw = vault.get("__secrets__") or {}
    secrets = {}
    for key, encrypted_value in raw.items():
        from envault.crypto import decrypt
        try:
            secrets[key] = decrypt(encrypted_value, passphrase)
        except Exception as exc:
            raise ValueError(f"Failed to decrypt secret '{key}': {exc}") from exc
    return secrets


def export_dotenv(secrets: dict) -> str:
    """Render secrets as a .env file string."""
    lines = []
    for key, value in sorted(secrets.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_json(secrets: dict, indent: int = 2) -> str:
    """Render secrets as a JSON string."""
    return json.dumps(secrets, indent=indent, sort_keys=True) + "\n"


def export_shell(secrets: dict) -> str:
    """Render secrets as shell export statements."""
    lines = []
    for key, value in sorted(secrets.items()):
        escaped = value.replace("'", "'\\''")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + ("\n" if lines else "")


def export_secrets(
    vault,
    passphrase: str,
    fmt: str = "dotenv",
    filter_prefix: Optional[str] = None,
) -> str:
    """Export secrets from *vault* in the requested format.

    Args:
        vault: A Vault-compatible object.
        passphrase: Master passphrase used to decrypt secrets.
        fmt: Output format — one of 'dotenv', 'json', or 'shell'.
        filter_prefix: If given, only export keys starting with this prefix.

    Returns:
        A string containing the exported secrets.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    secrets = _collect_secrets(vault, passphrase)

    if filter_prefix:
        secrets = {k: v for k, v in secrets.items() if k.startswith(filter_prefix)}

    if fmt == "dotenv":
        return export_dotenv(secrets)
    if fmt == "json":
        return export_json(secrets)
    return export_shell(secrets)
