# Curavias — Canonical Diagram Library

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |

> **Curavias** is the Swiss AI-powered patient-flow and hospital-capacity
> platform — a Microsoft Frontier-Firm reference implementation grounded on
> Fabric IQ, Foundry IQ, and Work IQ.

## Executive summary

This is the single source of truth for the five canonical Curavias diagrams:
system context, medallion data flow, agent topology, deployment and region, and
the key request sequence. Each diagram is authored once here and copied into the
documents listed in its **Embed in** note (GitHub Markdown cannot transclude, so
copies are kept in sync from this library). Terminology follows
[GLOSSARY.md](../GLOSSARY.md); facts follow
[ARCHITECTURE.md](../ARCHITECTURE.md),
[INFRASTRUCTURE.md](../INFRASTRUCTURE.md), and
[CURAVIAS-PRODUCT-STATUS.md](../CURAVIAS-PRODUCT-STATUS.md).

## How to use this library

* Copy the fenced `mermaid` block into the target doc under a short caption.
* When a diagram changes here, update **every** doc in its **Embed in** note in
  the same PR so copies do not drift.
* Keep node labels terminology-aligned to [GLOSSARY.md](../GLOSSARY.md).

## 1. System context (C4 level 1)

Curavias in its ecosystem: the Swiss care network it serves, the human + AI-agent
Frontier-Firm team that operates it, the Microsoft IQ backbone that grounds it,
and the GitHub delivery plane that builds it.

```mermaid
flowchart TB
    subgraph Team["Frontier-Firm team"]
        CT["Capacity and bed-management teams<br/>(agent bosses, HITL)"]
    end

    subgraph Network["Swiss care network"]
        ACUTE["Acute hospitals"]
        REHAB["Rehabilitation clinics"]
        SPITEX["Spitex (home care)"]
        INS["Insurer-linked coordination"]
    end

    CUR["Curavias platform<br/>advisory-only, synthetic data, no PHI"]

    subgraph IQ["Microsoft IQ backbone (Azure)"]
        FABRICIQ["Fabric IQ<br/>ontology + semantic backbone"]
        FOUNDRYIQ["Foundry IQ<br/>knowledge + agents"]
        WORKIQ["Work IQ<br/>M365 work context (read-only)"]
    end

    GH["GitHub delivery plane<br/>Copilot coding agent + MCP"]

    CT -->|questions, approvals| CUR
    CUR -->|advisory insights, cited answers| CT
    Network -->|synthetic capacity + episode data| CUR
    CUR --> FABRICIQ
    CUR --> FOUNDRYIQ
    CUR --> WORKIQ
    GH -.builds + governs.-> CUR
```

**Embed in:** README.md, ARCHITECTURE.md, PRD.md, CURAVIAS-PRODUCT-STATUS.md.

## 2. Medallion data flow

The Bronze / Silver / Gold lakehouse path from file upload to grounded
consumption. Silver is quality-gated (schema, FK, PHI-absence); Gold feeds the
Direct Lake semantic model and Fabric IQ, which in turn ground Foundry IQ and the
Fabric Data Agent.

```mermaid
flowchart LR
    UP["File upload<br/>(synthetic bundles)"] --> BR[("Bronze<br/>raw ingested")]
    BR --> SV[("Silver<br/>conformed + quality-gated")]
    SV --> GD[("Gold<br/>analytics-ready Delta")]
    GD --> SM["Direct Lake<br/>semantic model"]
    SM --> FIQ["Fabric IQ ontology"]
    FIQ --> FOIQ["Foundry IQ grounding"]
    FIQ --> FDA["Fabric Data Agent<br/>da_hospital_capacity"]
    SV -. data-quality gate .-> DQ["data-quality-agent"]
```

**Embed in:** DATA.md, ARCHITECTURE.md, INFRASTRUCTURE.md.

## 3. Agent topology and orchestration

The in-app Curavias copilot orchestrator dispatches to the Product Owner (PO),
Bed-Value Analysis (BVA), and capacity copilots, with supporting data and signal
agents. Every actionable output returns to a human agent boss for approval.

```mermaid
flowchart TB
    USER["Agent boss (human, HITL)"] --> ORCH["App copilot orchestrator"]

    subgraph Capacity["Capacity copilots"]
        BMCA["bmca-agent<br/>bed management"]
        OOA["ooa-agent<br/>occupancy / 72h forecast"]
        DCA["dca-agent<br/>discharge"]
        ORSA["orsa-agent<br/>OR steering"]
        SBA["sba-agent<br/>staffing balance"]
        CSA["csa-agent<br/>crisis / scenario"]
    end

    subgraph Advisory["Product + value"]
        PO["product-owner-agent"]
        BVA["bva-agent<br/>bed-value analysis"]
    end

    subgraph Support["Data + signal"]
        DQ["data-quality-agent"]
        SIG["signal-agent"]
    end

    ORCH --> Capacity
    ORCH --> Advisory
    ORCH --> Support
    WORKIQ["Work IQ context"] -.read-only.-> ORCH
    Capacity -->|cited, advisory-only| USER
    Advisory -->|cited, advisory-only| USER
```

**Embed in:** ARCHITECTURE.md, AI.md, AGENTS.md.

## 4. Deployment and region

As-deployed demo reality versus the target GA architecture. The demo runs PROD
single-region in Switzerland North with SIT in US regions (synthetic data only);
target GA adds Switzerland West failover.

```mermaid
flowchart TB
    subgraph Deployed["As-deployed (demo / proof-of-technology)"]
        direction TB
        SIT["SIT<br/>westus2 (+ eastus2 Foundry split)<br/>synthetic, no PHI"]
        PRODD["PROD<br/>switzerlandnorth (single region)<br/>synthetic, no PHI"]
        SIT -->|promote| PRODD
    end

    subgraph Target["Target GA architecture"]
        direction TB
        SWN["Switzerland North<br/>primary"]
        SWW["Switzerland West<br/>failover"]
        SWN -->|failover| SWW
    end

    Deployed -.sunset to Swiss GA<br/>ADR-0013 / ADR-0032 / ADR-0037.-> Target
```

**Embed in:** INFRASTRUCTURE.md, ALM_PLAN.md, CURAVIAS-PRODUCT-STATUS.md.

## 5. Key request sequence

A user question in the Curavias app flows through the orchestrator to the right
sub-agent(s) and returns a grounded, cited, advisory-only answer that a human
approves before any action.

```mermaid
sequenceDiagram
    actor User as Agent boss (human)
    participant App as Curavias App
    participant Orch as Orchestrator
    participant Agent as Sub-agent(s)
    participant IQ as Fabric IQ / Foundry IQ

    User->>App: Ask a capacity question
    App->>Orch: Forward with work context (Work IQ)
    Orch->>Agent: Dispatch to matching copilot
    Agent->>IQ: Retrieve grounded facts + knowledge
    IQ-->>Agent: Cited evidence (GroundedChunk)
    Agent-->>Orch: Advisory answer + citations
    Orch-->>App: Grounded, cited response
    App-->>User: Preview / recommendation (HITL)
    User->>App: Approve before any action
```

**Embed in:** ARCHITECTURE.md, AI.md, OPERATIONS.md.
