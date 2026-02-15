"""
Copilot Posture Check Validator

Validates the six posture checks required before enabling Microsoft Copilot.
Checks are aligned with CIS Microsoft 365 Foundations Benchmark v5.0
and ISO 27001:2022.

Usage:
    python posture_check_validator.py
    python posture_check_validator.py --output results.json
"""

import argparse
import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional


class Severity(Enum):
    HIGH = "high"
    MEDIUM = "medium"


class Status(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warning"
    SKIP = "skipped"


@dataclass
class PostureCheck:
    name: str
    severity: Severity
    status: Status
    description: str
    cis_reference: str
    iso_reference: str
    details: str = ""
    remediation: str = ""

    def to_dict(self):
        d = asdict(self)
        d["severity"] = self.severity.value
        d["status"] = self.status.value
        return d


POSTURE_CHECKS = [
    {
        "name": "Conditional Access Policies",
        "severity": Severity.HIGH,
        "description": "Verify MFA, device restrictions, and location-based controls for Copilot",
        "cis_reference": "CIS 5.2.2, 5.2.3",
        "iso_reference": "ISO A.8.3, A.8.5",
        "checks": [
            "MFA required for Copilot access",
            "Unmanaged devices blocked or limited",
            "Location-based restrictions enforced",
        ],
        "remediation": (
            "Configure Conditional Access in Microsoft Entra ID → Security → Conditional Access. "
            "Create a policy targeting Microsoft 365 Copilot with MFA requirement and device compliance."
        ),
    },
    {
        "name": "Data Loss Prevention Policies",
        "severity": Severity.HIGH,
        "description": "Ensure DLP policies cover Copilot-generated content",
        "cis_reference": "CIS 3.1.1, 3.2.1",
        "iso_reference": "ISO A.8.10, A.8.12",
        "checks": [
            "DLP policies apply to Copilot interactions",
            "Sensitive information types detected in AI responses",
            "Blocking actions configured for high-sensitivity content",
        ],
        "remediation": (
            "Navigate to Microsoft Purview → Data Loss Prevention → Policies. "
            "Ensure policies cover Microsoft 365 Copilot as a location."
        ),
    },
    {
        "name": "Sensitivity Labels",
        "severity": Severity.HIGH,
        "description": "Confirm sensitivity labels are deployed and enforced",
        "cis_reference": "CIS 3.3.1",
        "iso_reference": "ISO A.5.12, A.5.13",
        "checks": [
            "Labels applied to all high-value content",
            "Auto-labeling policies active",
            "Label-based access restrictions enforced",
        ],
        "remediation": (
            "Navigate to Microsoft Purview → Information Protection → Labels. "
            "Publish labels and enable auto-labeling for sensitive content types."
        ),
    },
    {
        "name": "External Sharing Controls",
        "severity": Severity.MEDIUM,
        "description": "Validate external sharing prevents Copilot data exposure",
        "cis_reference": "CIS 7.2.3, 7.2.6",
        "iso_reference": "ISO A.5.14, A.8.3",
        "checks": [
            "Guest access policies reviewed",
            "External sharing scoped to approved domains",
            "Anonymous sharing links disabled or limited",
        ],
        "remediation": (
            "Navigate to SharePoint Admin Center → Policies → Sharing. "
            "Set external sharing to 'Existing guests' or 'Only people in your organization'."
        ),
    },
    {
        "name": "Device Compliance",
        "severity": Severity.MEDIUM,
        "description": "Ensure only compliant devices access Copilot-enabled services",
        "cis_reference": "CIS 5.1.2",
        "iso_reference": "ISO A.8.1",
        "checks": [
            "Device compliance policies enforced",
            "Non-compliant devices blocked from Copilot",
            "MDM configured and active",
        ],
        "remediation": (
            "Navigate to Microsoft Intune → Devices → Compliance policies. "
            "Create compliance policies and link them to Conditional Access."
        ),
    },
    {
        "name": "Audit Logging",
        "severity": Severity.MEDIUM,
        "description": "Verify audit logging captures Copilot interactions",
        "cis_reference": "CIS 8.5.1",
        "iso_reference": "ISO A.8.15",
        "checks": [
            "Unified Audit Log enabled",
            "Copilot-specific events captured",
            "Log retention meets compliance requirements",
        ],
        "remediation": (
            "Navigate to Microsoft Purview → Audit → Audit retention policies. "
            "Ensure Copilot activities are included and retention period meets requirements."
        ),
    },
]


def run_validation(output_file: Optional[str] = None):
    """Run all posture check validations."""
    print("Microsoft Copilot Posture Check Validator")
    print("=" * 60)
    print()

    results = []
    high_pass = 0
    high_total = 0
    medium_pass = 0
    medium_total = 0

    for check_config in POSTURE_CHECKS:
        # In production, each check would query the relevant Microsoft API
        # For demo purposes, all checks are shown as requiring validation
        check = PostureCheck(
            name=check_config["name"],
            severity=check_config["severity"],
            status=Status.SKIP,
            description=check_config["description"],
            cis_reference=check_config["cis_reference"],
            iso_reference=check_config["iso_reference"],
            details="Manual validation required - connect to Microsoft Graph API",
            remediation=check_config["remediation"],
        )

        if check.severity == Severity.HIGH:
            high_total += 1
            if check.status == Status.PASS:
                high_pass += 1
        else:
            medium_total += 1
            if check.status == Status.PASS:
                medium_pass += 1

        icon = {
            Status.PASS: "✅",
            Status.FAIL: "❌",
            Status.WARN: "⚠️",
            Status.SKIP: "⏭️",
        }

        severity_label = f"[{check.severity.value.upper()}]"
        print(f"{icon[check.status]} {severity_label:8s} {check.name}")
        print(f"   {check.description}")
        print(f"   Compliance: {check.cis_reference} | {check.iso_reference}")
        print(f"   Sub-checks:")
        for sub in check_config["checks"]:
            print(f"     - {sub}")
        if check.status != Status.PASS:
            print(f"   Remediation: {check.remediation}")
        print()

        results.append(check)

    print("=" * 60)
    print("SUMMARY")
    print(f"  HIGH severity:   {high_pass}/{high_total} passing")
    print(f"  MEDIUM severity: {medium_pass}/{medium_total} passing")
    print()

    if high_pass < high_total:
        print("🚫 GATE: Do NOT expand Copilot access until all HIGH severity checks pass.")
    elif medium_pass < medium_total:
        print("⚠️  GATE: Address MEDIUM severity checks before broad production rollout.")
    else:
        print("✅ All posture checks passing. Ready for Copilot deployment.")

    if output_file:
        output = {
            "checks": [r.to_dict() for r in results],
            "summary": {
                "high_passing": high_pass,
                "high_total": high_total,
                "medium_passing": medium_pass,
                "medium_total": medium_total,
                "ready_for_pilot": high_pass == high_total,
                "ready_for_production": (high_pass == high_total and medium_pass == medium_total),
            },
        }
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate Copilot posture checks before deployment"
    )
    parser.add_argument("--output", help="Output file path for JSON results")
    args = parser.parse_args()

    run_validation(args.output)


if __name__ == "__main__":
    main()
