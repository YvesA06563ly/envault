"""CLI commands for managing secret aliases."""

from __future__ import annotations

import click

from envault.alias import (
    add_alias,
    remove_alias,
    resolve,
    list_aliases,
    aliases_for_key,
)


@click.group("alias", help="Manage short-name aliases for secret keys.")
def alias_group() -> None:  # pragma: no cover
    pass


@alias_group.command("add")
@click.argument("alias")
@click.argument("key")
@click.pass_obj
def add_alias_cmd(vault, alias: str, key: str) -> None:
    """Create ALIAS pointing to KEY."""
    try:
        add_alias(vault, alias, key)
        click.echo(f"Alias '{alias}' -> '{key}' created.")
    except (ValueError, KeyError) as exc:
        raise click.ClickException(str(exc))


@alias_group.command("remove")
@click.argument("alias")
@click.pass_obj
def remove_alias_cmd(vault, alias: str) -> None:
    """Delete ALIAS."""
    try:
        remove_alias(vault, alias)
        click.echo(f"Alias '{alias}' removed.")
    except KeyError as exc:
        raise click.ClickException(str(exc))


@alias_group.command("resolve")
@click.argument("name")
@click.pass_obj
def resolve_cmd(vault, name: str) -> None:
    """Print the canonical key that NAME resolves to."""
    canonical = resolve(vault, name)
    if canonical == name:
        click.echo(f"'{name}' is not an alias (no mapping found).")
    else:
        click.echo(f"'{name}' -> '{canonical}'")


@alias_group.command("list")
@click.pass_obj
def list_aliases_cmd(vault) -> None:
    """List all defined aliases."""
    entries = list_aliases(vault)
    if not entries:
        click.echo("No aliases defined.")
        return
    for entry in entries:
        click.echo(f"  {entry['alias']:30s} -> {entry['key']}")


@alias_group.command("for-key")
@click.argument("key")
@click.pass_obj
def for_key_cmd(vault, key: str) -> None:
    """Show all aliases that point to KEY."""
    names = aliases_for_key(vault, key)
    if not names:
        click.echo(f"No aliases found for '{key}'.")
    else:
        for name in sorted(names):
            click.echo(f"  {name}")
