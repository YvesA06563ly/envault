"""CLI commands for namespace management."""

from __future__ import annotations

import click

from envault.cli import _get_passphrase
from envault.vault import Vault
from envault import namespace as ns_mod


@click.group("namespace")
def namespace_group():
    """Manage secret namespaces."""


def _load_vault(vault_path: str) -> Vault:
    """Prompt for passphrase, load and return the vault at *vault_path*."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    return vault


@namespace_group.command("assign")
@click.argument("key")
@click.argument("namespace")
@click.option("--vault-path", default=".envault", show_default=True)
def assign_cmd(key: str, namespace: str, vault_path: str):
    """Assign KEY to NAMESPACE."""
    vault = _load_vault(vault_path)
    try:
        ns_mod.assign_namespace(vault, key, namespace)
        click.echo(f"Assigned '{key}' to namespace '{namespace}'.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@namespace_group.command("remove")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def remove_cmd(key: str, vault_path: str):
    """Remove namespace assignment for KEY."""
    vault = _load_vault(vault_path)
    removed = ns_mod.remove_namespace(vault, key)
    if removed:
        click.echo(f"Namespace assignment removed for '{key}'.")
    else:
        click.echo(f"'{key}' had no namespace assignment.")


@namespace_group.command("show")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
def show_cmd(key: str, vault_path: str):
    """Show namespace for KEY."""
    vault = _load_vault(vault_path)
    ns = ns_mod.get_namespace(vault, key)
    if ns:
        click.echo(f"{key} -> {ns}")
    else:
        click.echo(f"'{key}' is not assigned to any namespace.")


@namespace_group.command("list")
@click.option("--namespace", default=None, help="Filter by namespace.")
@click.option("--vault-path", default=".envault", show_default=True)
def list_cmd(namespace: str, vault_path: str):
    """List namespaces and their keys."""
    vault = _load_vault(vault_path)
    if namespace:
        keys = ns_mod.keys_in_namespace(vault, namespace)
        if keys:
            for k in keys:
                click.echo(f"  {k}")
        else:
            click.echo(f"No keys in namespace '{namespace}'.")
    else:
        mapping = ns_mod.list_namespaces(vault)
        if not mapping:
            click.echo("No namespaces defined.")
        for ns_name, keys in sorted(mapping.items()):
            click.echo(f"[{ns_name}]")
            for k in keys:
                click.echo(f"  {k}")
