# Endorsement

The **endorsement** feature allows team members to mark secrets as verified or trusted by adding their identity as an endorser.

## Concepts

- A **secret** can be endorsed by one or more **users**.
- Endorsements are stored inside the vault under a reserved metadata key.
- Endorsements are additive and idempotent — endorsing the same secret twice has no effect.

## CLI Usage

### Endorse a secret

```bash
envault endorse add DB_PASSWORD alice
```

### Revoke an endorsement

```bash
envault endorse revoke DB_PASSWORD alice
```

### Show endorsers for a secret

```bash
envault endorse show DB_PASSWORD
```

Example output:

```
Endorsers for 'DB_PASSWORD' (2):
  - alice
  - bob
```

### List all endorsed secrets

```bash
envault endorse list
```

Example output:

```
DB_PASSWORD: alice, bob
API_KEY: carol
```

## Python API

```python
from envault.endorsement import endorse, revoke_endorsement, get_endorsers, is_endorsed_by, endorsement_count, list_endorsed

# Add endorsement
endorse(vault, "API_KEY", "alice")

# Check endorsement
is_endorsed_by(vault, "API_KEY", "alice")  # True

# Count endorsers
endorsement_count(vault, "API_KEY")  # 1

# List all endorsers
get_endorsers(vault, "API_KEY")  # ["alice"]

# Revoke
revoke_endorsement(vault, "API_KEY", "alice")

# List all endorsed secrets
list_endorsed(vault)  # {"DB_PASS": ["bob"]}
```

## Notes

- Endorser lists are stored sorted alphabetically.
- Revoking the last endorser removes the secret's endorsement record entirely.
- Endorsements do not affect secret values or encryption.
