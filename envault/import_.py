"""
envault/import_.py

Import secrets into the vault from .env files, JSON, or shell-export files.
"""
from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import Dict, Tuple


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_dotenv(text: str) -> Dict[str, str]:
    """Parse KEY=VALUE pairs from a .env-style file."""
    secrets: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Strip optional leading 'export '
        line = re.sub(r"^export\s+", "", line)
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        # Remove surrounding quotes from value
        value = value.strip()
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if key:
            secrets[key] = value
    return secrets


def _parse_json(text: str) -> Dict[str, str]:
    """Parse a flat JSON object of string key/value pairs."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("JSON input must be a top-level object")
    return {str(k): str(v) for k, v in data.items()}


def _parse_shell(text: str) -> Dict[str, str]:
    """Parse 'export KEY=VALUE' shell lines (handles quoted values via shlex)."""
    secrets: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            tokens = shlex.split(line)
        except ValueError:
            continue
        for token in tokens:
            if token.startswith("export"):
                continue
            if "=" in token:
                key, _, value = token.partition("=")
                if key:
                    secrets[key] = value
    return secrets


_PARSERS = {
    "dotenv": _parse_dotenv,
    "json": _parse_json,
    "shell": _parse_shell,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def import_secrets(
    vault,
    source: str,
    fmt: str = "dotenv",
    overwrite: bool = False,
) -> Tuple[int, int]:
    """
    Import secrets from *source* text into *vault*.

    Returns (imported_count, skipped_count).
    Raises ValueError for unknown format or bad input.
    """
    if fmt not in _PARSERS:
        raise ValueError(f"Unknown import format '{fmt}'. Choose from: {list(_PARSERS)}")

    parsed = _PARSERS[fmt](source)
    imported = skipped = 0

    for key, value in parsed.items():
        existing = vault.get(key)
        if existing is not None and not overwrite:
            skipped += 1
            continue
        vault.set(key, value)
        imported += 1

    if imported:
        vault.save()

    return imported, skipped


def import_secrets_from_file(
    vault,
    path: str | Path,
    fmt: str | None = None,
    overwrite: bool = False,
) -> Tuple[int, int]:
    """Convenience wrapper that reads *path* and infers format from extension."""
    path = Path(path)
    if fmt is None:
        ext = path.suffix.lower()
        fmt = {"json": "json", ".env": "dotenv", ".sh": "shell"}.get(ext, "dotenv")
    return import_secrets(vault, path.read_text(encoding="utf-8"), fmt=fmt, overwrite=overwrite)
