"""CLI commands for secret flagging."""

from __future__ import annotations

import click

from envault.flagging import (
    VALID_FLAGS,
    add_flag,
    clear_flags,
    get_flags,
    has_flag,
    list_flagged,
    remove_flag,
)


@click.group("flag", help="Manage status flags on secrets.")
def flag_group() -> None:  # pragma: no cover
    pass


@flag_group.command("add")
@click.argument("key")
@click.argument("flag", type=click.Choice(sorted(VALID_FLAGS)))
@click.pass_obj
def add_flag_cmd(vault, key: str, flag: str) -> None:
    """Add FLAG to secret KEY."""
    try:
        add_flag(vault, key, flag)
        click.echo(f"Flag '{flag}' added to '{key}'.")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@flag_group.command("remove")
@click.argument("key")
@click.argument("flag", type=click.Choice(sorted(VALID_FLAGS)))
@click.pass_obj
def remove_flag_cmd(vault, key: str, flag: str) -> None:
    """Remove FLAG from secret KEY."""
    removed = remove_flag(vault, key, flag)
    if removed:
        click.echo(f"Flag '{flag}' removed from '{key}'.")
    else:
        click.echo(f"Flag '{flag}' was not set on '{key}'.")


@flag_group.command("show")
@click.argument("key")
@click.pass_obj
def show_flags_cmd(vault, key: str) -> None:
    """Show all flags on secret KEY."""
    flags = get_flags(vault, key)
    if flags:
        click.echo(f"{key}: {', '.join(sorted(flags))}")
    else:
        click.echo(f"No flags set on '{key}'.")


@flag_group.command("list")
@click.option("--flag", default=None, type=click.Choice(sorted(VALID_FLAGS)), help="Filter by flag.")
@click.pass_obj
def list_flagged_cmd(vault, flag) -> None:
    """List all flagged secrets, optionally filtered by FLAG."""
    results = list_flagged(vault, flag)
    if not results:
        click.echo("No flagged secrets found.")
        return
    for key, flags in sorted(results.items()):
        click.echo(f"{key}: {', '.join(sorted(flags))}")


@flag_group.command("clear")
@click.argument("key")
@click.pass_obj
def clear_flags_cmd(vault, key: str) -> None:
    """Clear all flags from secret KEY."""
    clear_flags(vault, key)
    click.echo(f"All flags cleared from '{key}'.")
