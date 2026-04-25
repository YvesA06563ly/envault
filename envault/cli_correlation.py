"""CLI commands for secret correlation."""
import click

from envault.correlation import link, unlink, get_correlates, clear_correlates, list_all
from envault.vault import Vault
from envault.cli import _get_passphrase


@click.group(name="correlate")
def correlation_group():
    """Manage correlations between secrets."""


def _load_vault() -> Vault:
    passphrase = _get_passphrase()
    v = Vault()
    v.load(passphrase)
    return v


@correlation_group.command("link")
@click.argument("key")
@click.argument("related")
def link_cmd(key: str, related: str):
    """Link KEY and RELATED as correlated secrets."""
    v = _load_vault()
    try:
        link(v, key, related)
        click.echo(f"Linked '{key}' <-> '{related}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@correlation_group.command("unlink")
@click.argument("key")
@click.argument("related")
def unlink_cmd(key: str, related: str):
    """Remove correlation between KEY and RELATED."""
    v = _load_vault()
    removed = unlink(v, key, related)
    if removed:
        click.echo(f"Unlinked '{key}' <-> '{related}'.")
    else:
        click.echo(f"No correlation found between '{key}' and '{related}'.")


@correlation_group.command("show")
@click.argument("key")
def show_cmd(key: str):
    """Show all secrets correlated with KEY."""
    v = _load_vault()
    peers = get_correlates(v, key)
    if not peers:
        click.echo(f"No correlations for '{key}'.")
    else:
        click.echo(f"Correlates of '{key}':")
        for p in peers:
            click.echo(f"  - {p}")


@correlation_group.command("clear")
@click.argument("key")
def clear_cmd(key: str):
    """Remove all correlations for KEY."""
    v = _load_vault()
    clear_correlates(v, key)
    click.echo(f"Cleared all correlations for '{key}'.")


@correlation_group.command("list")
def list_cmd():
    """List all correlations in the vault."""
    v = _load_vault()
    data = list_all(v)
    if not data:
        click.echo("No correlations defined.")
        return
    for key, peers in sorted(data.items()):
        click.echo(f"{key}: {', '.join(peers)}")
