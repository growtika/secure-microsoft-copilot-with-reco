"""
Scope Drift Monitor — OAuth Scope Risk Mapping for Connected AI Apps

Maps Microsoft Graph API permission scopes to risk tiers and provides
baseline comparison logic to detect when connected apps gain new
permissions over time.

This is a data model and comparison engine — not a turnkey scanner.
To use it against your tenant, you need to:

1. Register an app in Microsoft Entra ID
2. Grant Application.Read.All permissions
3. Query connected apps and their permission grants via Graph API

Graph API endpoints you'll need:
    GET https://graph.microsoft.com/v1.0/servicePrincipals
    GET https://graph.microsoft.com/v1.0/oauth2PermissionGrants
"""

import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional


class ScopeRisk(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Maps Microsoft Graph API permission scopes to risk tiers.
# Critical = full read/write across tenant resources
# High = broad data access (all files, all sites, all chats)
# Medium = read-only broad access
# Low = minimal / user-scoped
SCOPE_RISK_MAP = {
    # Critical — full read/write across tenant
    "Directory.ReadWrite.All": ScopeRisk.CRITICAL,
    "Mail.ReadWrite": ScopeRisk.CRITICAL,
    "Mail.Send": ScopeRisk.CRITICAL,
    "RoleManagement.ReadWrite.Directory": ScopeRisk.CRITICAL,
    # High — broad data access
    "Files.ReadWrite.All": ScopeRisk.HIGH,
    "Sites.ReadWrite.All": ScopeRisk.HIGH,
    "Calendars.ReadWrite": ScopeRisk.HIGH,
    "Chat.ReadWrite.All": ScopeRisk.HIGH,
    "ChannelMessage.Read.All": ScopeRisk.HIGH,
    # Medium — read-only broad access
    "User.Read.All": ScopeRisk.MEDIUM,
    "Group.Read.All": ScopeRisk.MEDIUM,
    "Directory.Read.All": ScopeRisk.MEDIUM,
    "Sites.Read.All": ScopeRisk.MEDIUM,
    "Files.Read.All": ScopeRisk.MEDIUM,
    # Low — minimal scopes
    "User.Read": ScopeRisk.LOW,
    "profile": ScopeRisk.LOW,
    "openid": ScopeRisk.LOW,
    "email": ScopeRisk.LOW,
    "offline_access": ScopeRisk.LOW,
}


@dataclass
class ConnectedApp:
    """A connected AI app with its granted OAuth scopes."""
    app_id: str
    name: str
    publisher: str
    scopes: list
    consent_type: str  # "admin" or "user"
    last_used: str
    users_count: int

    def get_risk_level(self) -> ScopeRisk:
        """Return the highest risk level across all granted scopes."""
        highest = ScopeRisk.LOW
        order = [ScopeRisk.LOW, ScopeRisk.MEDIUM, ScopeRisk.HIGH, ScopeRisk.CRITICAL]
        for scope in self.scopes:
            risk = SCOPE_RISK_MAP.get(scope, ScopeRisk.LOW)
            if order.index(risk) > order.index(highest):
                highest = risk
        return highest

    def get_high_risk_scopes(self) -> list:
        """Return scopes classified as HIGH or CRITICAL."""
        return [
            s for s in self.scopes
            if SCOPE_RISK_MAP.get(s, ScopeRisk.LOW) in (ScopeRisk.CRITICAL, ScopeRisk.HIGH)
        ]


@dataclass
class DriftFinding:
    """A single scope drift issue found during baseline comparison."""
    app_name: str
    finding_type: str  # "new_scope", "removed_scope", "new_app", "removed_app"
    details: str
    risk: ScopeRisk
    remediation: str

    def to_dict(self):
        d = asdict(self)
        d["risk"] = self.risk.value
        return d


def compare_baselines(current: list, baseline: list) -> list:
    """
    Compare current app permissions against a stored baseline.

    Args:
        current: list of ConnectedApp objects (current state)
        baseline: list of dicts from a previously saved baseline JSON

    Returns:
        list of DriftFinding objects describing what changed.
    """
    findings = []
    baseline_map = {app["app_id"]: app for app in baseline}
    current_map = {app.app_id: app for app in current}

    # New apps since baseline
    for app in current:
        if app.app_id not in baseline_map:
            findings.append(DriftFinding(
                app_name=app.name,
                finding_type="new_app",
                details=f"New connected app detected with scopes: {', '.join(app.scopes)}",
                risk=app.get_risk_level(),
                remediation="Review app permissions and verify it is approved for use.",
            ))
            continue

        # Scope expansion on existing apps
        old_scopes = set(baseline_map[app.app_id].get("scopes", []))
        new_scopes = set(app.scopes) - old_scopes
        if new_scopes:
            max_risk = ScopeRisk.LOW
            order = [ScopeRisk.LOW, ScopeRisk.MEDIUM, ScopeRisk.HIGH, ScopeRisk.CRITICAL]
            for scope in new_scopes:
                risk = SCOPE_RISK_MAP.get(scope, ScopeRisk.LOW)
                if order.index(risk) > order.index(max_risk):
                    max_risk = risk
            findings.append(DriftFinding(
                app_name=app.name,
                finding_type="new_scope",
                details=f"New scopes added: {', '.join(new_scopes)}",
                risk=max_risk,
                remediation="Review whether new scopes are justified. Revoke if excessive.",
            ))

    # Apps removed since baseline
    for app_id, app_data in baseline_map.items():
        if app_id not in current_map:
            findings.append(DriftFinding(
                app_name=app_data.get("name", app_id),
                finding_type="removed_app",
                details="App no longer connected (may have been removed).",
                risk=ScopeRisk.LOW,
                remediation="Confirm removal was intentional.",
            ))

    return findings


def save_baseline(apps: list, path: str):
    """Save current app state as a baseline JSON file."""
    with open(path, "w") as f:
        json.dump([asdict(app) for app in apps], f, indent=2)


def load_baseline(path: str) -> list:
    """Load a previously saved baseline JSON file."""
    with open(path) as f:
        return json.load(f)
