# Watermark

The **watermark** feature lets you attach provenance metadata to secrets stored in envault. A watermark records the *author* who last attested a secret, an optional *note*, and a short *fingerprint* derived from the secret's key, value, and author.

## How it works

When you set a watermark, envault computes a 16-character SHA-256 fingerprint from the combination of the secret key, its current value, and the author name. This fingerprint is stored alongside the author and note inside the vault (under a reserved metadata key).

Later, you can **verify** the watermark: envault re-derives the fingerprint and compares it to the stored one. If the secret value has been changed without updating the watermark, verification will fail.

## CLI usage

### Attach a watermark

```bash
envault watermark set DB_PASSWORD alice --note "approved for prod"
```

### Show a watermark

```bash
envault watermark show DB_PASSWORD
```

Output:
```
Key:         DB_PASSWORD
Author:      alice
Fingerprint: 3f9a1c2d4e5b6a7f
Note:        approved for prod
```

### Verify a watermark

```bash
envault watermark verify DB_PASSWORD
```

Returns exit code `0` on success, `1` on failure.

### Remove a watermark

```bash
envault watermark remove DB_PASSWORD
```

### List all watermarked secrets

```bash
envault watermark list
```

## Python API

```python
from envault.watermark import set_watermark, verify_watermark, get_watermark

mark = set_watermark(vault, "DB_PASSWORD", author="alice", note="approved")
print(mark["fingerprint"])

if verify_watermark(vault, "DB_PASSWORD"):
    print("Provenance intact")
```

## Notes

- Watermarks are stored as vault metadata, encrypted alongside your secrets.
- Changing a secret's value without updating the watermark will cause `verify` to fail.
- Watermarks are advisory — they do not prevent writes.
