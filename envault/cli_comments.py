"""CLI commands for managing per-secret comments."""

from __future__ import annotations

import click

from envault.comments import (
    get_comment,
    keys_with_comments,
    list_comments,
    remove_comment,
    set_comment,
)


@click.group(name="comment")
def comment_group():
    """Manage comments/annotations attached to secrets."""


@comment_group.command("set")
@click.argument("key")
@click.argument("comment")
@click.pass_context
def set_comment_cmd(ctx, key: str, comment: str):
    """Attach COMMENT to the secret KEY."""
    vault = ctx.obj["vault"]
    set_comment(vault, key, comment)
    click.echo(f"Comment set for '{key}'.")


@comment_group.command("remove")
@click.argument("key")
@click.pass_context
def remove_comment_cmd(ctx, key: str):
    """Remove the comment attached to KEY."""
    vault = ctx.obj["vault"]
    removed = remove_comment(vault, key)
    if removed:
        click.echo(f"Comment removed for '{key}'.")
    else:
        click.echo(f"No comment found for '{key}'.")


@comment_group.command("show")
@click.argument("key")
@click.pass_context
def show_comment_cmd(ctx, key: str):
    """Show the comment for KEY."""
    vault = ctx.obj["vault"]
    comment = get_comment(vault, key)
    if comment is None:
        click.echo(f"No comment for '{key}'.")
    else:
        click.echo(f"{key}: {comment}")


@comment_group.command("list")
@click.pass_context
def list_comments_cmd(ctx):
    """List all keys that have comments."""
    vault = ctx.obj["vault"]
    comments = list_comments(vault)
    if not comments:
        click.echo("No comments found.")
        return
    for k in sorted(comments):
        click.echo(f"{k}: {comments[k]}")
