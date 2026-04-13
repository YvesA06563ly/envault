"""env_check.py — Validate that required secrets exist and are non-empty in the vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CheckResult:
    key: str
    present: bool
    non_empty: bool
    message: str


@dataclass
class CheckReport:
    results: List[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.present and r.non_empty for r in self.results)

    @property
    def missing(self) -> List[str]:
        return [r.key for r in self.results if not r.present]

    @property
    def empty(self) -> List[str]:
        return [r.key for r in self.results if r.present and not r.non_empty]


def check_secrets(
    vault,
    required_keys: List[str],
    passphrase: str,
) -> CheckReport:
    """Check that every key in *required_keys* exists and is non-empty."""
    from envault.vault import Vault  # local import to avoid circular deps

    report = CheckReport()
    for key in required_keys:
        raw: Optional[str] = vault.get(key)
        if raw is None:
            report.results.append(
                CheckResult(key=key, present=False, non_empty=False,
                            message=f"'{key}' is missing from the vault")
            )
            continue
        try:
            from envault.crypto import decrypt
            value = decrypt(raw, passphrase)
        except Exception:
            report.results.append(
                CheckResult(key=key, present=True, non_empty=False,
                            message=f"'{key}' could not be decrypted")
            )
            continue
        non_empty = bool(value and value.strip())
        msg = "ok" if non_empty else f"'{key}' is present but empty"
        report.results.append(
            CheckResult(key=key, present=True, non_empty=non_empty, message=msg)
        )
    return report


def check_from_file(vault, path: str, passphrase: str) -> CheckReport:
    """Load a newline-separated list of required keys from *path* and check them."""
    with open(path) as fh:
        keys = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return check_secrets(vault, keys, passphrase)
