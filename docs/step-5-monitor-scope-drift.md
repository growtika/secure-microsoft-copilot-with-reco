# Step 5: Monitor Permission Scope Drift

## Overview

Over time, Copilot's effective access can expand as plugins are connected, integrations evolve, and permission scopes change. What begins as a tightly controlled deployment can drift into broader data access if connected apps and delegated permissions are not reviewed continuously.

## Navigation

**Reco Console:** `AI Governance → Connected AI Apps`

## Understanding Scope Drift

### What Causes Scope Drift

1. **New plugin installations** — Each plugin may request additional OAuth scopes
2. **Integration updates** — Vendors may expand requested permissions in updates
3. **Admin consent grants** — Broad admin consent can silently expand access
4. **Delegated permissions accumulation** — Users granting incremental access over time

### The Scope Donut Chart

The Reco dashboard visualizes permission distribution:

```
        ┌───────────────────┐
        │  Permission Scope │
        │    Distribution   │
        │                   │
        │    ┌─────────┐    │
        │   ╱    Low    ╲   │      🟢 Low Risk Scopes
        │  │  ┌───────┐  │  │      🟡 Medium Risk Scopes
        │  │ │  High  │  │  │      🟠 High Risk Scopes
        │  │ │  Risk  │  │  │      🔴 Critical Risk Scopes
        │  │  └───────┘  │  │
        │   ╲  Medium   ╱   │
        │    └─────────┘    │
        └───────────────────┘
```

- **Red and orange segments** highlight higher risk scopes
- **'High Scopes to Review' count** shows how many permissions exceed expected boundaries
- **Click any app** to view its individual plugins and revoke excessive scopes

## What to Monitor

### Connected App Inventory

| Attribute | What to Check |
|-----------|--------------|
| App Name | Is this an approved application? |
| Publisher | Is the publisher verified and trusted? |
| Scopes Requested | Do scopes match the app's stated function? |
| Consent Type | Admin consent vs. user consent |
| Last Used | Is the app actively in use? |
| Users Count | How many users have consented? |

### Permission Scope Risk Levels

| Risk Level | Example Scopes | Action |
|------------|---------------|--------|
| **Critical** | `Directory.ReadWrite.All`, `Mail.ReadWrite` | Immediate review and justification required |
| **High** | `Files.ReadWrite.All`, `Sites.ReadWrite.All` | Review within 1 week |
| **Medium** | `User.Read.All`, `Group.Read.All` | Quarterly review |
| **Low** | `User.Read`, `profile` | Annual review |

## Remediation Actions

### Revoke Excessive Scopes

When a connected app has more permissions than needed:

1. Navigate to the app details in Reco
2. Review individual plugin permissions
3. Revoke excessive scopes
4. Verify app functionality with reduced permissions
5. Document the change

### Remove Unused Apps

Apps that haven't been used in 90+ days should be reviewed for removal:

1. Identify inactive connected apps
2. Confirm with app owners that the integration is no longer needed
3. Revoke all permissions
4. Remove the app registration if appropriate

## Next Step

→ [Ongoing Governance](ongoing-governance.md)
