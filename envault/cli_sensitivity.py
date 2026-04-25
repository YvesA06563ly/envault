"""CLI commands for managing secret sensitivity classifications."""

from __future__ import annotations

import click

from envault.sensitivity import (
    VALID_LEVELS,
    clear_sensitivity,
    get_sensitivity,
    list_all,
    list_by_level,
    set_sensitivity,
)
from envault.vault import Vault


def _load_vault(ctx: click.Context) -> Vault:
    passphrase = ctx.obj.get("passphrase", "") if ctx.obj else ""
    return Vault(passphrase=passphrase)


@click.group("sensitivity")
def sensitivity_group() -> None:
    """Manage sensitivity classifications for secrets."""


@sensitivity_group.command("set")
@click.argument("key")
@click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
@click.pass_context
def set_sensitivity_cmd(ctx: click.Context, key: str, level: str) -> None:
    """Assign a sensitivity LEVEL to a secret KEY."""
    vault = _load_vault(ctx)
    try:
        set_sensitivity(vault, key, level)
        click.echo(f"Sensitivity for '{key}' set to '{level}'.")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@sensitivity_group.command("clear")
@click.argument("key")
@click.pass_context
def clear_sensitivity_cmd(ctx: click.Context, key: str) -> None:
    """Remove the sensitivity classification for a secret KEY."""
    vault = _load_vault(ctx)
    clear_sensitivity(vault, key)
    click.echo(f"Sensitivity classification cleared for '{key}'.")


@sensitivity_group.command("show")
@click.argument("key")
@click.pass_context
def show_sensitivity_cmd(ctx: click.Context, key: str) -> None:
    """Show the sensitivity level for a secret KEY."""
    vault = _load_vault(ctx)
    level = get_sensitivity(vault, key)
    if level is None:
        click.echo(f"No sensitivity classification set for '{key}'.")
    else:
        click.echo(f"{key}: {level}")


@sensitivity_group.command("list")
@click.option("--level", type=click.Choice(VALID_LEVELS, case_sensitive=False), default=None,
              help="Filter by sensitivity level.")
@click.pass_context
def list_sensitivity_cmd(ctx: click.Context, level: str | None) -> None:
    """List all sensitivity classifications, optionally filtered by LEVEL."""
    vault = _load_vault(ctx)
    if level:
        keys = list_by_level(vault, level)
        if not keys:
            click.echo(f"No secrets classified as '{level}'.")
        else:
            for k in keys:
                click.echo(f"{k}: {level}")
    else:
        data = list_all(vault)
        if not data:
            click.echo("No sensitivity classifications defined.")
        else:
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
