# Workflows

Workflows let you define named sequences of operations on vault secrets and execute them in one command.

## Concepts

A **workflow** is a named list of *steps*. Each step has:

| Field | Required | Description |
|-------|----------|-------------|
| `action` | yes | `set` or `delete` |
| `key` | yes | Secret key name |
| `value` | for `set` | Value to assign |

## CLI Usage

### Create a workflow

```bash
envault workflow create deploy \
  --steps '[{"action":"set","key":"ENV","value":"production"},{"action":"set","key":"DEBUG","value":"false"}]'
```

### List workflows

```bash
envault workflow list
```

### Show workflow steps

```bash
envault workflow show deploy
```

### Run a workflow

```bash
envault workflow run deploy
```

Output:
```
  [ok] set ENV
  [ok] set DEBUG
Workflow 'deploy' completed (2 step(s)).
```

### Delete a workflow

```bash
envault workflow delete deploy
```

## Storage

Workflows are stored inside the vault under the reserved key `__workflows__` as an encrypted JSON blob, so they benefit from the same passphrase protection as your secrets.

## Notes

- Workflow names must be non-empty strings.
- A workflow must contain at least one step.
- Unknown actions are recorded with status `unknown_action` and do not abort the run.
