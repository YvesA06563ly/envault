"""CLI commands for quota management."""

import click
from envault.quota import (
    set_quota,
    remove_quota,
    get_quota,
    list_quotas,
    check_quota,
)


@click.group(name="quota", help="Manage secret quotas per scope.")
def quota_group():
    pass


@quota_group.command("set")
@click.argument("scope")
@click.argument("limit", type=int)
@click.pass_context
def set_quota_cmd(ctx, scope: str, limit: int):
    """Set the maximum number of secrets for SCOPE."""
    vault = ctx.obj["vault"]
    set_quota(vault, scope, limit)
    click.echo(f"Quota for '{scope}' set to {limit}.")


@quota_group.command("remove")
@click.argument("scope")
@click.pass_context
def remove_quota_cmd(ctx, scope: str):
    """Remove the quota for SCOPE."""
    vault = ctx.obj["vault"]
    removed = remove_quota(vault, scope)
    if removed:
        click.echo(f"Quota for '{scope}' removed.")
    else:
        click.echo(f"No quota found for '{scope}'.")


@quota_group.command("show")
@click.argument("scope")
@click.pass_context
def show_quota_cmd(ctx, scope: str):
    """Show the quota for SCOPE."""
    vault = ctx.obj["vault"]
    limit = get_quota(vault, scope)
    if limit is None:
        click.echo(f"No quota set for '{scope}'.")
    else:
        click.echo(f"Quota for '{scope}': {limit}")


@quota_group.command("list")
@click.pass_context
def list_quotas_cmd(ctx):
    """List all quotas."""
    vault = ctx.obj["vault"]
    quotas = list_quotas(vault)
    if not quotas:
        click.echo("No quotas defined.")
        return
    for scope, limit in sorted(quotas.items()):
        click.echo(f"  {scope}: {limit}")


@quota_group.command("check")
@click.argument("scope")
@click.argument("count", type=int)
@click.pass_context
def check_quota_cmd(ctx, scope: str, count: int):
    """Check if COUNT secrets are within the quota for SCOPE."""
    vault = ctx.obj["vault"]
    ok = check_quota(vault, scope, count)
    if ok:
        click.echo(f"OK: {count} secrets is within the quota for '{scope}'.")
    else:
        click.echo(f"EXCEEDED: {count} secrets exceeds the quota for '{scope}'.")
        ctx.exit(1)
