"""CLI commands for managing per-secret notes."""

from __future__ import annotations

import click

from envault import notes as notes_mod
from envault.cli import _get_passphrase
from envault.vault import Vault


@click.group("notes")
def notes_group():
    """Manage rich text notes attached to secrets."""


@notes_group.command("set")
@click.argument("key")
@click.argument("text")
@click.option("--vault-path", default=".envault", show_default=True)
def set_note_cmd(key: str, text: str, vault_path: str):
    """Attach a note to KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    notes_mod.set_note(vault, key, text)
    click.echo(f"Note set for '{key}'.")


@notes_group.command("remove")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def remove_note_cmd(key: str, vault_path: str):
    """Remove the note attached to KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    removed = notes_mod.remove_note(vault, key)
    if removed:
        click.echo(f"Note removed for '{key}'.")
    else:
        click.echo(f"No note found for '{key}'.")


@notes_group.command("show")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def show_note_cmd(key: str, vault_path: str):
    """Show the note attached to KEY."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    text = notes_mod.get_note(vault, key)
    if text is None:
        click.echo(f"No note for '{key}'.")
    else:
        click.echo(text)


@notes_group.command("list")
@click.option("--vault-path", default=".envault", show_default=True)
def list_notes_cmd(vault_path: str):
    """List all secrets that have notes."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    all_notes = notes_mod.list_notes(vault)
    if not all_notes:
        click.echo("No notes recorded.")
        return
    for key, text in sorted(all_notes.items()):
        preview = text.splitlines()[0][:60]
        click.echo(f"{key}: {preview}")
