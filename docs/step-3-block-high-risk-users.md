# Step 3: Block High-Risk Users

## Overview

Not every identity in your tenant should have access to Copilot. Users with elevated risk based on role, behavioral signals, or account status can significantly increase exposure when generative AI is enabled. Identify and restrict these users before Copilot expands the reach of their existing access.

## Navigation

**Reco Console:** `Identities → Users`

## High-Risk User Categories

### 1. Departing Employees

Users in offboarding or departure workflows should not retain Copilot access. A departing employee with Copilot could rapidly surface and collect sensitive information before their access is terminated.

### 2. Elevated Risk Identities

Users flagged by Microsoft Entra ID Protection with elevated sign-in or user risk signals. These accounts may be compromised or exhibiting anomalous behavior.

### 3. Over-Privileged Accounts

Service accounts, admin accounts, or users with excessive permissions that were never scoped down. Copilot amplifies whatever access these identities already have.

### 4. External Identities

Guest users and B2B collaboration accounts that may have accumulated broader access than intended over time.

## Conditional Access Policy Configuration

Create a Conditional Access policy in Microsoft Entra ID that blocks Microsoft 365 Copilot for high-risk users:

```json
{
  "displayName": "Block Copilot for High-Risk Users",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeGroups": [
        "high-risk-users-group-id",
        "departing-employees-group-id"
      ]
    },
    "applications": {
      "includeApplications": [
        "Microsoft 365 Copilot"
      ]
    },
    "userRiskLevels": [
      "high"
    ]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": [
      "block"
    ]
  }
}
```

## Dynamic Risk Labels

These labels can update based on:
- **Identity risk signals** from Microsoft Entra ID Protection
- **HR-driven lifecycle events** (onboarding, role change, departure)
- **Behavioral analytics** from Reco's identity monitoring

> If a user is flagged as elevated risk or in a departure workflow, they should not retain Copilot access by default.

## Action Items

- [ ] Identify all users with elevated risk scores in Entra ID
- [ ] Create a dynamic security group for high-risk users
- [ ] Create the Conditional Access policy blocking Copilot for this group
- [ ] Confirm the control is enforced
- [ ] Validate that Copilot posture checks reflect the requirement as passing
- [ ] Set up automated group membership updates based on risk signals

## Next Step

→ [Step 4: Detect Risky AI Usage](step-4-detect-risky-ai-usage.md)
