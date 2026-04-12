"""Search secrets by key pattern or value substring within the vault."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from typing import List, Optional

from envault.vault import Vault


@dataclass
class SearchResult:
    key: str
    value: str
    match_type: str  # 'key' | 'value' | 'both'


def search_secrets(
    vault: Vault,
    passphrase: str,
    *,
    key_pattern: Optional[str] = None,
    value_substring: Optional[str] = None,
    case_sensitive: bool = False,
) -> List[SearchResult]:
    """Search vault secrets by key glob pattern and/or value substring.

    Args:
        vault: The Vault instance to search.
        passphrase: Passphrase used to decrypt secrets.
        key_pattern: Optional glob pattern to match against keys (e.g. "DB_*").
        value_substring: Optional substring to search for in decrypted values.
        case_sensitive: Whether matching is case-sensitive (default False).

    Returns:
        List of SearchResult items ordered by key.

    Raises:
        ValueError: If neither key_pattern nor value_substring is provided.
    """
    if key_pattern is None and value_substring is None:
        raise ValueError("At least one of key_pattern or value_substring must be provided.")

    raw = vault.load()
    secrets: dict = raw.get("secrets", {})

    flags = 0 if case_sensitive else re.IGNORECASE

    results: List[SearchResult] = []

    for key, encrypted_value in sorted(secrets.items()):
        from envault.crypto import decrypt

        try:
            value = decrypt(encrypted_value, passphrase)
        except Exception:
            continue

        key_match = False
        value_match = False

        if key_pattern is not None:
            pattern = key_pattern if case_sensitive else key_pattern.upper()
            target_key = key if case_sensitive else key.upper()
            key_match = fnmatch.fnmatch(target_key, pattern)

        if value_substring is not None:
            needle = value_substring if case_sensitive else value_substring.lower()
            haystack = value if case_sensitive else value.lower()
            value_match = needle in haystack

        if key_pattern and value_substring:
            if key_match and value_match:
                match_type = "both"
            elif key_match:
                match_type = "key"
            elif value_match:
                match_type = "value"
            else:
                continue
        elif key_pattern:
            if not key_match:
                continue
            match_type = "key"
        else:
            if not value_match:
                continue
            match_type = "value"

        results.append(SearchResult(key=key, value=value, match_type=match_type))

    return results
