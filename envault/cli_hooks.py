"""CLI commands for managing pre/post rotation hooks."""
from __future__ import annotations

import click

from envault.hooks import set_hook, remove_hook, list_hooks
from envault.vault import Vault
from envault.cli import _get_passphrase


@click.group("hooks")
def hooks_group() -> None:
    """Manage pre/post rotation hooks for secrets."""


@hooks_group.command("set")
@click.argument("key")
@click.argument("stage", type=click.Choice(["pre", "post"]))
@click.argument("command")
@click.option("--vault-path", default=".envault", show_default=True)
def set_hook_cmd(key: str, stage: str, command: str, vault_path: str) -> None:
    """Register a hook COMMAND for KEY at STAGE (pre or post rotation)."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    set_hook(vault, key, stage, command)
    click.echo(f"Hook set: [{stage}] {key} -> {command}")


@hooks_group.command("remove")
@click.argument("key")
@click.argument("stage", type=click.Choice(["pre", "post"]))
@click.option("--vault-path", default=".envault", show_default=True)
def remove_hook_cmd(key: str, stage: str, vault_path: str) -> None:
    """Remove the hook for KEY at STAGE."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    removed = remove_hook(vault, key, stage)
    if removed:
        click.echo(f"Hook removed: [{stage}] {key}")
    else:
        click.echo(f"No {stage} hook found for {key!r}.")


@hooks_group.command("list")
@click.option("--vault-path", default=".envault", show_default=True)
def list_hooks_cmd(vault_path: str) -> None:
    """List all registered hooks."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    hooks = list_hooks(vault)
    if not hooks:
        click.echo("No hooks registered.")
        return
    for key, stages in sorted(hooks.items()):
        for stage, command in sorted(stages.items()):
            click.echo(f"  {key}  [{stage}]  {command}")
