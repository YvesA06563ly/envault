"""CLI commands for archival management."""

from __future__ import annotations

import click

from envault.archival import (
    archive_secret,
    unarchive_secret,
    is_archived,
    list_archived,
)
from envault.vault import Vault
from envault.cli import _get_passphrase


@click.group("archive", help="Archive and unarchive secrets.")
def archive_group() -> None:  # pragma: no cover
    pass


@archive_group.command("add")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def archive_cmd(key: str, vault_path: str) -> None:
    """Archive a secret KEY so it is hidden from active listings."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    archive_secret(vault, key)
    click.echo(f"Archived '{key}'.")


@archive_group.command("remove")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def unarchive_cmd(key: str, vault_path: str) -> None:
    """Restore an archived secret KEY to active status."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    unarchive_secret(vault, key)
    click.echo(f"Unarchived '{key}'.")


@archive_group.command("show")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def show_archive_cmd(key: str, vault_path: str) -> None:
    """Show whether KEY is archived."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    status = "archived" if is_archived(vault, key) else "active"
    click.echo(f"'{key}' is {status}.")


@archive_group.command("list")
@click.option("--vault-path", default=".envault", show_default=True)
def list_archived_cmd(vault_path: str) -> None:
    """List all archived secrets."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    keys = list_archived(vault)
    if not keys:
        click.echo("No archived secrets.")
    else:
        for k in keys:
            click.echo(k)
