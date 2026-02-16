"""
Copilot Posture Check Reference

Defines the six posture checks required before enabling Microsoft Copilot,
with CIS M365 Benchmark v5.0 and ISO 27001:2022 mappings. This is a
reference data structure — not an automated validator.

Each check includes:
- What to validate (sub-checks)
- Where to validate it (Microsoft admin center path)
- Compliance mapping (CIS + ISO control IDs)
- Remediation steps if the check fails

Use this as a checklist, or extend it by querying Microsoft Graph API
to automate validation.
"""

from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    HIGH = "high"
    MEDIUM = "medium"


@dataclass
class PostureCheck:
    name: str
    severity: Severity
    description: str
    cis_reference: str
    iso_reference: str
    sub_checks: list
    admin_path: str
    remediation: str


POSTURE_CHECKS = [
    PostureCheck(
        name="Conditional Access Policies",
        severity=Severity.HIGH,
        description="MFA, device restrictions, and location-based controls for Copilot",
        cis_reference="CIS 5.2.2, 5.2.3",
        iso_reference="ISO A.8.3, A.8.5",
        sub_checks=[
            "MFA required for Copilot access",
            "Unmanaged devices blocked or limited",
            "Location-based restrictions enforced",
        ],
        admin_path="Microsoft Entra ID → Security → Conditional Access",
        remediation="Create a policy targeting Microsoft 365 Copilot with MFA requirement and device compliance.",
    ),
    PostureCheck(
        name="Data Loss Prevention Policies",
        severity=Severity.HIGH,
        description="DLP policies cover Copilot-generated content",
        cis_reference="CIS 3.1.1, 3.2.1",
        iso_reference="ISO A.8.10, A.8.12",
        sub_checks=[
            "DLP policies apply to Copilot interactions",
            "Sensitive information types detected in AI responses",
            "Blocking actions configured for high-sensitivity content",
        ],
        admin_path="Microsoft Purview → Data Loss Prevention → Policies",
        remediation="Ensure policies cover Microsoft 365 Copilot as a location.",
    ),
    PostureCheck(
        name="Sensitivity Labels",
        severity=Severity.HIGH,
        description="Sensitivity labels deployed and enforced across high-value content",
        cis_reference="CIS 3.3.1",
        iso_reference="ISO A.5.12, A.5.13",
        sub_checks=[
            "Labels applied to all high-value content",
            "Auto-labeling policies active",
            "Label-based access restrictions enforced",
        ],
        admin_path="Microsoft Purview → Information Protection → Labels",
        remediation="Publish labels and enable auto-labeling for sensitive content types.",
    ),
    PostureCheck(
        name="External Sharing Controls",
        severity=Severity.MEDIUM,
        description="External sharing scoped to prevent Copilot data exposure",
        cis_reference="CIS 7.2.3, 7.2.6",
        iso_reference="ISO A.5.14, A.8.3",
        sub_checks=[
            "Guest access policies reviewed",
            "External sharing scoped to approved domains",
            "Anonymous sharing links disabled or limited",
        ],
        admin_path="SharePoint Admin Center → Policies → Sharing",
        remediation="Set external sharing to 'Existing guests' or 'Only people in your organization'.",
    ),
    PostureCheck(
        name="Device Compliance",
        severity=Severity.MEDIUM,
        description="Only compliant devices can access Copilot-enabled services",
        cis_reference="CIS 5.1.2",
        iso_reference="ISO A.8.1",
        sub_checks=[
            "Device compliance policies enforced",
            "Non-compliant devices blocked from Copilot",
            "MDM configured and active",
        ],
        admin_path="Microsoft Intune → Devices → Compliance policies",
        remediation="Create compliance policies and link them to Conditional Access.",
    ),
    PostureCheck(
        name="Audit Logging",
        severity=Severity.MEDIUM,
        description="Audit logging captures Copilot interactions",
        cis_reference="CIS 8.5.1",
        iso_reference="ISO A.8.15",
        sub_checks=[
            "Unified Audit Log enabled",
            "Copilot-specific events captured",
            "Log retention meets compliance requirements",
        ],
        admin_path="Microsoft Purview → Audit → Audit retention policies",
        remediation="Ensure Copilot activities are included and retention period meets requirements.",
    ),
]


# Gate logic
def evaluate_readiness(results: dict) -> dict:
    """
    Given a dict of {check_name: bool} pass/fail results,
    determine deployment readiness.

    Returns:
        {"pilot_ready": bool, "production_ready": bool, "blocking": [...]}
    """
    blocking = []
    for check in POSTURE_CHECKS:
        passed = results.get(check.name, False)
        if not passed:
            blocking.append({
                "name": check.name,
                "severity": check.severity.value,
                "remediation": check.remediation,
                "admin_path": check.admin_path,
            })

    high_blocking = [b for b in blocking if b["severity"] == "high"]
    medium_blocking = [b for b in blocking if b["severity"] == "medium"]

    return {
        "pilot_ready": len(high_blocking) == 0,
        "production_ready": len(blocking) == 0,
        "high_blocking": high_blocking,
        "medium_blocking": medium_blocking,
    }
