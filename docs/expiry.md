# Secret Expiry

envault lets you attach an expiry date to any secret so you can track
rotation deadlines and catch stale credentials before they become a problem.

## Setting an expiry

```bash
envault expiry set DB_PASSWORD 90
# DB_PASSWORD expires at 2025-10-14T12:00:00+00:00
```

The second argument is the number of **days** from now until the secret expires.

## Checking a single secret

```bash
envault expiry show DB_PASSWORD
# DB_PASSWORD: 2025-10-14T12:00:00+00:00 [valid]
```

If the secret has passed its expiry date the status shows `EXPIRED`.

## Listing expiring secrets

```bash
envault expiry list --within 30
```

Prints every secret that expires within the next 30 days (default 7),
sorted soonest-first.  Expired secrets are flagged `[EXPIRED]`.

## Clearing an expiry

```bash
envault expiry clear DB_PASSWORD
# Expiry cleared for 'DB_PASSWORD'.
```

## Python API

```python
from envault.expiry import set_expiry, get_expiry, is_expired, list_expiring

set_expiry(vault, "API_KEY", days=60)

expiry_dt = get_expiry(vault, "API_KEY")   # datetime | None
expired   = is_expired(vault, "API_KEY")   # bool
due_soon  = list_expiring(vault, within_days=14)
```

## Integration with rotation

Combine expiry with `envault rotation` to automatically flag secrets that
need rotating:

```bash
# After rotating a secret, reset its expiry window
envault secret set DB_PASSWORD "$NEW_PASS"
envault expiry set DB_PASSWORD 90
```
