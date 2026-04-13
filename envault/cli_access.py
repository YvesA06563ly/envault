"""CLI commands for managing per-secret access control."""

from __future__ import annotations

import click

from envault.access import grant, revoke, can, list_permissions, list_profile_grants
from envault.cli import _get_passphrase
from envault.vault import Vault


@click.group("access", help="Manage per-secret access permissions.")
def access_group() -> None:
    pass


@access_group.command("grant")
@click.argument("secret_key")
@click.argument("profile")
@click.argument("permission", type=click.Choice(["read", "write"]))
def grant_cmd(secret_key: str, profile: str, permission: str) -> None:
    """Grant PROFILE the PERMISSION ('read'|'write') on SECRET_KEY."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase=passphrase)
    vault.load()
    grant(vault, secret_key, profile, permission)
    click.echo(f"Granted '{permission}' on '{secret_key}' to profile '{profile}'.")


@access_group.command("revoke")
@click.argument("secret_key")
@click.argument("profile")
@click.argument("permission", type=click.Choice(["read", "write"]))
def revoke_cmd(secret_key: str, profile: str, permission: str) -> None:
    """Revoke PROFILE's PERMISSION on SECRET_KEY."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase=passphrase)
    vault.load()
    revoke(vault, secret_key, profile, permission)
    click.echo(f"Revoked '{permission}' on '{secret_key}' from profile '{profile}'.")


@access_group.command("check")
@click.argument("secret_key")
@click.argument("profile")
@click.argument("permission", type=click.Choice(["read", "write"]))
def check_cmd(secret_key: str, profile: str, permission: str) -> None:
    """Check whether PROFILE holds PERMISSION on SECRET_KEY."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase=passphrase)
    vault.load()
    result = can(vault, secret_key, profile, permission)
    status = "ALLOWED" if result else "DENIED"
    click.echo(f"{profile} -> {permission} on '{secret_key}': {status}")


@access_group.command("show")
@click.argument("secret_key")
def show_cmd(secret_key: str) -> None:
    """Show all permissions configured for SECRET_KEY."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase=passphrase)
    vault.load()
    perms = list_permissions(vault, secret_key)
    if perms is None:
        click.echo(f"No access rules configured for '{secret_key}'.")
        return
    for perm, profiles in perms.items():
        if profiles:
            click.echo(f"  {perm}: {', '.join(profiles)}")


@access_group.command("profile")
@click.argument("profile")
def profile_cmd(profile: str) -> None:
    """List all secrets and permissions accessible by PROFILE."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase=passphrase)
    vault.load()
    grants = list_profile_grants(vault, profile)
    if not grants:
        click.echo(f"No grants found for profile '{profile}'.")
        return
    for key, perms in sorted(grants.items()):
        click.echo(f"  {key}: {', '.join(perms)}")
