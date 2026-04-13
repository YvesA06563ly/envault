# Notification Subscriptions

Envault supports subscribing external channels (webhooks, email addresses, Slack URLs, etc.) to vault events so your team is alerted when important changes occur.

## Supported Events

| Event      | Triggered when …                              |
|------------|-----------------------------------------------|
| `rotation` | A secret is rotated                           |
| `expiry`   | A secret is nearing or past its expiry date   |
| `access`   | An ACL check or grant/revoke occurs           |
| `import`   | Secrets are bulk-imported                     |
| `delete`   | A secret is removed from the vault            |

## CLI Usage

### Subscribe a channel

```bash
envault notify subscribe rotation https://hooks.example.com/my-webhook
envault notify subscribe expiry admin@example.com
```

### Unsubscribe a channel

```bash
envault notify unsubscribe rotation https://hooks.example.com/my-webhook
```

### List all subscriptions

```bash
envault notify list
```

Filter by event:

```bash
envault notify list --event expiry
```

### Manually dispatch a test notification

```bash
envault notify dispatch rotation
```

This is useful for verifying that your webhook endpoint is reachable.

## Programmatic API

```python
from envault.notify import subscribe, unsubscribe, dispatch, list_subscriptions

subscribe(vault, "rotation", "https://hooks.example.com/1")
dispatch(vault, "rotation", payload={"key": "DB_PASSWORD"})
print(list_subscriptions(vault))
```

## Notes

- Subscriptions are stored inside the vault (encrypted at rest).
- The `dispatch` function currently logs notified channels; wire it to your HTTP client or email library for real delivery.
- Multiple channels can subscribe to the same event.
