"""CLI commands for secret pinning."""

from __future__ import annotations

import click

from envault.pin import pin_secret, unpin_secret, is_pinned, list_pins, pin_info


@click.group("pin")
def pin_group():
    """Pin secrets to prevent accidental rotation."""


@pin_group.command("add")
@click.argument("key")
@click.option("--reason", "-r", default="", help="Why this secret is pinned.")
@click.pass_obj
def add_pin_cmd(vault, key: str, reason: str):
    """Pin KEY, optionally recording a REASON."""
    if is_pinned(vault, key):
        click.echo(f"Secret '{key}' is already pinned.")
        return
    pin_secret(vault, key, reason)
    msg = f"Pinned '{key}'."
    if reason:
        msg += f" Reason: {reason}"
    click.echo(msg)


@pin_group.command("remove")
@click.argument("key")
@click.pass_obj
def remove_pin_cmd(vault, key: str):
    """Unpin KEY."""
    if unpin_secret(vault, key):
        click.echo(f"Unpinned '{key}'.")
    else:
        click.echo(f"Secret '{key}' was not pinned.", err=True)


@pin_group.command("list")
@click.pass_obj
def list_pins_cmd(vault):
    """List all pinned secrets."""
    pins = list_pins(vault)
    if not pins:
        click.echo("No secrets are currently pinned.")
        return
    for entry in pins:
        reason_part = f"  # {entry['reason']}" if entry["reason"] else ""
        click.echo(f"  {entry['key']}{reason_part}")


@pin_group.command("show")
@click.argument("key")
@click.pass_obj
def show_pin_cmd(vault, key: str):
    """Show pin details for KEY."""
    info = pin_info(vault, key)
    if info is None:
        click.echo(f"Secret '{key}' is not pinned.")
        return
    click.echo(f"Key   : {info['key']}")
    click.echo(f"Reason: {info['reason'] or '(none)'}")
