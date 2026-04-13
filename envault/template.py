"""Template rendering: substitute secrets into template strings."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envault.vault import Vault

# Matches {{ SECRET_NAME }} with optional surrounding whitespace
_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


@dataclass
class RenderResult:
    rendered: str
    resolved: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.missing) == 0


def render_template(template: str, vault: "Vault", passphrase: str) -> RenderResult:
    """Replace every {{ KEY }} placeholder with the matching secret value.

    Keys that are not found in the vault are left unreplaced and collected
    in ``RenderResult.missing``.
    """
    resolved: list[str] = []
    missing: list[str] = []

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        try:
            value = vault.get(key, passphrase)  # type: ignore[attr-defined]
            resolved.append(key)
            return value
        except Exception:
            missing.append(key)
            return match.group(0)  # leave placeholder intact

    rendered = _PLACEHOLDER_RE.sub(_replace, template)
    return RenderResult(rendered=rendered, resolved=resolved, missing=missing)


def render_template_file(
    path: str, vault: "Vault", passphrase: str
) -> RenderResult:
    """Read a template file from *path* and render it."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    return render_template(content, vault, passphrase)
