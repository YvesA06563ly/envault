# Snapshot Feature

The `snapshot` module lets you capture the current state of selected secrets and restore them later. This is useful before bulk rotations or risky deployments.

## CLI Usage

### Create a snapshot

```bash
envault snapshot create <name> KEY1 KEY2 ...
```

Captures the current values of the listed keys into a named snapshot stored inside the vault.

**Example:**
```bash
envault snapshot create pre-deploy DB_URL API_KEY SECRET_TOKEN
# Snapshot 'pre-deploy' created at 2024-01-15T10:00:00+00:00 with 3 key(s).
```

### List snapshots

```bash
envault snapshot list
```

Displays all snapshots with their creation time and captured keys.

### Restore a snapshot

```bash
envault snapshot restore <name>
```

Writes the stored secret values back into the vault, overwriting current values.

**Example:**
```bash
envault snapshot restore pre-deploy
# Restored 3 key(s) from snapshot 'pre-deploy': DB_URL, API_KEY, SECRET_TOKEN
```

### Delete a snapshot

```bash
envault snapshot delete <name>
```

Permanently removes the named snapshot.

## Python API

```python
from envault.vault import Vault
from envault import snapshot

vault = Vault(passphrase)

# Create
entry = snapshot.create_snapshot(vault, "v1", ["DB_URL", "API_KEY"])

# List
all_snaps = snapshot.list_snapshots(vault)

# Restore
restored_keys = snapshot.restore_snapshot(vault, "v1")

# Delete
snapshot.delete_snapshot(vault, "v1")
```

## Notes

- Snapshots are stored encrypted inside the vault under the reserved key `__snapshots__`.
- Snapshot names are arbitrary strings; creating a snapshot with an existing name overwrites it.
- Only keys that exist at snapshot time are captured; missing keys are silently skipped.
