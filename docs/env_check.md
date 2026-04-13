# env-check

The `check` command group lets you validate that a set of required secrets are
present **and non-empty** in the vault before deploying or running an
application.

## Commands

### `envault check run [KEYS]... [--file FILE]`

Verify one or more secrets by name.  Exit code is `0` on success and `1` if
any secret is missing or empty.

```bash
# Check individual keys
envault check run DB_URL API_KEY JWT_SECRET

# Check keys listed in a file
envault check run --file required-secrets.txt

# Combine both
envault check run EXTRA_KEY --file required-secrets.txt

# Suppress the ✔ lines, only show failures
envault check run --quiet --file required-secrets.txt
```

**Keys file format** (`required-secrets.txt`):
```
# Database
DB_URL
DB_PASSWORD

# Auth
JWT_SECRET
API_KEY
```
Lines starting with `#` and blank lines are ignored.

### `envault check list-missing [KEYS]...`

Print only the keys that are absent or empty, one per line.  Useful for
scripting:

```bash
missing=$(envault check list-missing DB_URL API_KEY)
if [ -n "$missing" ]; then
  echo "Missing secrets: $missing"
  exit 1
fi
```

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | All required secrets are present and non-empty |
| `1`  | One or more secrets are missing or empty |

## Python API

```python
from envault.env_check import check_secrets, check_from_file

report = check_secrets(vault, ["DB_URL", "API_KEY"], passphrase)
if not report.passed:
    print("Missing:", report.missing)
    print("Empty  :", report.empty)
```
