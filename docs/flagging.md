# Secret Flagging

Envault supports attaching **status flags** to secrets to communicate their health, review state, or operational concerns.

## Available Flags

| Flag | Meaning |
|------|--------|
| `suspicious` | The secret value looks unusual or may be compromised |
| `stale` | The secret hasn't been rotated in a long time |
| `reviewed` | A human has reviewed and approved this secret |
| `deprecated` | The secret is no longer actively used |
| `needs-rotation` | The secret should be rotated at the next opportunity |

## CLI Usage

### Add a flag

```bash
envault flag add DB_PASSWORD suspicious
```

### Remove a flag

```bash
envault flag remove DB_PASSWORD suspicious
```

### Show flags on a secret

```bash
envault flag show DB_PASSWORD
# DB_PASSWORD: suspicious, stale
```

### List all flagged secrets

```bash
envault flag list
```

### Filter by flag

```bash
envault flag list --flag stale
```

### Clear all flags from a secret

```bash
envault flag clear DB_PASSWORD
```

## Python API

```python
from envault.flagging import add_flag, remove_flag, get_flags, has_flag, list_flagged, clear_flags

# Add a flag
add_flag(vault, "DB_PASSWORD", "stale")

# Check a flag
if has_flag(vault, "DB_PASSWORD", "stale"):
    print("Secret is stale!")

# List all flags on a secret
flags = get_flags(vault, "DB_PASSWORD")

# Find all secrets with a given flag
stale_secrets = list_flagged(vault, flag="stale")

# Remove a specific flag
remove_flag(vault, "DB_PASSWORD", "stale")

# Clear all flags
clear_flags(vault, "DB_PASSWORD")
```

## Notes

- Flags are stored inside the vault under a reserved metadata key.
- Adding the same flag twice is idempotent.
- Flags are validated against the known set; unknown flags raise a `ValueError`.
