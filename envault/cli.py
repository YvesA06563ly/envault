"""CLI entry-point for envault."""

from __future__ import annotations

import click

from envault.vault import Vault
from envault.rotation import rotate_secret, last_rotated, needs_rotation


def _get_passphrase(confirm: bool = False) -> str:
    passphrase = click.prompt("Passphrase", hide_input=True)
    if confirm:
        click.prompt("Confirm passphrase", hide_input=True, confirmation_prompt=True)
    return passphrase


@click.group()
@click.option("--vault-path", default=".envault", show_default=True, help="Path to vault directory.")
@click.pass_context
def cli(ctx: click.Context, vault_path: str) -> None:
    """envault — secure secret management CLI."""
    ctx.ensure_object(dict)
    ctx.obj["vault_path"] = vault_path


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_secret(ctx: click.Context, key: str, value: str) -> None:
    """Store a secret KEY=VALUE in the vault."""
    passphrase = _get_passphrase()
    vault = Vault(ctx.obj["vault_path"], passphrase)
    vault.set(key, value)
    click.echo(f"Secret '{key}' stored.")


@cli.command("get")
@click.argument("key")
@click.pass_context
def get_secret(ctx: click.Context, key: str) -> None:
    """Retrieve a secret by KEY."""
    passphrase = _get_passphrase()
    vault = Vault(ctx.obj["vault_path"], passphrase)
    value = vault.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
    else:
        click.echo(value)


@cli.command("list")
@click.pass_context
def list_secrets(ctx: click.Context) -> None:
    """List all stored secret keys."""
    passphrase = _get_passphrase()
    vault = Vault(ctx.obj["vault_path"], passphrase)
    keys = vault.keys()
    if not keys:
        click.echo("No secrets stored.")
    else:
        for key in sorted(keys):
            click.echo(key)


@cli.command("rotate")
@click.argument("key")
@click.argument("new_value")
@click.pass_context
def rotate(ctx: click.Context, key: str, new_value: str) -> None:
    """Rotate the value of KEY to NEW_VALUE and record rotation timestamp."""
    passphrase = _get_passphrase()
    vault = Vault(ctx.obj["vault_path"], passphrase)
    rotate_secret(vault, key, new_value)
    click.echo(f"Secret '{key}' rotated successfully.")


@cli.command("rotation-status")
@click.argument("key")
@click.option("--max-age-days", default=90, show_default=True, help="Max age in days before rotation is due.")
@click.pass_context
def rotation_status(ctx: click.Context, key: str, max_age_days: int) -> None:
    """Show rotation status for KEY."""
    passphrase = _get_passphrase()
    vault = Vault(ctx.obj["vault_path"], passphrase)
    ts = last_rotated(vault, key)
    if ts is None:
        click.echo(f"'{key}' has never been rotated.")
    else:
        click.echo(f"'{key}' last rotated: {ts.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    due = needs_rotation(vault, key, max_age_days)
    click.echo(f"Rotation due: {'YES' if due else 'no'}")
