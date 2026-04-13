# Namespace Support

Namespaces let you group related secrets under a logical prefix, making
large vaults easier to navigate and manage.

## Concepts

- A **namespace** is a simple string label (no `/` characters allowed).
- Each secret key can belong to **at most one** namespace.
- Namespaces are stored inside the vault itself (under the reserved key
  `__namespaces__`), so they are encrypted along with your secrets.

## CLI Usage

### Assign a key to a namespace

```bash
envault namespace assign DB_PASSWORD database
envault namespace assign DB_USER database
envault namespace assign STRIPE_SECRET payments
```

### Show the namespace for a key

```bash
envault namespace show DB_PASSWORD
# DB_PASSWORD -> database
```

### List all namespaces and their keys

```bash
envault namespace list
# [database]
#   DB_PASSWORD
#   DB_USER
# [payments]
#   STRIPE_SECRET
```

### Filter by a specific namespace

```bash
envault namespace list --namespace database
#   DB_PASSWORD
#   DB_USER
```

### Remove a namespace assignment

```bash
envault namespace remove DB_PASSWORD
# Namespace assignment removed for 'DB_PASSWORD'.
```

## Python API

```python
from envault.namespace import (
    assign_namespace,
    remove_namespace,
    get_namespace,
    list_namespaces,
    keys_in_namespace,
    qualified_name,
)

assign_namespace(vault, "DB_PASS", "database")
print(get_namespace(vault, "DB_PASS"))       # "database"
print(keys_in_namespace(vault, "database"))  # ["DB_PASS"]
print(qualified_name("DB_PASS", "database")) # "database/DB_PASS"
```

## Notes

- Namespace names may **not** contain `/`.
- Deleting a secret does not automatically remove its namespace assignment;
  call `remove_namespace` explicitly if needed.
- The reserved key `__namespaces__` should not be used for regular secrets.
