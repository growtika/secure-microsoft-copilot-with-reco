# Step 4: Detect Risky AI Usage

[← Step 3](step-3-block-high-risk-users.md) | [Back to Overview](../README.md) | [Step 5 →](step-5-monitor-scope-drift.md)

## Overview

Once Copilot is live, you need continuous visibility into how it's being used. Bulk data access, sensitive content surfacing, anomalous patterns, and cross-boundary probes should trigger alerts.

## Deployment Strategy

**Phase 1 — Preview (Pilot):** Policies generate alerts for review only. No production routing. Use this phase to understand normal patterns and build a baseline.

**Phase 2 — Production:** Full alert routing to SOC/SIEM. Automated response workflows active.

## What to Detect

| Policy | Severity | What It Catches |
|--------|----------|-----------------|
| Bulk Data Access | High | User accesses 50+ files via Copilot in 1 hour |
| Sensitive Content Surfacing | High | Copilot response references Confidential/Highly Confidential files |
| Anomalous Usage | Medium | Query volume exceeds p95 baseline, off-hours usage, new topic categories |
| Cross-Boundary Access | Critical | Guest user attempts cross-tenant data discovery |
| Data Exfiltration | Critical | High copy-paste volume + external share attempt |
| Departing Employee Usage | High | User in departure workflow uses Copilot |

See [`policies/detection-policies.yaml`](../policies/detection-policies.yaml) for the full policy definitions.

## Alert SLAs

| Severity | Response Time |
|----------|--------------|
| Critical | 15 minutes |
| High | 4 hours |
| Medium | 24 hours |
| Low | Weekly review batch |

## Alert Response Flow

```
Alert Triggered
     │
     ▼
┌─────────────┐
│  Severity?  │
└─────────────┘
     │
     ├── Critical → Immediate SOC review, auto-block if configured
     ├── High → Review within 4 hours
     ├── Medium → Review within 24 hours
     └── Low → Weekly review batch
```

## Next Step

→ [Step 5: Monitor Permission Scope Drift](step-5-monitor-scope-drift.md)
