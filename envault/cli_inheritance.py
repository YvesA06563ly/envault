"""CLI commands for secret inheritance."""

from __future__ import annotations

import click

from envault.inheritance import (
    set_inherit,
    clear_inherit,
    get_parent,
    list_inheriting,
)
from envault.vault import Vault
from envault.cli import _get_passphrase


@click.group("inherit")
def inherit_group():
    """Manage secret inheritance rules."""


@inherit_group.command("set")
@click.argument("key")
@click.argument("parent")
@click.option("--vault-path", default=".envault", show_default=True)
def set_inherit_cmd(key: str, parent: str, vault_path: str):
    """Make KEY inherit its value from PARENT."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    try:
        set_inherit(vault, key, parent)
        click.echo(f"'{key}' now inherits from '{parent}'.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@inherit_group.command("clear")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def clear_inherit_cmd(key: str, vault_path: str):
    """Remove inheritance rule for KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    clear_inherit(vault, key)
    click.echo(f"Inheritance cleared for '{key}'.")


@inherit_group.command("show")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def show_inherit_cmd(key: str, vault_path: str):
    """Show the parent that KEY inherits from."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    parent = get_parent(vault, key)
    if parent:
        click.echo(f"'{key}' inherits from '{parent}'.")
    else:
        click.echo(f"'{key}' has no inheritance rule.")


@inherit_group.command("list")
@click.option("--vault-path", default=".envault", show_default=True)
def list_inherit_cmd(vault_path: str):
    """List all inheritance rules."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    rules = list_inheriting(vault)
    if not rules:
        click.echo("No inheritance rules defined.")
        return
    for child, parent in sorted(rules.items()):
        click.echo(f"  {child} -> {parent}")
