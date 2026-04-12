"""Diff utilities for comparing vault secrets against a .env file or another source."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from envault.export import _collect_secrets
from envault.import_ import _parse_dotenv, _parse_json, _parse_shell


@dataclass
class DiffEntry:
    key: str
    status: str          # 'added' | 'removed' | 'changed' | 'unchanged'
    vault_value: Optional[str] = None
    other_value: Optional[str] = None


def _parse_source(text: str, fmt: str) -> Dict[str, str]:
    """Parse external source text into a key/value dict."""
    fmt = fmt.lower()
    if fmt == "dotenv":
        return _parse_dotenv(text)
    if fmt == "json":
        return _parse_json(text)
    if fmt == "shell":
        return _parse_shell(text)
    raise ValueError(f"Unsupported format: {fmt!r}. Choose dotenv, json, or shell.")


def diff_secrets(
    vault,
    passphrase: str,
    other: Dict[str, str],
    *,
    include_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare decrypted vault secrets against *other* dict.

    Returns a list of DiffEntry objects sorted by key.
    """
    vault_secrets: Dict[str, str] = _collect_secrets(vault, passphrase)

    all_keys = set(vault_secrets) | set(other)
    entries: List[DiffEntry] = []

    for key in sorted(all_keys):
        v_val = vault_secrets.get(key)
        o_val = other.get(key)

        if v_val is None:
            entries.append(DiffEntry(key, "added", vault_value=None, other_value=o_val))
        elif o_val is None:
            entries.append(DiffEntry(key, "removed", vault_value=v_val, other_value=None))
        elif v_val != o_val:
            entries.append(DiffEntry(key, "changed", vault_value=v_val, other_value=o_val))
        elif include_unchanged:
            entries.append(DiffEntry(key, "unchanged", vault_value=v_val, other_value=o_val))

    return entries


def diff_from_text(
    vault,
    passphrase: str,
    text: str,
    fmt: str = "dotenv",
    *,
    include_unchanged: bool = False,
) -> List[DiffEntry]:
    """Convenience wrapper: parse *text* then diff against vault."""
    other = _parse_source(text, fmt)
    return diff_secrets(vault, passphrase, other, include_unchanged=include_unchanged)
