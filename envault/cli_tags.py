"""CLI commands for secret tag management."""
from __future__ import annotations

import click

from envault.cli import _get_passphrase
from envault.vault import Vault
from envault.tags import add_tag, remove_tag, list_tags, find_by_tag, clear_tags


@click.group(name="tag", help="Manage tags on secrets.")
def tag_group() -> None:
    pass


@tag_group.command("add")
@click.argument("secret_key")
@click.argument("tag")
@click.option("--vault-path", default=".envault", show_default=True)
def add_tag_cmd(secret_key: str, tag: str, vault_path: str) -> None:
    """Attach TAG to SECRET_KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    add_tag(vault, secret_key, tag)
    click.echo(f"Tag '{tag}' added to '{secret_key}'.")


@tag_group.command("remove")
@click.argument("secret_key")
@click.argument("tag")
@click.option("--vault-path", default=".envault", show_default=True)
def remove_tag_cmd(secret_key: str, tag: str, vault_path: str) -> None:
    """Remove TAG from SECRET_KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    try:
        remove_tag(vault, secret_key, tag)
        click.echo(f"Tag '{tag}' removed from '{secret_key}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@tag_group.command("list")
@click.argument("secret_key")
@click.option("--vault-path", default=".envault", show_default=True)
def list_tags_cmd(secret_key: str, vault_path: str) -> None:
    """List all tags on SECRET_KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    tags = list_tags(vault, secret_key)
    if tags:
        for t in tags:
            click.echo(t)
    else:
        click.echo(f"No tags found for '{secret_key}'.")


@tag_group.command("find")
@click.argument("tag")
@click.option("--vault-path", default=".envault", show_default=True)
def find_by_tag_cmd(tag: str, vault_path: str) -> None:
    """Find all secrets carrying TAG."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    keys = find_by_tag(vault, tag)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No secrets found with tag '{tag}'.")


@tag_group.command("clear")
@click.argument("secret_key")
@click.option("--vault-path", default=".envault", show_default=True)
def clear_tags_cmd(secret_key: str, vault_path: str) -> None:
    """Remove all tags from SECRET_KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    clear_tags(vault, secret_key)
    click.echo(f"All tags cleared from '{secret_key}'.")
