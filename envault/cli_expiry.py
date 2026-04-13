"""CLI commands for secret expiry management."""

from __future__ import annotations

import click
from envault.cli import _get_passphrase
from envault.vault import Vault
from envault import expiry as exp


@click.group("expiry")
def expiry_group():
    """Manage secret expiry dates."""


@expiry_group.command("set")
@click.argument("key")
@click.argument("days", type=int)
@click.option("--vault-path", default=".envault", show_default=True)
def set_expiry_cmd(key: str, days: int, vault_path: str):
    """Set KEY to expire in DAYS days."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    try:
        expires_at = exp.set_expiry(vault, key, days)
        click.echo(f"Expiry set: {key} expires at {expires_at.isoformat()}")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@expiry_group.command("clear")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def clear_expiry_cmd(key: str, vault_path: str):
    """Remove expiry for KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    removed = exp.clear_expiry(vault, key)
    if removed:
        click.echo(f"Expiry cleared for '{key}'.")
    else:
        click.echo(f"No expiry was set for '{key}'.")


@expiry_group.command("show")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def show_expiry_cmd(key: str, vault_path: str):
    """Show expiry date for KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    expiry = exp.get_expiry(vault, key)
    if expiry is None:
        click.echo(f"No expiry set for '{key}'.")
    else:
        status = "EXPIRED" if exp.is_expired(vault, key) else "valid"
        click.echo(f"{key}: {expiry.isoformat()} [{status}]")


@expiry_group.command("list")
@click.option("--within", default=7, show_default=True, help="Days window.")
@click.option("--vault-path", default=".envault", show_default=True)
def list_expiring_cmd(within: int, vault_path: str):
    """List secrets expiring within WITHIN days."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    results = exp.list_expiring(vault, within_days=within)
    if not results:
        click.echo(f"No secrets expiring within {within} days.")
        return
    for entry in results:
        tag = " [EXPIRED]" if entry["expired"] else ""
        click.echo(f"  {entry['key']}: {entry['expires_at'].isoformat()}{tag}")
