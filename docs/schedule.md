# Rotation Schedules

envault supports automatic rotation scheduling so you can track which secrets are due for rotation based on a configurable interval.

## Commands

### Set a schedule

```bash
envault schedule set <KEY> <INTERVAL_DAYS> [--notify]
```

Schedules `KEY` to be rotated every `INTERVAL_DAYS` days. Use `--notify` to flag that notification channels should be alerted when the key becomes due.

**Example:**
```bash
envault schedule set DB_PASSWORD 30 --notify
```

### Remove a schedule

```bash
envault schedule remove <KEY>
```

Removes the rotation schedule for the given key.

### List all schedules

```bash
envault schedule list
```

Displays all keys with active rotation schedules, their intervals, and creation timestamps.

### Check due keys

```bash
envault schedule due
```

Lists all keys whose rotation interval has elapsed since their last recorded rotation. Keys with no rotation history are always considered due.

## How it works

Schedule metadata is stored as a JSON blob inside the vault under a reserved key. The `due` command compares the current time against the last rotation timestamp (recorded by `envault rotate`) and the configured interval.

## Integration with rotation

Schedules work alongside `envault.rotation` — the `last_rotated` function is used to determine when a key was last rotated. Run `envault rotate <KEY>` to update the rotation timestamp and reset the schedule countdown.

## Notes

- Interval must be at least 1 day.
- Schedules persist across vault sessions.
- Notifications are advisory; actual dispatch depends on configured notify channels.
