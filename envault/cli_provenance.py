"""CLI commands for provenance tracking."""

from __future__ import annotations

import click

from envault.provenance import (
    clear_provenance,
    get_provenance,
    has_provenance,
    list_provenance,
    set_provenance,
)
from envault.vault import Vault


def _load_vault(ctx: click.Context) -> Vault:
    vault_path = ctx.obj.get("vault_path", ".envault")
    passphrase = ctx.obj.get("passphrase", "")
    v = Vault(vault_path, passphrase)
    v.load()
    return v


@click.group("provenance")
def provenance_group() -> None:
    """Manage secret provenance (origin tracking)."""


@provenance_group.command("set")
@click.argument("key")
@click.argument("source")
@click.option("--author", default=None, help="Author or owner of the secret.")
@click.option("--note", default=None, help="Optional free-text note.")
@click.pass_context
def set_provenance_cmd(
    ctx: click.Context, key: str, source: str, author: str | None, note: str | None
) -> None:
    """Record provenance for KEY with SOURCE."""
    vault = _load_vault(ctx)
    set_provenance(vault, key, source, author=author, note=note)
    click.echo(f"Provenance recorded for '{key}'.")


@provenance_group.command("show")
@click.argument("key")
@click.pass_context
def show_provenance_cmd(ctx: click.Context, key: str) -> None:
    """Show provenance for KEY."""
    vault = _load_vault(ctx)
    record = get_provenance(vault, key)
    if record is None:
        click.echo(f"No provenance recorded for '{key}'.")
        return
    click.echo(f"Key:         {key}")
    click.echo(f"Source:      {record['source']}")
    click.echo(f"Author:      {record.get('author') or '—'}")
    click.echo(f"Note:        {record.get('note') or '—'}")
    click.echo(f"Recorded at: {record.get('recorded_at')}")


@provenance_group.command("clear")
@click.argument("key")
@click.pass_context
def clear_provenance_cmd(ctx: click.Context, key: str) -> None:
    """Remove provenance record for KEY."""
    vault = _load_vault(ctx)
    if not has_provenance(vault, key):
        click.echo(f"No provenance found for '{key}'.")
        return
    clear_provenance(vault, key)
    click.echo(f"Provenance cleared for '{key}'.")


@provenance_group.command("list")
@click.pass_context
def list_provenance_cmd(ctx: click.Context) -> None:
    """List all secrets with recorded provenance."""
    vault = _load_vault(ctx)
    records = list_provenance(vault)
    if not records:
        click.echo("No provenance records found.")
        return
    for key, rec in sorted(records.items()):
        click.echo(f"{key}  source={rec['source']}  author={rec.get('author') or '—'}")
