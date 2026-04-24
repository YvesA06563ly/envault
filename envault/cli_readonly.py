"""CLI commands for managing read-only secret protection."""

from __future__ import annotations

import click

from envault.readonly import protect, unprotect, is_protected, list_protected
from envault.vault import Vault
from envault.cli import _get_passphrase


@click.group("readonly", help="Manage read-only protection for secrets.")
def readonly_group() -> None:
    pass


@readonly_group.command("protect")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def protect_cmd(key: str, vault_path: str) -> None:
    """Mark KEY as read-only."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    protect(vault, key)
    click.echo(f"Secret '{key}' is now read-only.")


@readonly_group.command("unprotect")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def unprotect_cmd(key: str, vault_path: str) -> None:
    """Remove read-only protection from KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    unprotect(vault, key)
    click.echo(f"Read-only protection removed from '{key}'.")


@readonly_group.command("show")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def show_cmd(key: str, vault_path: str) -> None:
    """Show whether KEY is protected."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    status = "read-only" if is_protected(vault, key) else "writable"
    click.echo(f"{key}: {status}")


@readonly_group.command("list")
@click.option("--vault-path", default=".envault", show_default=True)
def list_cmd(vault_path: str) -> None:
    """List all read-only secrets."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    keys = list_protected(vault)
    if not keys:
        click.echo("No read-only secrets.")
    else:
        for k in keys:
            click.echo(k)
