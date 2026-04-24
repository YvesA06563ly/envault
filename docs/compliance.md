# Compliance Framework Tagging

envault supports tagging secrets with regulatory compliance framework labels,
allowing teams to track which secrets fall under specific standards.

## Supported Frameworks

| Key        | Standard                              |
|------------|---------------------------------------|
| `pci-dss`  | Payment Card Industry DSS             |
| `hipaa`    | Health Insurance Portability Act      |
| `soc2`     | SOC 2 Type II                         |
| `gdpr`     | General Data Protection Regulation    |
| `iso27001` | ISO/IEC 27001 Information Security    |

## Commands

### Assign a framework

```bash
envault compliance assign DB_PASSWORD pci-dss
```

### Remove a framework

```bash
envault compliance remove DB_PASSWORD pci-dss
```

### Show frameworks for a secret

```bash
envault compliance show DB_PASSWORD
# pci-dss, soc2
```

### List secrets by framework

```bash
envault compliance list gdpr
# API_KEY
# USER_TOKEN
```

### Generate a coverage report

```bash
envault compliance report hipaa
# Framework : hipaa
# Coverage  : 66.7% (2/3)
# Uncovered : LEGACY_TOKEN
```

## Programmatic API

```python
from envault.compliance import assign_framework, get_frameworks, compliance_report

assign_framework(vault, "DB_PASS", "pci-dss")
frameworks = get_frameworks(vault, "DB_PASS")
report = compliance_report(vault, "pci-dss", all_keys=["DB_PASS", "API_KEY"])
print(report.coverage_pct)  # 50.0
```

## Notes

- Framework names are case-insensitive.
- A secret may be tagged with multiple frameworks.
- The coverage report only considers keys explicitly passed as `all_keys`.
