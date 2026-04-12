"""CLI commands for managing deployment targets in envault."""

from __future__ import annotations

import click

from envault.targets import add_target, get_target, list_targets, remove_target


@click.group("target")
def target_group():
    """Manage deployment targets."""


@target_group.command("add")
@click.argument("name")
@click.argument("url")
@click.option("--description", "-d", default="", help="Human-readable description.")
@click.pass_context
def add_target_cmd(ctx: click.Context, name: str, url: str, description: str) -> None:
    """Register a new deployment target NAME at URL."""
    vault = ctx.obj["vault"]
    try:
        add_target(vault, name, url, description)
        click.echo(f"Target '{name}' added ({url}).")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@target_group.command("remove")
@click.argument("name")
@click.pass_context
def remove_target_cmd(ctx: click.Context, name: str) -> None:
    """Remove a registered deployment target by NAME."""
    vault = ctx.obj["vault"]
    try:
        remove_target(vault, name)
        click.echo(f"Target '{name}' removed.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@target_group.command("list")
@click.pass_context
def list_targets_cmd(ctx: click.Context) -> None:
    """List all registered deployment targets."""
    vault = ctx.obj["vault"]
    targets = list_targets(vault)
    if not targets:
        click.echo("No targets registered.")
        return
    for t in targets:
        desc = f"  # {t['description']}" if t.get("description") else ""
        click.echo(f"  {t['name']:20s}  {t['url']}{desc}")


@target_group.command("show")
@click.argument("name")
@click.pass_context
def show_target_cmd(ctx: click.Context, name: str) -> None:
    """Show details for a single deployment target NAME."""
    vault = ctx.obj["vault"]
    target = get_target(vault, name)
    if target is None:
        raise click.ClickException(f"Target '{name}' not found.")
    click.echo(f"Name       : {target['name']}")
    click.echo(f"URL        : {target['url']}")
    click.echo(f"Description: {target.get('description', '')}")
