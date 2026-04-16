"""CLI commands for managing workflows."""
import json
import click
from envault.vault import Vault
from envault.cli import _get_passphrase
import envault.workflow as wf_mod


@click.group("workflow")
def workflow_group():
    """Manage named workflows."""


@workflow_group.command("create")
@click.argument("name")
@click.option("--steps", required=True, help="JSON array of step objects.")
@click.option("--vault-path", default=".envault", show_default=True)
def create_workflow_cmd(name, steps, vault_path):
    """Create a named workflow from a JSON steps array."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    try:
        parsed = json.loads(steps)
    except json.JSONDecodeError as exc:
        raise click.BadParameter(f"Invalid JSON: {exc}") from exc
    wf_mod.create_workflow(vault, name, parsed)
    click.echo(f"Workflow '{name}' created with {len(parsed)} step(s).")


@workflow_group.command("delete")
@click.argument("name")
@click.option("--vault-path", default=".envault", show_default=True)
def delete_workflow_cmd(name, vault_path):
    """Delete a named workflow."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    removed = wf_mod.delete_workflow(vault, name)
    if removed:
        click.echo(f"Workflow '{name}' deleted.")
    else:
        click.echo(f"Workflow '{name}' not found.", err=True)


@workflow_group.command("list")
@click.option("--vault-path", default=".envault", show_default=True)
def list_workflows_cmd(vault_path):
    """List all workflows."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    names = wf_mod.list_workflows(vault)
    if names:
        for n in names:
            click.echo(n)
    else:
        click.echo("No workflows defined.")


@workflow_group.command("show")
@click.argument("name")
@click.option("--vault-path", default=".envault", show_default=True)
def show_workflow_cmd(name, vault_path):
    """Show steps of a workflow."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    data = wf_mod.get_workflow(vault, name)
    if data is None:
        click.echo(f"Workflow '{name}' not found.", err=True)
        return
    click.echo(json.dumps(data["steps"], indent=2))


@workflow_group.command("run")
@click.argument("name")
@click.option("--vault-path", default=".envault", show_default=True)
def run_workflow_cmd(name, vault_path):
    """Run a named workflow."""
    passphrase = _get_passphrase()
    vault = Vault(vault_path, passphrase)
    vault.load()
    try:
        results = wf_mod.run_workflow(vault, name)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        return
    for r in results:
        click.echo(f"  [{r['status']}] {r['action']} {r['key']}")
    click.echo(f"Workflow '{name}' completed ({len(results)} step(s)).")
