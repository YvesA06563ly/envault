"""CLI commands for snapshot management."""

from __future__ import annotations

import click

from envault.cli import _get_passphrase
from envault.vault import Vault
from envault import snapshot as snap


@click.group("snapshot")
def snapshot_group() -> None:
    """Manage vault snapshots."""


@snapshot_group.command("create")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
def create_snapshot_cmd(name: str, keys: tuple[str, ...]) -> None:
    """Create a snapshot NAME capturing the given KEYS."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    entry = snap.create_snapshot(vault, name, list(keys))
    click.echo(f"Snapshot '{name}' created at {entry['created_at']} with {len(entry['secrets'])} key(s).")


@snapshot_group.command("restore")
@click.argument("name")
def restore_snapshot_cmd(name: str) -> None:
    """Restore secrets from snapshot NAME."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    try:
        restored = snap.restore_snapshot(vault, name)
        click.echo(f"Restored {len(restored)} key(s) from snapshot '{name}': {', '.join(restored)}")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@snapshot_group.command("list")
def list_snapshots_cmd() -> None:
    """List all available snapshots."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    entries = snap.list_snapshots(vault)
    if not entries:
        click.echo("No snapshots found.")
        return
    for entry in entries:
        keys_str = ", ".join(entry["keys"]) if entry["keys"] else "(empty)"
        click.echo(f"{entry['name']}  [{entry['created_at']}]  keys: {keys_str}")


@snapshot_group.command("delete")
@click.argument("name")
def delete_snapshot_cmd(name: str) -> None:
    """Delete snapshot NAME."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    try:
        snap.delete_snapshot(vault, name)
        click.echo(f"Snapshot '{name}' deleted.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
