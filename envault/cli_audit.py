"""CLI commands for the audit log."""

from __future__ import annotations

import click

from envault.audit import get_log
from envault.cli import _get_passphrase
from envault.vault import Vault


@click.group("audit")
def audit_group() -> None:
    """View the audit log for secret operations."""


@audit_group.command("log")
@click.option("--key", default=None, help="Filter entries by secret key.")
@click.option("--action", default=None, help="Filter entries by action type.")
@click.option(
    "--limit",
    default=20,
    show_default=True,
    help="Maximum number of entries to display.",
)
@click.option("--vault-path", default=".envault", show_default=True)
def show_log_cmd(
    key: str | None,
    action: str | None,
    limit: int,
    vault_path: str,
) -> None:
    """Display recent audit log entries."""
    passphrase = _get_passphrase(confirm=False)
    vault = Vault(vault_path, passphrase)
    vault.load()

    entries = get_log(vault, key=key, action=action, limit=limit)
    if not entries:
        click.echo("No audit entries found.")
        return

    for entry in entries:
        parts = [entry["timestamp"], entry["action"].upper(), entry["key"]]
        if entry.get("actor"):
            parts.append(f"actor={entry['actor']}")
        if entry.get("details"):
            parts.append(entry["details"])
        click.echo("  ".join(parts))


@audit_group.command("clear")
@click.option("--vault-path", default=".envault", show_default=True)
@click.confirmation_option(prompt="Clear the entire audit log?")
def clear_log_cmd(vault_path: str) -> None:
    """Delete all audit log entries."""
    passphrase = _get_passphrase(confirm=False)
    vault = Vault(vault_path, passphrase)
    vault.load()
    vault.set("__audit_log__", "[]")
    vault.save()
    click.echo("Audit log cleared.")
