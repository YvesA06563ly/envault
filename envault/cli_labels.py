"""CLI commands for label management."""

from __future__ import annotations

import click

from envault.labels import (
    set_label,
    remove_label,
    get_labels,
    find_by_label,
    clear_labels,
)


@click.group("labels")
def labels_group():
    """Manage key=value labels on secrets."""


@labels_group.command("set")
@click.argument("secret_key")
@click.argument("label_key")
@click.argument("label_value")
@click.pass_context
def set_label_cmd(ctx, secret_key, label_key, label_value):
    """Set LABEL_KEY=LABEL_VALUE on SECRET_KEY."""
    vault = ctx.obj["vault"]
    set_label(vault, secret_key, label_key, label_value)
    click.echo(f"Label '{label_key}={label_value}' set on '{secret_key}'.")


@labels_group.command("remove")
@click.argument("secret_key")
@click.argument("label_key")
@click.pass_context
def remove_label_cmd(ctx, secret_key, label_key):
    """Remove LABEL_KEY from SECRET_KEY."""
    vault = ctx.obj["vault"]
    removed = remove_label(vault, secret_key, label_key)
    if removed:
        click.echo(f"Label '{label_key}' removed from '{secret_key}'.")
    else:
        click.echo(f"Label '{label_key}' not found on '{secret_key}'.")


@labels_group.command("show")
@click.argument("secret_key")
@click.pass_context
def show_labels_cmd(ctx, secret_key):
    """Show all labels for SECRET_KEY."""
    vault = ctx.obj["vault"]
    labels = get_labels(vault, secret_key)
    if not labels:
        click.echo(f"No labels for '{secret_key}'.")
    else:
        for k, v in sorted(labels.items()):
            click.echo(f"  {k}={v}")


@labels_group.command("find")
@click.argument("label_key")
@click.argument("label_value", required=False, default=None)
@click.pass_context
def find_by_label_cmd(ctx, label_key, label_value):
    """Find secrets with LABEL_KEY (optionally matching LABEL_VALUE)."""
    vault = ctx.obj["vault"]
    keys = find_by_label(vault, label_key, label_value)
    if not keys:
        click.echo("No secrets found.")
    else:
        for k in keys:
            click.echo(k)


@labels_group.command("clear")
@click.argument("secret_key")
@click.pass_context
def clear_labels_cmd(ctx, secret_key):
    """Remove all labels from SECRET_KEY."""
    vault = ctx.obj["vault"]
    clear_labels(vault, secret_key)
    click.echo(f"All labels cleared from '{secret_key}'.")
