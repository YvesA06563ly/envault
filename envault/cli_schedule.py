"""CLI commands for managing rotation schedules."""
import click
from envault.vault import Vault
from envault.cli import _get_passphrase
from envault import schedule as sched
from envault.rotation import last_rotated


@click.group("schedule")
def schedule_group():
    """Manage automatic rotation schedules."""


@schedule_group.command("set")
@click.argument("key")
@click.argument("interval_days", type=int)
@click.option("--notify", is_flag=True, default=False, help="Trigger notifications when due.")
def set_schedule_cmd(key, interval_days, notify):
    """Schedule KEY to rotate every INTERVAL_DAYS days."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    try:
        sched.set_schedule(vault, key, interval_days, notify=notify)
        click.echo(f"Schedule set: '{key}' every {interval_days} day(s).")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@schedule_group.command("remove")
@click.argument("key")
def remove_schedule_cmd(key):
    """Remove the rotation schedule for KEY."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    removed = sched.remove_schedule(vault, key)
    if removed:
        click.echo(f"Schedule removed for '{key}'.")
    else:
        click.echo(f"No schedule found for '{key}'.")


@schedule_group.command("list")
def list_schedules_cmd():
    """List all scheduled rotation keys."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    schedules = sched.list_schedules(vault)
    if not schedules:
        click.echo("No schedules configured.")
        return
    for key, cfg in schedules.items():
        notify_flag = " [notify]" if cfg.get("notify") else ""
        click.echo(f"{key}: every {cfg['interval_days']} day(s){notify_flag} (since {cfg['created_at']})")


@schedule_group.command("due")
def due_cmd():
    """List keys whose scheduled rotation is due."""
    passphrase = _get_passphrase()
    vault = Vault(passphrase)
    due = sched.due_keys(vault, lambda k: last_rotated(vault, k))
    if not due:
        click.echo("No keys are due for rotation.")
    else:
        click.echo("Keys due for rotation:")
        for key in due:
            click.echo(f"  {key}")
