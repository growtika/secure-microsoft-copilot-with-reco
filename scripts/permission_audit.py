"""
Permission Audit Script for Microsoft 365 Copilot Security

Identifies overshared files, sensitivity label conflicts, and permission
inheritance issues before enabling Microsoft Copilot.

Prerequisites:
    pip install msal requests

Usage:
    python permission_audit.py --tenant-id YOUR_TENANT_ID
    python permission_audit.py --tenant-id YOUR_TENANT_ID --output report.json
"""

import argparse
import json
import sys
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
    file_path: str
    site: str
    sensitivity_label: Optional[str]
    sharing_scope: str
    risk_level: RiskLevel
    issue: str
    remediation: str

    def to_dict(self):
        d = asdict(self)
        d["risk_level"] = self.risk_level.value
        return d


@dataclass
class AuditReport:
    tenant_id: str
    total_files_scanned: int = 0
    findings: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def add_finding(self, finding: PermissionFinding):
        self.findings.append(finding)

    def generate_summary(self):
        self.summary = {
            "total_findings": len(self.findings),
            "critical": len([f for f in self.findings if f.risk_level == RiskLevel.CRITICAL]),
            "high": len([f for f in self.findings if f.risk_level == RiskLevel.HIGH]),
            "medium": len([f for f in self.findings if f.risk_level == RiskLevel.MEDIUM]),
            "low": len([f for f in self.findings if f.risk_level == RiskLevel.LOW]),
        }
        return self.summary

    def to_dict(self):
        return {
            "tenant_id": self.tenant_id,
            "total_files_scanned": self.total_files_scanned,
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings],
        }


def classify_risk(sensitivity_label: Optional[str], sharing_scope: str) -> RiskLevel:
    """Classify risk based on sensitivity label and sharing scope."""
    if sensitivity_label in ("Confidential", "Highly Confidential"):
        if sharing_scope in ("external", "anonymous"):
            return RiskLevel.CRITICAL
        if sharing_scope == "organization":
            return RiskLevel.HIGH
    if sensitivity_label == "Internal Only":
        if sharing_scope in ("external", "anonymous", "organization"):
            return RiskLevel.MEDIUM
    return RiskLevel.LOW


def get_remediation(risk_level: RiskLevel, sharing_scope: str) -> str:
    """Return remediation guidance based on risk level."""
    remediations = {
        RiskLevel.CRITICAL: "Revoke sharing immediately. Restrict to named users only.",
        RiskLevel.HIGH: "Restrict sharing scope to named users or specific groups.",
        RiskLevel.MEDIUM: "Review sharing scope and reduce to minimum required access.",
        RiskLevel.LOW: "Monitor for drift. Include in quarterly access review.",
    }
    return remediations.get(risk_level, "Review and assess.")


def check_inheritance_issues(site_permissions: dict) -> list:
    """
    Check for permission inheritance breaks that could cause
    individual files to have broader access than their parent folder.
    """
    issues = []
    # In production, this would query SharePoint API for broken inheritance
    # Example structure:
    # {
    #     "folder": "/sites/project/Shared Documents/Confidential",
    #     "folder_access": ["Team A"],
    #     "files": [
    #         {"name": "report.docx", "access": ["Everyone"]},  # BROKEN
    #     ]
    # }
    for folder_path, folder_data in site_permissions.items():
        folder_access = set(folder_data.get("access", []))
        for file_info in folder_data.get("files", []):
            file_access = set(file_info.get("access", []))
            if file_access - folder_access:
                issues.append({
                    "file": file_info["name"],
                    "folder": folder_path,
                    "folder_access": list(folder_access),
                    "file_access": list(file_access),
                    "extra_access": list(file_access - folder_access),
                })
    return issues


