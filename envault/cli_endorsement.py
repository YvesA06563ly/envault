"""CLI commands for the endorsement feature."""

from __future__ import annotations

import click

from envault import endorsement as endr
from envault.vault import Vault
from envault.cli import _get_passphrase


@click.group("endorse")
def endorse_group() -> None:
    """Manage secret endorsements."""


def _load_vault() -> Vault:
    passphrase = _get_passphrase()
    v = Vault()
    v.load(passphrase)
    return v


@endorse_group.command("add")
@click.argument("key")
@click.argument("user")
def add_endorsement_cmd(key: str, user: str) -> None:
    """Endorse KEY as verified by USER."""
    v = _load_vault()
    endr.endorse(v, key, user)
    click.echo(f"✓ {user} endorsed '{key}'.")


@endorse_group.command("revoke")
@click.argument("key")
@click.argument("user")
def revoke_endorsement_cmd(key: str, user: str) -> None:
    """Remove USER's endorsement from KEY."""
    v = _load_vault()
    removed = endr.revoke_endorsement(v, key, user)
    if removed:
        click.echo(f"✓ Removed endorsement of '{key}' by {user}.")
    else:
        click.echo(f"No endorsement by {user} found for '{key}'.")


@endorse_group.command("show")
@click.argument("key")
def show_endorsements_cmd(key: str) -> None:
    """Show all endorsers for KEY."""
    v = _load_vault()
    endorsers = endr.get_endorsers(v, key)
    if not endorsers:
        click.echo(f"No endorsements for '{key}'.")
    else:
        click.echo(f"Endorsers for '{key}' ({len(endorsers)}):")
        for u in endorsers:
            click.echo(f"  - {u}")


@endorse_group.command("list")
def list_endorsed_cmd() -> None:
    """List all secrets with at least one endorsement."""
    v = _load_vault()
    endorsed = endr.list_endorsed(v)
    if not endorsed:
        click.echo("No endorsed secrets.")
    else:
        for key, users in endorsed.items():
            click.echo(f"{key}: {', '.join(users)}")
