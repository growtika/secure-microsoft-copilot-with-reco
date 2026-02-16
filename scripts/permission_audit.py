"""
Permission Risk Classification for Microsoft 365 Copilot

Provides data models and risk classification logic for auditing M365
permissions before enabling Copilot. This is a framework — not a
turnkey scanner. To use it against your tenant, you need to:

1. Register an app in Microsoft Entra ID
2. Grant Sites.Read.All and Files.Read.All application permissions
3. Authenticate with MSAL and feed Graph API results into these models

The core value here is the risk classification logic (classify_risk)
and the inheritance checker (check_inheritance_issues), which encode
the sensitivity-label-vs-sharing-scope risk matrix from the guide.

Graph API endpoints you'll need:
    GET https://graph.microsoft.com/v1.0/sites?search=*
    GET https://graph.microsoft.com/v1.0/sites/{id}/drive/root/children
    GET https://graph.microsoft.com/v1.0/sites/{id}/drive/items/{id}?$select=sensitivityLabel
"""

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PermissionFinding:
    """A single permission issue found during audit."""
    file_path: str
    site: str
    sensitivity_label: Optional[str]
    sharing_scope: str  # "named_users", "team", "organization", "external", "anonymous"
    risk_level: RiskLevel
    issue: str
    remediation: str

    def to_dict(self):
        d = asdict(self)
        d["risk_level"] = self.risk_level.value
        return d


@dataclass
class AuditReport:
    """Collects findings and generates a summary."""
    tenant_id: str
    total_files_scanned: int = 0
    findings: list = field(default_factory=list)

    def add_finding(self, finding: PermissionFinding):
        self.findings.append(finding)

    def summary(self) -> dict:
        return {
            "total_findings": len(self.findings),
            "critical": sum(1 for f in self.findings if f.risk_level == RiskLevel.CRITICAL),
            "high": sum(1 for f in self.findings if f.risk_level == RiskLevel.HIGH),
            "medium": sum(1 for f in self.findings if f.risk_level == RiskLevel.MEDIUM),
            "low": sum(1 for f in self.findings if f.risk_level == RiskLevel.LOW),
            "copilot_ready": all(
                f.risk_level not in (RiskLevel.CRITICAL, RiskLevel.HIGH)
                for f in self.findings
            ),
        }

    def to_json(self, path: str):
        with open(path, "w") as f:
            json.dump({
                "tenant_id": self.tenant_id,
                "total_files_scanned": self.total_files_scanned,
                "summary": self.summary(),
                "findings": [f.to_dict() for f in self.findings],
            }, f, indent=2)


def classify_risk(sensitivity_label: Optional[str], sharing_scope: str) -> RiskLevel:
    """
    Classify risk based on sensitivity label vs. sharing scope.

    This implements the risk matrix from the guide:

                        Named   Team    Org-Wide  External  Anonymous
    Highly Confidential  LOW    MEDIUM   CRIT      CRIT      CRIT
    Confidential         LOW    LOW      HIGH      CRIT      CRIT
    Internal Only        LOW    LOW      LOW       HIGH      CRIT
    General              LOW    LOW      LOW       MEDIUM    HIGH
    """
    broad = ("external", "anonymous")
    if sensitivity_label in ("Confidential", "Highly Confidential"):
        if sharing_scope in broad:
            return RiskLevel.CRITICAL
        if sharing_scope == "organization":
            return RiskLevel.HIGH if sensitivity_label == "Confidential" else RiskLevel.CRITICAL
        if sharing_scope == "team" and sensitivity_label == "Highly Confidential":
            return RiskLevel.MEDIUM
    if sensitivity_label == "Internal Only":
        if sharing_scope == "anonymous":
            return RiskLevel.CRITICAL
        if sharing_scope == "external":
            return RiskLevel.HIGH
    if sensitivity_label == "General":
        if sharing_scope == "anonymous":
            return RiskLevel.HIGH
        if sharing_scope == "external":
            return RiskLevel.MEDIUM
    return RiskLevel.LOW


def check_inheritance_issues(site_permissions: dict) -> list:
    """
    Detect broken permission inheritance in SharePoint.

    Input format (from your Graph API query):
    {
        "/sites/project/Shared Documents/Confidential": {
            "access": ["Team A"],
            "files": [
                {"name": "report.docx", "access": ["Team A"]},
                {"name": "budget.xlsx", "access": ["Everyone"]},  # broken
            ]
        }
    }

    Returns list of files where file-level access exceeds folder-level access.
    """
    issues = []
    for folder_path, folder_data in site_permissions.items():
        folder_access = set(folder_data.get("access", []))
        for file_info in folder_data.get("files", []):
            file_access = set(file_info.get("access", []))
            extra = file_access - folder_access
            if extra:
                issues.append({
                    "file": file_info["name"],
                    "folder": folder_path,
                    "folder_access": sorted(folder_access),
                    "file_access": sorted(file_access),
                    "extra_access": sorted(extra),
                })
    return issues


REMEDIATION = {
    RiskLevel.CRITICAL: "Revoke sharing immediately. Restrict to named users only.",
    RiskLevel.HIGH: "Restrict sharing scope to named users or specific security groups.",
    RiskLevel.MEDIUM: "Review sharing scope and reduce to minimum required access.",
    RiskLevel.LOW: "Monitor for drift. Include in quarterly access review.",
}
