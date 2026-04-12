"""CLI entry point for envault."""

import click
from pathlib import Path

from envault.vault import Vault


def _get_passphrase(ctx: click.Context) -> str:
    return click.prompt("Vault passphrase", hide_input=True)


@click.group()
@click.option("--vault", "vault_path", default=".envault/vault.enc",
              show_default=True, help="Path to the vault file.")
@click.pass_context
def cli(ctx: click.Context, vault_path: str) -> None:
    """envault — secure environment secret manager."""
    ctx.ensure_object(dict)
    ctx.obj["vault"] = Vault(Path(vault_path))


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_secret(ctx: click.Context, key: str, value: str) -> None:
    """Store or update a secret KEY=VALUE in the vault."""
    vault: Vault = ctx.obj["vault"]
    passphrase = _get_passphrase(ctx)
    vault.set_secret(key, value, passphrase)
    click.echo(f"✓ Secret '{key}' saved.")


@cli.command("get")
@click.argument("key")
@click.pass_context
def get_secret(ctx: click.Context, key: str) -> None:
    """Retrieve a secret by KEY."""
    vault: Vault = ctx.obj["vault"]
    passphrase = _get_passphrase(ctx)
    secrets = vault.load(passphrase)
    if key not in secrets:
        raise click.ClickException(f"Key '{key}' not found in vault.")
    click.echo(secrets[key])


@cli.command("list")
@click.pass_context
def list_secrets(ctx: click.Context) -> None:
    """List all secret keys stored in the vault."""
    vault: Vault = ctx.obj["vault"]
    passphrase = _get_passphrase(ctx)
    secrets = vault.load(passphrase)
    if not secrets:
        click.echo("Vault is empty.")
    else:
        for key in sorted(secrets):
            click.echo(f"  {key}")


@cli.command("delete")
@click.argument("key")
@click.pass_context
def delete_secret(ctx: click.Context, key: str) -> None:
    """Delete a secret by KEY."""
    vault: Vault = ctx.obj["vault"]
    passphrase = _get_passphrase(ctx)
    removed = vault.delete_secret(key, passphrase)
    if removed:
        click.echo(f"✓ Secret '{key}' deleted.")
    else:
        raise click.ClickException(f"Key '{key}' not found in vault.")
