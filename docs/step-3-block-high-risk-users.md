# Step 3: Block High-Risk Users

[← Step 2](step-2-posture-checks.md) | [Back to Overview](../README.md) | [Step 4 →](step-4-detect-risky-ai-usage.md)

## Overview

Not every identity in your tenant should have Copilot access. Users with elevated risk — departing employees, compromised accounts, over-privileged admins, unmanaged external identities — should be blocked before Copilot expands the reach of their existing access.

## High-Risk User Categories

| Category | Why It Matters |
|----------|---------------|
| **Departing employees** | Could rapidly surface and collect sensitive data before access is terminated |
| **Elevated risk identities** | Flagged by Entra ID Protection — may be compromised |
| **Over-privileged accounts** | Admin/service accounts with excessive permissions that Copilot amplifies |
| **External identities** | Guest/B2B accounts that accumulated broader access than intended |

## Conditional Access Policy

Create a CA policy in Entra ID that blocks Copilot for high-risk users. See [`scripts/conditional_access_policy.json`](../scripts/conditional_access_policy.json) for a ready-to-import template.

The policy should:
- Target a dynamic security group containing high-risk users
- Scope to the Microsoft 365 Copilot application
- Include `userRiskLevels: ["high"]` condition
- Set `grantControls` to `block`

## Dynamic Risk Labels

Group membership should update automatically based on:
- **Entra ID Protection** — sign-in risk and user risk signals
- **HR lifecycle events** — onboarding, role change, departure
- **Behavioral analytics** — anomalous access patterns

## Identity Risk Decision Tree

See [`diagrams/identity-risk-decision-tree.mmd`](../diagrams/identity-risk-decision-tree.mmd) for the full decision flow.

## Action Items

- [ ] Identify all users with elevated risk scores in Entra ID
- [ ] Create a dynamic security group for high-risk users
- [ ] Import the Conditional Access policy template
- [ ] Validate enforcement
- [ ] Set up automated group membership updates based on risk signals

## Next Step

→ [Step 4: Detect Risky AI Usage](step-4-detect-risky-ai-usage.md)
