"""CLI commands for secret value history."""
from __future__ import annotations

import click

from envault.history import clear_history, get_history, list_keys_with_history
from envault.vault import Vault
from envault.cli import _get_passphrase


@click.group("history")
def history_group() -> None:
    """View and manage secret value history."""


@history_group.command("show")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def show_history_cmd(key: str, vault_path: str) -> None:
    """Show the value history for KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    entries = get_history(vault, key)
    if not entries:
        click.echo(f"No history found for '{key}'.")
        return
    click.echo(f"History for '{key}' ({len(entries)} entries):")
    for i, entry in enumerate(entries, 1):
        prev = entry.get("previous") or "<none>"
        click.echo(f"  [{i}] {entry['timestamp']}  prev={prev}")


@history_group.command("clear")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
@click.confirmation_option(prompt="Clear all history for this key?")
def clear_history_cmd(key: str, vault_path: str) -> None:
    """Clear the value history for KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    removed = clear_history(vault, key)
    if removed:
        click.echo(f"History cleared for '{key}'.")
    else:
        click.echo(f"No history to clear for '{key}'.")


@history_group.command("list")
@click.option("--vault-path", default=".envault", show_default=True)
def list_history_cmd(vault_path: str) -> None:
    """List all keys that have recorded history."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    keys = list_keys_with_history(vault)
    if not keys:
        click.echo("No history recorded yet.")
        return
    click.echo("Keys with history:")
    for k in sorted(keys):
        click.echo(f"  {k}")
