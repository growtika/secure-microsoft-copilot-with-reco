# Step 2: Pass the Copilot Posture Checks

## Overview

These six posture checks validate the configurations that most directly shape Copilot exposure. If any check fails, enabling Copilot can expand the impact of existing access gaps, risky identities, or unmanaged device usage by making discoverable content easier to find and summarize.

## Navigation

**Reco Console:** `AI Governance → AI Posture Checks`

## The Six Posture Checks

### 1. Conditional Access Policies

Verify that Conditional Access policies are configured to control who can access Copilot and under what conditions.

**Severity:** HIGH

**What to validate:**
- MFA is required for Copilot access
- Unmanaged devices are blocked or limited
- Location-based restrictions are enforced

### 2. Data Loss Prevention (DLP) Policies

Ensure DLP policies cover Copilot-generated content and prevent sensitive data from being surfaced or exported.

**Severity:** HIGH

**What to validate:**
- DLP policies apply to Copilot interactions
- Sensitive information types are detected in AI-generated responses
- Blocking actions are configured for high-sensitivity content

### 3. Sensitivity Labels

Confirm that sensitivity labels are deployed and enforced across the content that Copilot can access.

**Severity:** HIGH

**What to validate:**
- Labels are applied to all high-value content
- Auto-labeling policies are active
- Label-based access restrictions are enforced

### 4. External Sharing Controls

Validate that external sharing settings prevent Copilot from surfacing content shared with external parties.

**Severity:** MEDIUM

**What to validate:**
- Guest access policies are reviewed
- External sharing is scoped to approved domains
- Anonymous sharing links are disabled or limited

### 5. Device Compliance

Ensure that only compliant devices can access Copilot-enabled services.

**Severity:** MEDIUM

**What to validate:**
- Device compliance policies are enforced
- Non-compliant devices are blocked from Copilot
- Mobile device management (MDM) is configured

### 6. Audit Logging

Verify that audit logging captures Copilot interactions for investigation and compliance.

**Severity:** MEDIUM

**What to validate:**
- Unified Audit Log is enabled
- Copilot-specific events are captured
- Log retention meets compliance requirements

## Compliance Mappings

Each posture check aligns with established frameworks:

| Posture Check | CIS M365 Benchmark v5.0 | ISO 27001:2022 |
|--------------|--------------------------|----------------|
| Conditional Access | 5.2.2, 5.2.3 | A.8.3, A.8.5 |
| DLP Policies | 3.1.1, 3.2.1 | A.8.10, A.8.12 |
| Sensitivity Labels | 3.3.1 | A.5.12, A.5.13 |
| External Sharing | 7.2.3, 7.2.6 | A.5.14, A.8.3 |
| Device Compliance | 5.1.2 | A.8.1 |
| Audit Logging | 8.5.1 | A.8.15 |

## Gate Rule

> **Action:** Do not expand Copilot access until all HIGH severity checks pass. MEDIUM severity checks should be addressed before proceeding to broad production rollout.

## Next Step

→ [Step 3: Block High-Risk Users](step-3-block-high-risk-users.md)
