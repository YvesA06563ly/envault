# Secret Comments

envault lets you attach human-readable comments or annotations to any secret key. Comments are stored encrypted inside the vault alongside your secrets.

## Commands

### Set a comment

```bash
envault comment set DB_PASSWORD "Primary PostgreSQL password — rotated monthly"
```

### Show the comment for a key

```bash
envault comment show DB_PASSWORD
# DB_PASSWORD: Primary PostgreSQL password — rotated monthly
```

### Remove a comment

```bash
envault comment remove DB_PASSWORD
# Comment removed for 'DB_PASSWORD'.
```

### List all annotated keys

```bash
envault comment list
# API_KEY: Third-party payment gateway key
# DB_PASSWORD: Primary PostgreSQL password — rotated monthly
# JWT_SECRET: Signing secret for user sessions
```

## Programmatic API

```python
from envault.comments import set_comment, get_comment, remove_comment, list_comments

# Attach a comment
set_comment(vault, "API_KEY", "Payment gateway — rotate every 90 days")

# Retrieve it
note = get_comment(vault, "API_KEY")

# Remove it
remove_comment(vault, "API_KEY")

# Get all comments as a dict
all_comments = list_comments(vault)
```

## Notes

- Comments are stored under the reserved key `__comments__` as a JSON blob.
- Deleting a secret does **not** automatically delete its comment; use `comment remove` explicitly.
- Comments are included in vault snapshots and exports where the raw vault data is preserved.
