# Complementary: Native Microsoft Purview Copilot Controls

[← Back to Overview](../README.md)

## Overview

Microsoft has been rolling out native Copilot security controls within Purview and SharePoint Advanced Management. These controls are complementary to Reco's AI governance layer — they reduce the attack surface by limiting what Copilot can access, while Reco monitors how that access is used and detects misuse.

## Restricted SharePoint Search

**What it does:** Limits which SharePoint sites Copilot can index and surface content from. Instead of Copilot searching across all sites a user has access to, it restricts queries to a curated allowlist of approved sites.

**When to use it:** During initial Copilot rollout when permission debt hasn't been fully remediated. Acts as a safety net — even if oversharing exists on unlisted sites, Copilot won't surface that content.

**How it complements Reco:**
- Restricted SharePoint Search limits the *searchable scope*
- Reco monitors *what happens within that scope* — detecting anomalous access patterns, bulk queries, and sensitive content surfacing

```mermaid
graph LR
    subgraph "Without Restricted Search"
        ALL[All SharePoint Sites<br/>user has access to] --> CP1[Copilot searches<br/>everything]
        CP1 --> RISK1[High exposure risk<br/>from legacy oversharing]
    end

    subgraph "With Restricted Search"
        ALLOW[Curated allowlist<br/>of approved sites] --> CP2[Copilot searches<br/>only approved sites]
        CP2 --> RISK2[Reduced exposure<br/>bounded search scope]
    end

    style RISK1 fill:#d63031,color:#fff
    style RISK2 fill:#00b894,color:#fff
    style ALL fill:#ff6b6b,color:#fff
    style ALLOW fill:#00b894,color:#fff
```

## SharePoint Advanced Management

**What it does:** Provides site-level access governance including oversharing reports, site lifecycle policies, and data access governance at the site collection level.

**Key capabilities:**
- Oversharing reports identifying broadly shared content
- Site lifecycle policies for inactive sites
- Conditional access policies at the site level
- Data access governance dashboards

**How it complements Reco:**
- SAM identifies oversharing at the SharePoint level
- Reco extends this with cross-service visibility (Teams, Exchange, OneDrive) and adds identity risk correlation

## Data Access Governance Reports

**What it does:** Identifies content shared broadly across the tenant — org-wide shares, external shares, anonymous links — and surfaces it in Microsoft Purview.

**How it complements Reco:**
- DAG reports are Microsoft's native version of the permission audit
- Reco adds the risk classification layer (correlating sharing scope with sensitivity labels) and the continuous monitoring that detects when new oversharing occurs

## Topic-Level Permission Controls

**What it does:** Restricts Copilot from surfacing content in specific topics or sensitivity categories, adding granular control beyond file-level permissions.

**How it complements Reco:**
- Topic controls restrict what Copilot *generates*
- Reco detects when users *attempt* to surface restricted content — providing the detection signal that native controls alone don't offer

## Defense-in-Depth Model

```mermaid
graph TD
    subgraph "Layer 1: Reduce Attack Surface — Microsoft Native"
        L1A[Restricted SharePoint Search<br/><i>Limit searchable scope</i>]
        L1B[SharePoint Advanced Management<br/><i>Site-level governance</i>]
        L1C[Data Access Governance<br/><i>Oversharing identification</i>]
        L1D[Topic-Level Controls<br/><i>Content category restrictions</i>]
    end

    subgraph "Layer 2: Access Control — Microsoft Entra ID"
        L2A[Conditional Access<br/><i>User + device + location gates</i>]
        L2B[Sensitivity Labels<br/><i>Content classification</i>]
        L2C[DLP Policies<br/><i>Data loss prevention</i>]
    end

    subgraph "Layer 3: Detect & Respond — Reco"
        L3A[AI Posture Checks<br/><i>Pre-deployment validation</i>]
        L3B[Identity Risk Analysis<br/><i>User classification</i>]
        L3C[Threat Detection<br/><i>Anomaly & behavior monitoring</i>]
        L3D[Scope Drift Monitoring<br/><i>Plugin permission tracking</i>]
    end

    L1A & L1B & L1C & L1D --> COPILOT[Microsoft Copilot]
    COPILOT --> L2A & L2B & L2C
    L2A & L2B & L2C --> RESPONSE[Copilot Response]
    RESPONSE --> L3A & L3B & L3C & L3D

    style L1A fill:#0078d4,color:#fff
    style L1B fill:#0078d4,color:#fff
    style L1C fill:#0078d4,color:#fff
    style L1D fill:#0078d4,color:#fff
    style L2A fill:#ffd93d,color:#000
    style L2B fill:#ffd93d,color:#000
    style L2C fill:#ffd93d,color:#000
    style L3A fill:#00d4aa,color:#000
    style L3B fill:#00d4aa,color:#000
    style L3C fill:#00d4aa,color:#000
    style L3D fill:#00d4aa,color:#000
    style COPILOT fill:#5f27cd,color:#fff
    style RESPONSE fill:#636e72,color:#fff
```

> **The key insight:** Native controls and Reco address different layers of the problem. Native controls restrict what Copilot *can* access. Reco detects what users *are doing* with that access. A defense-in-depth approach uses both.
