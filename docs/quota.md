# Quota Management

The **quota** feature lets you cap the number of secrets allowed per scope (e.g. namespace, environment, or any arbitrary label). This helps enforce governance policies and prevents accidental secret sprawl.

## Concepts

- **Scope** — an arbitrary string key (e.g. `production`, `dev`, `team-backend`).
- **Limit** — the maximum number of secrets permitted within that scope.
- Quotas are stored inside the vault under a reserved metadata key and are therefore encrypted at rest along with all other data.

## CLI Usage

### Set a quota

```bash
envault quota set <scope> <limit>
```

Example:

```bash
envault quota set production 100
```

### Show a quota

```bash
envault quota show <scope>
```

### Remove a quota

```bash
envault quota remove <scope>
```

### List all quotas

```bash
envault quota list
```

### Check whether a count is within quota

```bash
envault quota check <scope> <count>
```

Exits with code `1` if the count meets or exceeds the limit, making it suitable for use in CI pipelines.

## Python API

```python
from envault.quota import set_quota, get_quota, check_quota, list_quotas, remove_quota

# Define a limit
set_quota(vault, "production", 100)

# Query
print(get_quota(vault, "production"))  # 100

# Enforce before adding a new secret
if not check_quota(vault, "production", current_count):
    raise RuntimeError("Quota exceeded for production")

# List everything
for scope, limit in list_quotas(vault).items():
    print(f"{scope}: {limit}")
```

## Notes

- Limits must be positive integers; passing `0` or a negative value raises a `ValueError`.
- If no quota is defined for a scope, `check_quota` always returns `True` (unrestricted).
- Quotas are independent of namespaces but can mirror them for fine-grained control.
