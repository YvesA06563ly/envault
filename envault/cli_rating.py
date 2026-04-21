"""CLI commands for the secret quality rating feature."""

from __future__ import annotations

import click

from envault.rating import rate_secret, get_rating, list_ratings, clear_rating


@click.group("rating")
def rating_group() -> None:
    """Score secrets by quality and strength."""


@rating_group.command("score")
@click.argument("key")
@click.argument("value")
@click.pass_context
def score_cmd(ctx: click.Context, key: str, value: str) -> None:
    """Rate the quality of VALUE for KEY and store the result."""
    vault = ctx.obj["vault"]
    result = rate_secret(vault, key, value)
    click.echo(f"Key   : {result.key}")
    click.echo(f"Score : {result.score}/100")
    click.echo(f"Grade : {result.grade}")
    if result.reasons:
        click.echo("Issues:")
        for reason in result.reasons:
            click.echo(f"  - {reason}")
    else:
        click.echo("Issues: none — excellent secret!")


@rating_group.command("show")
@click.argument("key")
@click.pass_context
def show_cmd(ctx: click.Context, key: str) -> None:
    """Show the stored rating for KEY."""
    vault = ctx.obj["vault"]
    result = get_rating(vault, key)
    if result is None:
        click.echo(f"No rating found for '{key}'.")
        raise SystemExit(1)
    click.echo(f"Key   : {result.key}")
    click.echo(f"Score : {result.score}/100  Grade: {result.grade}")
    if result.reasons:
        for reason in result.reasons:
            click.echo(f"  - {reason}")


@rating_group.command("list")
@click.option("--failing", is_flag=True, help="Show only secrets with grade F.")
@click.pass_context
def list_cmd(ctx: click.Context, failing: bool) -> None:
    """List all stored ratings."""
    vault = ctx.obj["vault"]
    results = list_ratings(vault)
    if failing:
        results = [r for r in results if r.grade == "F"]
    if not results:
        click.echo("No ratings stored.")
        return
    click.echo(f"{'KEY':<30} {'SCORE':>5}  {'GRADE'}")
    click.echo("-" * 42)
    for r in results:
        click.echo(f"{r.key:<30} {r.score:>5}  {r.grade}")


@rating_group.command("clear")
@click.argument("key")
@click.pass_context
def clear_cmd(ctx: click.Context, key: str) -> None:
    """Remove the stored rating for KEY."""
    vault = ctx.obj["vault"]
    removed = clear_rating(vault, key)
    if removed:
        click.echo(f"Rating for '{key}' cleared.")
    else:
        click.echo(f"No rating found for '{key}'.")
