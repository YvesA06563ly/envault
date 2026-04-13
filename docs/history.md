# Secret Value History

envault automatically tracks a history of value changes for each secret,
allowing you to audit when a secret was rotated and what its previous values
were (stored encrypted inside the vault).

## How it works

Every time `record_history()` is called (e.g. when a secret is set or rotated),
an entry is appended containing:

- `value` – the **new** value
- `previous` – the value that was replaced (`null` for the first entry)
- `timestamp` – ISO-8601 UTC timestamp

At most **20** entries are retained per key (oldest are pruned automatically).

## CLI commands

### Show history for a key

```bash
envault history show DB_PASSWORD
```

Outputs a numbered list of entries with timestamps and the previous value at
each rotation.

### List all keys with history

```bash
envault history list
```

### Clear history for a key

```bash
envault history clear DB_PASSWORD
```

You will be prompted to confirm before history is deleted.

## Python API

```python
from envault.history import record_history, get_history, clear_history, list_keys_with_history

# Record a change
record_history(vault, "DB_PASSWORD", old_value="old", new_value="new")

# Retrieve history (oldest first)
entries = get_history(vault, "DB_PASSWORD")
for entry in entries:
    print(entry["timestamp"], entry["value"])

# Remove history
clear_history(vault, "DB_PASSWORD")

# Which keys have history?
keys = list_keys_with_history(vault)
```

## Storage

History data is stored under the reserved key `__history__` inside the vault
file, encrypted alongside all other secrets.
