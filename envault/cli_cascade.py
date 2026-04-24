"""CLI commands for cascade management."""

from __future__ import annotations

import click

from envault.cascade import (
    add_cascade,
    remove_cascade,
    list_cascade,
    list_all_cascades,
    resolve_cascade,
)
from envault.vault import Vault
from envault.cli import _get_passphrase


@click.group("cascade")
def cascade_group():
    """Manage secret cascade propagation rules."""


@cascade_group.command("add")
@click.argument("source")
@click.argument("target")
@click.pass_context
def add_cascade_cmd(ctx: click.Context, source: str, target: str) -> None:
    """Add a cascade rule: TARGET updates when SOURCE changes."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase=passphrase)
    vault.load()
    add_cascade(vault, source, target)
    click.echo(f"Cascade added: {source} -> {target}")


@cascade_group.command("remove")
@click.argument("source")
@click.argument("target")
@click.pass_context
def remove_cascade_cmd(ctx: click.Context, source: str, target: str) -> None:
    """Remove a cascade rule."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase=passphrase)
    vault.load()
    removed = remove_cascade(vault, source, target)
    if removed:
        click.echo(f"Cascade removed: {source} -> {target}")
    else:
        click.echo(f"No cascade found: {source} -> {target}", err=True)
        raise SystemExit(1)


@cascade_group.command("list")
@click.argument("source")
@click.pass_context
def list_cascade_cmd(ctx: click.Context, source: str) -> None:
    """List direct cascade targets for SOURCE."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase=passphrase)
    vault.load()
    targets = list_cascade(vault, source)
    if not targets:
        click.echo(f"No cascades defined for '{source}'.")
    else:
        for t in targets:
            click.echo(t)


@cascade_group.command("show-all")
@click.pass_context
def show_all_cmd(ctx: click.Context) -> None:
    """Show all cascade rules."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase=passphrase)
    vault.load()
    all_cascades = list_all_cascades(vault)
    if not all_cascades:
        click.echo("No cascade rules defined.")
    else:
        for src, targets in sorted(all_cascades.items()):
            for tgt in targets:
                click.echo(f"{src} -> {tgt}")


@cascade_group.command("resolve")
@click.argument("source")
@click.pass_context
def resolve_cmd(ctx: click.Context, source: str) -> None:
    """Resolve all downstream keys (including transitive) from SOURCE."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase=passphrase)
    vault.load()
    downstream = resolve_cascade(vault, source)
    if not downstream:
        click.echo(f"No downstream keys for '{source}'.")
    else:
        for key in downstream:
            click.echo(key)
