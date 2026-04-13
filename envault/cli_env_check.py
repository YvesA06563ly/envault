"""cli_env_check.py — CLI commands for the env-check feature."""

from __future__ import annotations

import sys
import click

from envault.env_check import check_secrets, check_from_file


@click.group("check")
def check_group() -> None:
    """Validate that required secrets exist in the vault."""


@check_group.command("run")
@click.argument("keys", nargs=-1, required=False)
@click.option("--file", "-f", "keys_file", default=None,
              help="File with one required key per line (# comments ok).")
@click.option("--quiet", "-q", is_flag=True, help="Only print failures.")
@click.pass_context
def run_check_cmd(ctx: click.Context, keys, keys_file, quiet) -> None:
    """Check that KEYS (and/or keys from --file) are present and non-empty."""
    vault = ctx.obj["vault"]
    passphrase = ctx.obj["passphrase"]

    if not keys and not keys_file:
        raise click.UsageError("Provide KEY arguments and/or --file.")

    required = list(keys)

    if keys_file:
        try:
            report = check_from_file(vault, keys_file, passphrase)
            # merge with any explicit keys
            if required:
                from envault.env_check import check_secrets
                extra = check_secrets(vault, required, passphrase)
                report.results = extra.results + report.results
        except FileNotFoundError:
            raise click.ClickException(f"Keys file not found: {keys_file}")
    else:
        report = check_secrets(vault, required, passphrase)

    any_failure = False
    for r in report.results:
        if r.present and r.non_empty:
            if not quiet:
                click.echo(click.style(f"  ✔  {r.key}", fg="green"))
        else:
            any_failure = True
            click.echo(click.style(f"  ✘  {r.message}", fg="red"))

    if any_failure:
        sys.exit(1)
    elif not quiet:
        click.echo(click.style("All checks passed.", fg="green", bold=True))


@check_group.command("list-missing")
@click.argument("keys", nargs=-1, required=True)
@click.pass_context
def list_missing_cmd(ctx: click.Context, keys) -> None:
    """Print only the keys that are missing or empty."""
    vault = ctx.obj["vault"]
    passphrase = ctx.obj["passphrase"]
    report = check_secrets(vault, list(keys), passphrase)
    problems = report.missing + report.empty
    if problems:
        for k in problems:
            click.echo(k)
        sys.exit(1)