def run_audit(tenant_id: str, output_file: Optional[str] = None):
    """Run the full permission audit."""
    print(f"Starting permission audit for tenant: {tenant_id}")
    print("=" * 60)

    report = AuditReport(tenant_id=tenant_id)

    # NOTE: In production, replace this with Microsoft Graph API calls:
    #
    # 1. Authenticate with MSAL:
    #    app = msal.ConfidentialClientApplication(client_id, authority, client_credential)
    #    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    #
    # 2. Query SharePoint sites:
    #    GET https://graph.microsoft.com/v1.0/sites?search=*
    #
    # 3. For each site, query drive items with sharing info:
    #    GET https://graph.microsoft.com/v1.0/sites/{site-id}/drive/root/children
    #
    # 4. Check sensitivity labels:
    #    GET https://graph.microsoft.com/v1.0/sites/{site-id}/drive/items/{item-id}
    #    ?$select=sensitivityLabel,sharingInformation

    print("\nAudit configuration:")
    print(f"  Tenant ID: {tenant_id}")
    print(f"  Output: {output_file or 'stdout'}")
    print("\nTo run this audit against your tenant:")
    print("  1. Register an app in Microsoft Entra ID")
    print("  2. Grant Sites.Read.All and Files.Read.All permissions")
    print("  3. Set environment variables:")
    print("     export AZURE_CLIENT_ID=<your-client-id>")
    print("     export AZURE_CLIENT_SECRET=<your-client-secret>")
    print("     export AZURE_TENANT_ID=<your-tenant-id>")
    print("\nExample findings (demo mode):")

    # Demo findings to illustrate the output format
    demo_findings = [
        PermissionFinding(
            file_path="/sites/finance/Shared Documents/Q4 Budget.xlsx",
            site="Finance Team Site",
            sensitivity_label="Confidential",
            sharing_scope="organization",
            risk_level=RiskLevel.HIGH,
            issue="Confidential file shared with entire organization",
            remediation="Restrict to Finance team members only",
        ),
        PermissionFinding(
            file_path="/sites/hr/Shared Documents/Employee Records/salaries.xlsx",
            site="HR Team Site",
            sensitivity_label="Highly Confidential",
            sharing_scope="external",
            risk_level=RiskLevel.CRITICAL,
            issue="Highly Confidential HR file has external sharing enabled",
            remediation="Revoke external sharing immediately",
        ),
        PermissionFinding(
            file_path="/sites/marketing/Shared Documents/Campaign Plan.pptx",
            site="Marketing Team Site",
            sensitivity_label="Internal Only",
            sharing_scope="anonymous",
            risk_level=RiskLevel.MEDIUM,
            issue="Internal Only file accessible via anonymous link",
            remediation="Remove anonymous link, restrict to named users",
        ),
    ]

    for finding in demo_findings:
        report.add_finding(finding)
        icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        print(f"\n  {icon[finding.risk_level.value]} [{finding.risk_level.value.upper()}] {finding.file_path}")
        print(f"    Issue: {finding.issue}")
        print(f"    Remediation: {finding.remediation}")

    report.total_files_scanned = 3  # Demo value
    summary = report.generate_summary()

    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print(f"  Files scanned: {report.total_files_scanned}")
    print(f"  Total findings: {summary['total_findings']}")
    print(f"  Critical: {summary['critical']}")
    print(f"  High: {summary['high']}")
    print(f"  Medium: {summary['medium']}")
    print(f"  Low: {summary['low']}")

    if summary["critical"] > 0 or summary["high"] > 0:
        print("\n⚠️  RECOMMENDATION: Do NOT enable Copilot until Critical and High findings are remediated.")
    else:
        print("\n✅ No Critical or High findings. Environment is ready for Copilot posture checks.")

    if output_file:
        with open(output_file, "w") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\nFull report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Audit Microsoft 365 permissions before enabling Copilot"
    )
    parser.add_argument("--tenant-id", required=True, help="Microsoft 365 tenant ID")
    parser.add_argument("--output", help="Output file path for JSON report")
    args = parser.parse_args()

    run_audit(args.tenant_id, args.output)


if __name__ == "__main__":
    main()
