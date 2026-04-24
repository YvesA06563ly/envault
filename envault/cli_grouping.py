"""CLI commands for secret grouping."""

from __future__ import annotations

import click

from envault.grouping import (
    assign_group,
    remove_from_group,
    list_groups,
    members_of,
    groups_of,
    delete_group,
)


@click.group("group", help="Organise secrets into named groups.")
def group_group() -> None:  # pragma: no cover
    pass


@group_group.command("assign")
@click.argument("key")
@click.argument("group")
@click.pass_obj
def assign_cmd(vault, key: str, group: str) -> None:
    """Assign KEY to GROUP."""
    assign_group(vault, key, group)
    click.echo(f"Assigned '{key}' to group '{group}'.")


@group_group.command("remove")
@click.argument("key")
@click.argument("group")
@click.pass_obj
def remove_cmd(vault, key: str, group: str) -> None:
    """Remove KEY from GROUP."""
    if remove_from_group(vault, key, group):
        click.echo(f"Removed '{key}' from group '{group}'.")
    else:
        click.echo(f"'{key}' was not in group '{group}'.")


@group_group.command("list")
@click.pass_obj
def list_cmd(vault) -> None:
    """List all groups."""
    groups = list_groups(vault)
    if not groups:
        click.echo("No groups defined.")
        return
    for g in groups:
        click.echo(g)


@group_group.command("members")
@click.argument("group")
@click.pass_obj
def members_cmd(vault, group: str) -> None:
    """Show all secrets in GROUP."""
    members = members_of(vault, group)
    if not members:
        click.echo(f"Group '{group}' is empty or does not exist.")
        return
    for m in members:
        click.echo(m)


@group_group.command("show")
@click.argument("key")
@click.pass_obj
def show_cmd(vault, key: str) -> None:
    """Show all groups that KEY belongs to."""
    groups = groups_of(vault, key)
    if not groups:
        click.echo(f"'{key}' does not belong to any group.")
        return
    for g in groups:
        click.echo(g)


@group_group.command("delete")
@click.argument("group")
@click.pass_obj
def delete_cmd(vault, group: str) -> None:
    """Delete an entire GROUP."""
    if delete_group(vault, group):
        click.echo(f"Deleted group '{group}'.")
    else:
        click.echo(f"Group '{group}' does not exist.")
