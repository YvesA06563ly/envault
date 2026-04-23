"""CLI commands for the secret health-scoring feature."""
from __future__ import annotations

import click

from envault.scoring import score_secret, score_all


@click.group("score")
def scoring_group() -> None:
    """Health-score commands for secrets."""


@scoring_group.command("show")
@click.argument("key")
@click.pass_context
def show_score_cmd(ctx: click.Context, key: str) -> None:
    """Show the health score breakdown for KEY."""
    vault = ctx.obj["vault"]
    bd = score_secret(vault, key)
    click.echo(f"Score for '{key}':")
    click.echo(f"  Rotation  : {bd.rotation:>3} / 30")
    click.echo(f"  Expiry    : {bd.expiry:>3} / 25")
    click.echo(f"  Integrity : {bd.integrity:>3} / 25")
    click.echo(f"  Policy    : {bd.policy:>3} / 20")
    click.echo(f"  ─────────────────")
    click.echo(f"  Total     : {bd.total:>3} / 100")


@scoring_group.command("list")
@click.option("--min-score", default=0, show_default=True, help="Only show secrets at or below this score.")
@click.pass_context
def list_scores_cmd(ctx: click.Context, min_score: int) -> None:
    """List health scores for all secrets, optionally filtered by a maximum score."""
    vault = ctx.obj["vault"]
    scores = score_all(vault)
    if not scores:
        click.echo("No secrets found.")
        return
    rows = sorted(scores.items(), key=lambda kv: kv[1].total)
    header = f"{'KEY':<30} {'SCORE':>5}  BREAKDOWN"
    click.echo(header)
    click.echo("-" * len(header))
    for key, bd in rows:
        if bd.total <= min_score or min_score == 0:
            click.echo(
                f"{key:<30} {bd.total:>5}  "
                f"rot={bd.rotation} exp={bd.expiry} int={bd.integrity} pol={bd.policy}"
            )


@scoring_group.command("summary")
@click.pass_context
def summary_cmd(ctx: click.Context) -> None:
    """Print an overall vault health summary."""
    vault = ctx.obj["vault"]
    scores = score_all(vault)
    if not scores:
        click.echo("No secrets found.")
        return
    totals = [bd.total for bd in scores.values()]
    avg = sum(totals) / len(totals)
    perfect = sum(1 for t in totals if t == 100)
    at_risk = sum(1 for t in totals if t < 50)
    click.echo(f"Secrets evaluated : {len(totals)}")
    click.echo(f"Average score     : {avg:.1f} / 100")
    click.echo(f"Perfect (100)     : {perfect}")
    click.echo(f"At risk (<50)     : {at_risk}")
