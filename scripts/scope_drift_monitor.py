"""
Scope Drift Monitor for Connected AI Apps

Monitors permission scope changes in connected AI applications
to detect drift that could expand Copilot's effective data access.

Usage:
    python scope_drift_monitor.py
    python scope_drift_monitor.py --baseline baseline.json
    python scope_drift_monitor.py --output drift_report.json
"""

import argparse
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional


class ScopeRisk(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


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
    app_id: str
    name: str
    publisher: str
    scopes: list
    consent_type: str
    last_used: str
    users_count: int

    def get_risk_level(self) -> ScopeRisk:
        highest = ScopeRisk.LOW
        order = [ScopeRisk.LOW, ScopeRisk.MEDIUM, ScopeRisk.HIGH, ScopeRisk.CRITICAL]
        for scope in self.scopes:
            risk = SCOPE_RISK_MAP.get(scope, ScopeRisk.LOW)
            if order.index(risk) > order.index(highest):
                highest = risk
        return highest

    def get_high_risk_scopes(self) -> list:
        return [
            s for s in self.scopes
            if SCOPE_RISK_MAP.get(s, ScopeRisk.LOW) in (ScopeRisk.CRITICAL, ScopeRisk.HIGH)
        ]


@dataclass
class DriftFinding:
    app_name: str
    finding_type: str  # "new_scope", "removed_scope", "new_app", "unused_app"
    details: str
    risk: ScopeRisk
    remediation: str

    def to_dict(self):
        d = asdict(self)
        d["risk"] = self.risk.value
        return d


def compare_baselines(current: list, baseline: list) -> list:
    """Compare current app permissions against a stored baseline."""
    findings = []
    baseline_map = {app["app_id"]: app for app in baseline}
    current_map = {app.app_id: app for app in current}

    # Check for new apps
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

        # Check for new scopes
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

    # Check for unused apps
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


def run_monitor(baseline_file: Optional[str] = None, output_file: Optional[str] = None):
    """Run scope drift monitoring."""
    print("Copilot Connected App Scope Drift Monitor")
    print("=" * 60)
    print()

    # In production, query Microsoft Graph API:
    # GET https://graph.microsoft.com/v1.0/servicePrincipals
    # GET https://graph.microsoft.com/v1.0/oauth2PermissionGrants

    demo_apps = [
        ConnectedApp(
            app_id="app-001",
            name="Copilot for Microsoft 365",
            publisher="Microsoft",
            scopes=["Files.Read.All", "Sites.Read.All", "User.Read", "Chat.ReadWrite.All"],
            consent_type="admin",
            last_used="2026-01-22",
            users_count=150,
        ),
        ConnectedApp(
            app_id="app-002",
            name="Third-Party AI Plugin",
            publisher="ExampleVendor",
            scopes=["Files.ReadWrite.All", "Mail.ReadWrite", "User.Read.All"],
            consent_type="admin",
            last_used="2026-01-20",
            users_count=45,
        ),
        ConnectedApp(
            app_id="app-003",
            name="Analytics Dashboard",
            publisher="AnalyticsCo",
            scopes=["User.Read", "Directory.Read.All"],
            consent_type="user",
            last_used="2025-10-15",
            users_count=3,
        ),
    ]

    print("Connected AI Apps:")
    print()

    risk_icons = {
        ScopeRisk.CRITICAL: "🔴",
        ScopeRisk.HIGH: "🟠",
        ScopeRisk.MEDIUM: "🟡",
        ScopeRisk.LOW: "🟢",
    }

    high_scopes_to_review = 0

    for app in demo_apps:
        risk = app.get_risk_level()
        high_risk = app.get_high_risk_scopes()
        high_scopes_to_review += len(high_risk)

        print(f"  {risk_icons[risk]} {app.name} (by {app.publisher})")
        print(f"    Consent: {app.consent_type} | Users: {app.users_count} | Last used: {app.last_used}")
        print(f"    Scopes ({len(app.scopes)}):")
        for scope in app.scopes:
            scope_risk = SCOPE_RISK_MAP.get(scope, ScopeRisk.LOW)
            print(f"      {risk_icons[scope_risk]} {scope}")
        if high_risk:
            print(f"    ⚠️  High-risk scopes to review: {', '.join(high_risk)}")
        print()

    print(f"High Scopes to Review: {high_scopes_to_review}")
    print()

    # Check for unused apps (90+ days)
    unused = [a for a in demo_apps if a.last_used < "2025-11-01"]
    if unused:
        print("⚠️  Unused apps (90+ days inactive):")
        for app in unused:
            print(f"    - {app.name} (last used: {app.last_used})")
        print()

    if output_file:
        output = {
            "scan_date": datetime.now().isoformat(),
            "apps": [asdict(a) for a in demo_apps],
            "high_scopes_to_review": high_scopes_to_review,
            "unused_apps": [a.name for a in unused],
        }
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor permission scope drift in connected AI apps"
    )
    parser.add_argument("--baseline", help="Path to baseline JSON for comparison")
    parser.add_argument("--output", help="Output file path for JSON report")
    args = parser.parse_args()

    run_monitor(args.baseline, args.output)


if __name__ == "__main__":
    main()
