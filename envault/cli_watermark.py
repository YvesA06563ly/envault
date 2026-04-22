"""CLI commands for the watermark feature."""

from __future__ import annotations

import click

from envault.vault import Vault
from envault.cli import _get_passphrase
from envault.watermark import (
    set_watermark,
    get_watermark,
    remove_watermark,
    verify_watermark,
    list_watermarks,
)


@click.group("watermark", help="Manage secret provenance watermarks.")
def watermark_group() -> None:
    pass


@watermark_group.command("set")
@click.argument("key")
@click.argument("author")
@click.option("--note", default="", help="Optional provenance note.")
def set_watermark_cmd(key: str, author: str, note: str) -> None:
    """Attach a watermark to KEY identifying AUTHOR."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    mark = set_watermark(vault, key, author, note)
    click.echo(f"Watermark set for '{key}' (fingerprint: {mark['fingerprint']}).")


@watermark_group.command("show")
@click.argument("key")
def show_watermark_cmd(key: str) -> None:
    """Show the watermark for KEY."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    mark = get_watermark(vault, key)
    if not mark:
        click.echo(f"No watermark found for '{key}'.")
        return
    click.echo(f"Key:         {key}")
    click.echo(f"Author:      {mark['author']}")
    click.echo(f"Fingerprint: {mark['fingerprint']}")
    if mark.get("note"):
        click.echo(f"Note:        {mark['note']}")


@watermark_group.command("verify")
@click.argument("key")
def verify_watermark_cmd(key: str) -> None:
    """Verify the watermark fingerprint for KEY."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    if verify_watermark(vault, key):
        click.echo(f"✓ Watermark for '{key}' is valid.")
    else:
        click.echo(f"✗ Watermark for '{key}' is INVALID or missing.", err=True)
        raise SystemExit(1)


@watermark_group.command("remove")
@click.argument("key")
def remove_watermark_cmd(key: str) -> None:
    """Remove the watermark for KEY."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    if remove_watermark(vault, key):
        click.echo(f"Watermark removed for '{key}'.")
    else:
        click.echo(f"No watermark found for '{key}'.")


@watermark_group.command("list")
def list_watermarks_cmd() -> None:
    """List all watermarked secrets."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    marks = list_watermarks(vault)
    if not marks:
        click.echo("No watermarks recorded.")
        return
    for m in marks:
        note_part = f"  [{m['note']}]" if m.get("note") else ""
        click.echo(f"{m['key']:30s}  {m['author']:20s}  {m['fingerprint']}{note_part}")
