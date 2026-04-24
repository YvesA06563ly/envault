"""CLI commands for compliance framework management."""

from __future__ import annotations

import click

from envault.compliance import (
    assign_framework,
    remove_framework,
    get_frameworks,
    list_by_framework,
    compliance_report,
    _KNOWN_FRAMEWORKS,
)
from envault.vault import Vault


def _load_vault(ctx) -> Vault:
    return ctx.obj["vault"]


@click.group("compliance")
def compliance_group():
    """Manage compliance framework tags for secrets."""


@compliance_group.command("assign")
@click.argument("key")
@click.argument("framework")
@click.pass_context
def assign_cmd(ctx, key: str, framework: str):
    """Assign FRAMEWORK to KEY."""
    vault = _load_vault(ctx)
    try:
        assign_framework(vault, key, framework)
        click.echo(f"Assigned '{framework}' to '{key}'.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@compliance_group.command("remove")
@click.argument("key")
@click.argument("framework")
@click.pass_context
def remove_cmd(ctx, key: str, framework: str):
    """Remove FRAMEWORK from KEY."""
    vault = _load_vault(ctx)
    remove_framework(vault, key, framework)
    click.echo(f"Removed '{framework}' from '{key}'.")


@compliance_group.command("show")
@click.argument("key")
@click.pass_context
def show_cmd(ctx, key: str):
    """Show frameworks assigned to KEY."""
    vault = _load_vault(ctx)
    frameworks = get_frameworks(vault, key)
    if frameworks:
        click.echo(", ".join(frameworks))
    else:
        click.echo(f"No frameworks assigned to '{key}'.")


@compliance_group.command("list")
@click.argument("framework")
@click.pass_context
def list_cmd(ctx, framework: str):
    """List secrets tagged with FRAMEWORK."""
    vault = _load_vault(ctx)
    keys = list_by_framework(vault, framework)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No secrets tagged with '{framework}'.")


@compliance_group.command("report")
@click.argument("framework")
@click.pass_context
def report_cmd(ctx, framework: str):
    """Coverage report for FRAMEWORK across all vault secrets."""
    vault = _load_vault(ctx)
    all_keys = [k for k in (vault.load() or {}).keys() if not k.startswith("__")]
    report = compliance_report(vault, framework, all_keys)
    click.echo(f"Framework : {report.framework}")
    click.echo(f"Coverage  : {report.coverage_pct}% ({len(report.covered)}/{len(report.covered)+len(report.uncovered)})")
    if report.uncovered:
        click.echo("Uncovered : " + ", ".join(report.uncovered))
