"""CLI commands for managing notification subscriptions."""

from __future__ import annotations

import click

from envault.notify import (
    SUPPORTED_EVENTS,
    dispatch,
    get_subscribers,
    list_subscriptions,
    subscribe,
    unsubscribe,
)
from envault.vault import Vault
from envault.cli import _get_passphrase


@click.group("notify")
def notify_group():
    """Manage notification subscriptions for vault events."""


@notify_group.command("subscribe")
@click.argument("event", type=click.Choice(sorted(SUPPORTED_EVENTS)))
@click.argument("channel")
@click.option("--vault-path", default=".envault", show_default=True)
def subscribe_cmd(event, channel, vault_path):
    """Subscribe CHANNEL to EVENT notifications."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    subscribe(vault, event, channel)
    click.echo(f"Subscribed '{channel}' to '{event}' notifications.")


@notify_group.command("unsubscribe")
@click.argument("event", type=click.Choice(sorted(SUPPORTED_EVENTS)))
@click.argument("channel")
@click.option("--vault-path", default=".envault", show_default=True)
def unsubscribe_cmd(event, channel, vault_path):
    """Unsubscribe CHANNEL from EVENT notifications."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    removed = unsubscribe(vault, event, channel)
    if removed:
        click.echo(f"Unsubscribed '{channel}' from '{event}'.")
    else:
        click.echo(f"'{channel}' was not subscribed to '{event}'.")


@notify_group.command("list")
@click.option("--event", type=click.Choice(sorted(SUPPORTED_EVENTS)), default=None)
@click.option("--vault-path", default=".envault", show_default=True)
def list_subscriptions_cmd(event, vault_path):
    """List all notification subscriptions, optionally filtered by EVENT."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    if event:
        subs = {event: get_subscribers(vault, event)}
    else:
        subs = list_subscriptions(vault)
    if not any(subs.values()):
        click.echo("No subscriptions configured.")
        return
    for ev, channels in sorted(subs.items()):
        for ch in channels:
            click.echo(f"{ev}: {ch}")


@notify_group.command("dispatch")
@click.argument("event", type=click.Choice(sorted(SUPPORTED_EVENTS)))
@click.option("--vault-path", default=".envault", show_default=True)
def dispatch_cmd(event, vault_path):
    """Manually dispatch a test notification for EVENT."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    notified = dispatch(vault, event)
    if notified:
        click.echo(f"Dispatched '{event}' to: {', '.join(notified)}")
    else:
        click.echo(f"No subscribers for '{event}'.")
