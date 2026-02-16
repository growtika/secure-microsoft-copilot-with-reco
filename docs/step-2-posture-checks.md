# Step 2: Pass the Copilot Posture Checks

[← Step 1](step-1-fix-permission-debt.md) | [Back to Overview](../README.md) | [Step 3 →](step-3-block-high-risk-users.md)

## Overview

Six posture checks validate the configurations that most directly shape Copilot exposure. If any HIGH check fails, do not enable Copilot.

See [`scripts/posture_check_validator.py`](../scripts/posture_check_validator.py) for the full check definitions with compliance mappings and remediation steps.

## The Six Checks

| # | Check | Severity | What to Validate |
|---|-------|----------|-----------------|
| 1 | **Conditional Access** | HIGH | MFA required, unmanaged devices blocked, location restrictions enforced |
| 2 | **DLP Policies** | HIGH | DLP covers Copilot interactions, sensitive info types detected, blocking actions configured |
| 3 | **Sensitivity Labels** | HIGH | Labels on all high-value content, auto-labeling active, label-based restrictions enforced |
| 4 | **External Sharing** | MEDIUM | Guest access reviewed, sharing scoped to approved domains, anonymous links disabled |
| 5 | **Device Compliance** | MEDIUM | Compliance policies enforced, non-compliant devices blocked, MDM configured |
| 6 | **Audit Logging** | MEDIUM | Unified Audit Log enabled, Copilot events captured, retention meets requirements |

## Compliance Mappings

| Check | CIS M365 v5.0 | ISO 27001:2022 |
|-------|---------------|----------------|
| Conditional Access | 5.2.2, 5.2.3 | A.8.3, A.8.5 |
| DLP Policies | 3.1.1, 3.2.1 | A.8.10, A.8.12 |
| Sensitivity Labels | 3.3.1 | A.5.12, A.5.13 |
| External Sharing | 7.2.3, 7.2.6 | A.5.14, A.8.3 |
| Device Compliance | 5.1.2 | A.8.1 |
| Audit Logging | 8.5.1 | A.8.15 |

## Gate Rule

> All HIGH checks pass → cleared for pilot.
> All MEDIUM checks pass → cleared for production rollout.

## Where to Validate

| Check | Admin Path |
|-------|-----------|
| Conditional Access | Microsoft Entra ID → Security → Conditional Access |
| DLP Policies | Microsoft Purview → Data Loss Prevention → Policies |
| Sensitivity Labels | Microsoft Purview → Information Protection → Labels |
| External Sharing | SharePoint Admin Center → Policies → Sharing |
| Device Compliance | Microsoft Intune → Devices → Compliance policies |
| Audit Logging | Microsoft Purview → Audit → Audit retention policies |

## Next Step

→ [Step 3: Block High-Risk Users](step-3-block-high-risk-users.md)
