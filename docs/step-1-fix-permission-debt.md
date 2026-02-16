# Step 1: Fix Permission Debt First

[← Back to Overview](../README.md) | [Next: Step 2 →](step-2-posture-checks.md)

## Overview

Before enabling Copilot, you need a clear picture of what your current permissions expose. Legacy sharing and unmanaged access sprawl create risk that is invisible until Copilot makes it searchable.

## Priority Order

Start with the highest risk content:

1. **Publicly accessible files** — shared with "Anyone with the link"
2. **Organization-wide shares** — content shared across the entire tenant
3. **Externally shared files** — documents shared with external collaborators
4. **Sensitivity label mismatches** — files tagged `Confidential` or `Internal Only` with broad sharing

## SharePoint Permission Inheritance

> **Warning:** SharePoint permission inheritance breaks at the file level. A folder may appear restricted while individual files retain broader sharing permissions applied in the past. Copilot queries based on effective access — it will find those files.

```
📁 Project Folder (Restricted to Team A)
├── 📄 report.docx ← Inherited: Team A only ✅
├── 📄 budget.xlsx ← Overridden: Shared with Everyone ⚠️
└── 📄 strategy.pptx ← Overridden: External sharing enabled ⚠️
```

## Risk Classification

See [`scripts/permission_audit.py`](../scripts/permission_audit.py) for the `classify_risk()` function that implements the sensitivity label vs. sharing scope risk matrix from the README.

## Action Items

### 1. Generate a Sensitivity Label Conflict Report

```powershell
# PowerShell: Find files with Confidential label shared broadly
Get-PnPListItem -List "Documents" -PageSize 500 | Where-Object {
    $_["_ComplianceTag"] -eq "Confidential" -and
    $_["SharedWithUsers"] -match "Everyone"
} | Select-Object FileLeafRef, FileRef, SharedWithUsers
```

### 2. Audit Sharing Links

```powershell
# Find all anonymous/organization-wide sharing links
Get-PnPSite -Includes SharingCapability | Where-Object {
    $_.SharingCapability -ne "Disabled"
}
```

### 3. Remediation Priority

| Risk Level | Condition | Action |
|------------|-----------|--------|
| **Critical** | Confidential + External sharing | Revoke immediately |
| **High** | Confidential + Org-wide sharing | Restrict to named users |
| **Medium** | Internal Only + Broad sharing | Review and scope down |
| **Low** | General + Team sharing | Monitor for drift |

## Validation

Before proceeding to Step 2, confirm:
- [ ] No `Confidential` files are shared organization-wide
- [ ] No `Confidential` files have external sharing enabled
- [ ] Orphaned sharing links have been revoked
- [ ] SharePoint permission inheritance audited for high-value sites

## Next Step

→ [Step 2: Pass the Copilot Posture Checks](step-2-posture-checks.md)
