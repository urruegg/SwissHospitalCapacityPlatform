# MVP Agent Solution Design
## Swiss AI-Powered Patient Flow and Hospital Capacity Platform

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-08 |
| **Author** | Urs Rueegg |
| **Status** | Draft for Review |
| **Scope** | MVP — first agent set, Swiss acute-care operations |

---

## Document Purpose

This document provides the detailed solution design for the first production-oriented
agent set of the Swiss AI-Powered Patient Flow and Hospital Capacity Platform.
It translates the MVP architecture, compliance, and data baseline into a
concrete, implementable agentic architecture pattern suitable for Swiss acute-care
hospital operations under FADP, EPDG, and KVG constraints.

This design is **directly constrained** by and fully traceable to:

- `docs/SD.md` (v1.2.0) — MVP solution design baseline
- `docs/PRD.md` (v1.1.1) — Functional and non-functional requirements
- `docs/ARCHITECTURE.md` (v0.10.0) — Architecture decisions and GA baseline
- `docs/AI.md` (v0.4.1) — AI service pattern and PHI inference rules
- `docs/COMPLIANCE.md` (v0.3.1) — Swiss control model CH-C01–CH-C10
- `docs/SECURITY.md` (v0.3.1) — Zero Trust baseline
- `docs/DATA.md` (v0.3.1) — Data domains, contracts, retention
- `docs/INFRASTRUCTURE.md` (v1.2.0) — Deployed topology
- `docs/OPERATIONS.md` (v1.0.1) — Operating model and SLOs
- `docs/BVA.md` (v1.0.1) — Business value and cost assumptions
- `docs/ALM_PLAN.md` (v0.3.0) — Delivery governance
- `docs/TEST.md` (v0.2.1) — Quality gates

---

## 1. Agentic Architecture

### 1.1 Design Scope and Constraints

Before defining agents, the following architecture constraints from the baseline
**must not be violated**:

| Constraint | Source | Rule |
| ---------- | ------ | ---- |
| GA-only services on MVP critical path | `AR-D-006`, `docs/AI.md` | No preview-only services for regulated data |
| Agent runtime is application-hosted | `docs/AI.md §GA Service Baseline` | Not Foundry-hosted agent resources |
| PHI inference only in Swiss regions | `AR-D-003`, `AR-D-004` | Switzerland North / West, Standard or Regional Provisioned only |
| React web app is mandatory MVP channel | `AR-D-005` | No M365 Copilot dependency at MVP |
| No autonomous closed-loop actuation for clinical decisions | `NFR-AI-001`, `docs/SD.md §1.3` | All patient-affecting actions require human confirmation |
| Advisory-only AI responses | `NFR-AI-001` | Copilot outputs do not replace human operational authority |

---

### 1.2 Agent Set — First Production-Oriented MVP Agents

Eight agents form the MVP agent set. They are organized into three tiers:
**Orchestration**, **Specialist Domain**, and **Governance**.

```text
┌─────────────────────────────────────────────────────────────────┐
│  ORCHESTRATION TIER                                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Operations Orchestrator Agent (OOA)                   │    │
│  │  Central planner: intent decomposition, guardrail      │    │
│  │  enforcement, response synthesis                       │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  SPECIALIST DOMAIN TIER                  GOVERNANCE TIER        │
│  ┌──────────────────────┐  ┌──────────────────────────────┐    │
│  │ Demand Forecasting   │  │ Compliance & Safety Agent    │    │
│  │ Agent (DFA)          │  │ (CSA)                        │    │
│  ├──────────────────────┤  ├──────────────────────────────┤    │
│  │ Discharge Coord.     │  │ Explainability & Audit       │    │
│  │ Agent (DCA)          │  │ Agent (EAA)                  │    │
│  ├──────────────────────┤  ├──────────────────────────────┤    │
│  │ Bed Mgmt Copilot     │  │ Data Quality & Semantics     │    │
│  │ Agent (BMCA)         │  │ Agent (DQSA)                 │    │
│  ├──────────────────────┤  └──────────────────────────────┘    │
│  │ Integration Workflow │                                       │
│  │ Agent (IWA)          │                                       │
│  └──────────────────────┘                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

#### Agent 1: Operations Orchestrator Agent (OOA)

| Attribute | Definition |
| --------- | ---------- |
| **ID** | AGT-001 |
| **Tier** | Orchestration |
| **Primary Role** | Central planner and response synthesizer |
| **Responsibility** | Decomposes user intent into an execution plan; coordinates specialist agents as tools; aggregates typed results; enforces guardrails before synthesis |
| **Inputs** | User request (intent), session context, policy state, role identity |
| **Outputs** | Execution plan, aggregated response with citations, escalation route, action confirmation request |
| **Human Oversight Point** | Operations lead must confirm any high-impact multi-agent action before execution |
| **PRD Coverage** | `FR-CX-001`, `FR-CX-002`, `FR-CX-003`, `FR-GOV-001`, `NFR-AI-001`, `NFR-AI-004` |
| **Compliance Controls** | `CH-C03` (traceability), `CH-C10` (AI oversight) |

**Responsibilities in detail:**

1. Parse incoming intent and classify as: information query, recommendation request, or action trigger.
2. Build a typed execution plan referencing which specialist agents are invoked and in what sequence or parallel.
3. Apply pre-execution policy check via the Compliance and Safety Agent before any side-effecting step.
4. Collect typed results from specialist agents and assemble a grounded response.
5. Invoke Explainability and Audit Agent to attach evidence bundle before returning output.
6. Surface a human confirmation prompt for any action-class response (not advisory-only).

---

#### Agent 2: Demand Forecasting Agent (DFA)

| Attribute | Definition |
| --------- | ---------- |
| **ID** | AGT-002 |
| **Tier** | Specialist Domain |
| **Primary Role** | 72-hour admission pressure forecasting |
| **Responsibility** | Queries the AML forecast pipeline; retrieves latest scored outputs; enriches with specialty and time-bucket segmentation; attaches run provenance |
| **Inputs** | Historical arrivals, seasonality data, external signals (calendar, public holidays), Fabric curated capacity dataset |
| **Outputs** | Forecast table (specialty × time bucket), confidence intervals, drift indicators, run identifier, model version |
| **Human Oversight Point** | Capacity manager reviews forecast deltas before incorporating into staffing or transfer decisions |
| **PRD Coverage** | `FR-FC-001`, `FR-FC-002`, `FR-FC-003`, `FR-FC-004`, `FR-FC-005`, `FR-FC-006` |
| **Compliance Controls** | `CH-C03` (model run traceability), `CH-C10` (AI oversight for high-impact forecast) |

**Responsibilities in detail:**

1. On schedule trigger (hourly) or on-demand from OOA: retrieve the latest AML forecast run output from the Fabric curated serving view.
2. Validate run metadata: run ID, model version, execution timestamp against the AI output contract `DC-AI-FORECAST-v1`.
3. Segment outputs by specialty and time window as required by `FR-FC-002`.
4. Detect and flag confidence degradation or drift indicators that exceed SLO thresholds.
5. Return a typed forecast result including grounding citations to source data and model run provenance.
6. Publish forecast outputs to Power BI operational views per `FR-FC-004`.

---

#### Agent 3: Discharge Coordination Agent (DCA)

| Attribute | Definition |
| --------- | ---------- |
| **ID** | AGT-003 |
| **Tier** | Specialist Domain |
| **Primary Role** | Discharge readiness identification and partner coordination preparation |
| **Responsibility** | Queries AML discharge scoring; ranks candidate patients; identifies blockers; prepares downstream coordination workflow triggers |
| **Inputs** | Clinical progression signals (KIS-derived), bed-state events, pathway constraints, partner availability context |
| **Outputs** | Ranked discharge candidates, blocker reasons with explanatory factors, readiness scorecard, downstream workflow trigger payload |
| **Human Oversight Point** | Clinician validates candidates and explicitly approves downstream coordination actions before IWA is invoked |
| **PRD Coverage** | `FR-DC-001`, `FR-DC-002`, `FR-DC-003`, `FR-DC-004`, `FR-DC-005`, `FR-DC-006` |
| **Compliance Controls** | `CH-C03` (traceability), `CH-C07` (EPR consent/access where applicable), `CH-C10` (AI oversight with mandatory human-in-the-loop) |

**Responsibilities in detail:**

1. On scheduled rescore cadence (up to 48 runs/day plus event-triggered delta) or on-demand: retrieve latest AML discharge scoring output.
2. Validate run metadata against AI output contract `DC-AI-FEATURES-v1`.
3. Rank inpatients by discharge readiness score; apply explanatory factor extraction for top candidates.
4. Identify and tag blockers (e.g., pending diagnostic results, social care plan missing, rehabilitation slot unavailable).
5. Prepare a typed workflow trigger payload for the Integration Workflow Agent — but **do not invoke IWA directly**; submit candidate list to OOA for human approval routing.
6. Maintain an explanation bundle per candidate that supports clinician review and audit requirements.

---

#### Agent 4: Bed Management Copilot Agent (BMCA)

| Attribute | Definition |
| --------- | ---------- |
| **ID** | AGT-004 |
| **Tier** | Specialist Domain |
| **Primary Role** | Conversational decision support for real-time capacity optimization |
| **Responsibility** | Handles the conversational interaction surface; grounds responses in live operational data, forecast outputs, and discharge signals; presents bottleneck explanations and recommended options |
| **Inputs** | Live capacity state (Fabric serving view), forecast output (from DFA), discharge candidates (from DCA), policy constraints, user conversation context |
| **Outputs** | Grounded conversational response with cited sources and timestamps, recommended operational options, impact simulation, action confirmation request |
| **Human Oversight Point** | Operations team explicitly confirms any transfer/prioritization recommendation before it becomes a trigger |
| **PRD Coverage** | `FR-CX-001`, `FR-CX-002`, `FR-CX-003`, `FR-CX-004`, `FR-CX-006` |
| **Compliance Controls** | `CH-C03` (response traceability), `CH-C10` (advisory boundary enforcement) |

**Responsibilities in detail:**

1. Receive user intent from OOA; classify as status query, recommendation request, or action request.
2. Retrieve grounding context from Fabric copilot grounding serving view per contract `DC-GRD-CONTEXT-v1`.
3. Call Azure OpenAI (Standard/Regional Provisioned, Switzerland region only) with a role-aware system prompt and cited grounding context.
4. Return a grounded response with inline citations, source timestamps, and response ID.
5. For recommendation-class responses: include confidence level, alternative options, and an explicit "confirm to act" prompt.
6. Enforce advisory framing: no response shall instruct an action without a human confirmation step.
7. Persist prompt, context snapshot, response ID, and user role to the audit store (Cosmos DB / Azure SQL).

---

#### Agent 5: Integration Workflow Agent (IWA)

| Attribute | Definition |
| --------- | ---------- |
| **ID** | AGT-005 |
| **Tier** | Specialist Domain |
| **Primary Role** | Downstream partner coordination execution and tracking |
| **Responsibility** | Translates approved discharge actions into outbound Logic Apps workflow triggers; tracks acknowledgements; handles retries and dead-letters; surfaces unresolved exceptions |
| **Inputs** | Approved discharge actions (human-confirmed), partner routing rules, Service Bus queue state |
| **Outputs** | Outbound workflow events, partner acknowledgement status, retry/exception status, dead-letter escalation alerts |
| **Human Oversight Point** | Care coordinator supervises unresolved exceptions and provides manual override instructions |
| **PRD Coverage** | `FR-DATA-007`, `FR-DC-003`, `FR-DC-004`, `FR-GOV-005` |
| **Compliance Controls** | `CH-C03` (full outbound/inbound event audit log), `CH-C05` (partner endpoint boundary enforcement) |

**Responsibilities in detail:**

1. Receive approved action payload from OOA only after human confirmation gate is recorded.
2. Publish outbound coordination event to Service Bus with correlation ID linking to discharge candidate and approval event.
3. Invoke Azure Logic Apps workflow for partner-specific routing (Spitex, rehabilitation, social care).
4. Monitor for acknowledgement callbacks and write outcomes to the partner integration events domain in Fabric.
5. Implement idempotent retry with exponential backoff for transient partner endpoint failures.
6. Escalate to dead-letter handling with operational alert after max retry exhaustion.
7. Emit a full audit event record for every outbound and inbound exchange.

---

#### Agent 6: Data Quality and Semantics Agent (DQSA)

| Attribute | Definition |
| --------- | ---------- |
| **ID** | AGT-006 |
| **Tier** | Governance |
| **Primary Role** | Feed quality monitoring and semantic contract integrity enforcement |
| **Responsibility** | Monitors operational feed quality against data contracts; detects schema drift and SLA breaches; issues remediation suggestions to the data steward |
| **Inputs** | Source feed telemetry, schema contracts (DC-ING-*, DC-CUR-*), lineage metadata from Fabric/Purview |
| **Outputs** | Data quality alert, schema drift alert, contract breach report, remediation suggestion |
| **Human Oversight Point** | Data steward approves all corrective data interventions |
| **PRD Coverage** | `NFR-DQ-001`, `NFR-DQ-002`, `NFR-DQ-003`, `NFR-DQ-004` |
| **Compliance Controls** | `CH-C01` (purpose and minimization governance), `CH-C03` (traceability) |

**Responsibilities in detail:**

1. On event-stream and scheduled triggers: validate ingestion contract conformance for ADT, ED, bed-state, and discharge feeds.
2. Run completeness, timeliness, valid-range, and uniqueness checks per contract `DC-ING-ADT-v1` and related contracts.
3. Detect schema drift between current schema and pinned contract version; emit drift alert.
4. Score data quality against SLO thresholds; write quality scorecard to governance evidence domain.
5. Surface remediation suggestions to the data steward (e.g., missing required field, upstream system outage).
6. Block AI pipelines from consuming feeds with critical quality failures until cleared by steward.

---

#### Agent 7: Compliance and Safety Agent (CSA)

| Attribute | Definition |
| --------- | ---------- |
| **ID** | AGT-007 |
| **Tier** | Governance |
| **Primary Role** | Pre-execution policy gate and safety guardrail |
| **Responsibility** | Evaluates every side-effecting action against the current policy set (Swiss data law, role-based rules, AI safety thresholds) before execution is permitted |
| **Inputs** | User identity, action intent and payload, legal policy set, AI model risk rules, session context |
| **Outputs** | Allow / Deny decision with reason code, exception request record, evidence artifact |
| **Human Oversight Point** | Privacy/security owner reviews and approves any policy exception |
| **PRD Coverage** | `FR-GOV-005`, `FR-GOV-006`, `NFR-COMP-007`, `NFR-AI-001`, `NFR-AI-005` |
| **Compliance Controls** | `CH-C01` (purpose limitation), `CH-C02` (privacy by design), `CH-C05` (cross-border deny-by-default), `CH-C10` (AI oversight) |

**Responsibilities in detail:**

1. On every side-effecting action invocation: receive action type, payload, and user context from OOA.
2. Evaluate against policy rule set:
   - PHI cross-border transfer: default deny unless approved runbook is active.
   - Deployment-type restriction: block Global / Data Zone / Developer types for PHI inference.
   - Role authorization: verify the requesting user's role permits the intended action.
   - AI safety threshold: check confidence scores and model risk flags before discharge or transfer actions.
3. Return Allow with reason code, or Deny with reason code and required remediation path.
4. Emit an evidence artifact for every decision (allow and deny) to the governance audit store.
5. For policy exception requests: open a compliance exception record requiring elevated approval.

---

#### Agent 8: Explainability and Audit Agent (EAA)

| Attribute | Definition |
| --------- | ---------- |
| **ID** | AGT-008 |
| **Tier** | Governance |
| **Primary Role** | Traceability evidence generation and audit trail management |
| **Responsibility** | Produces explanation bundles for every forecast, discharge, and copilot recommendation; maintains the end-to-end audit trail from source event to user-facing output and any triggered action |
| **Inputs** | Model metadata and run IDs, retrieval citations and context snapshots, workflow event records |
| **Outputs** | Explanation bundle per recommendation, full audit trail record, evidence artifact for governance review |
| **Human Oversight Point** | Audit/compliance reviewer validates evidence completeness at release and audit cycles |
| **PRD Coverage** | `FR-GOV-001`, `FR-GOV-004`, `NFR-AI-002`, `NFR-AI-003`, `NFR-AI-004` |
| **Compliance Controls** | `CH-C03` (end-to-end traceability), `CH-C10` (AI oversight evidence) |

**Responsibilities in detail:**

1. On every recommendation or action trigger: collect model run ID, version, execution timestamp, confidence score, and contributing feature signals.
2. Collect retrieval citations: source dataset references, grounding context snapshot, and retrieval timestamp.
3. Compose a typed explanation bundle including: what was recommended, why (contributing factors), how confident (score and thresholds), which data was used (citations), and when (timestamps).
4. Persist the bundle to the AI and decision trace domain in Fabric (retention class R3: 24 months).
5. Emit a structured audit trail event linking source event → model output → recommendation → human decision → action trigger.
6. Support compliance review queries: surface evidence bundles for sampled recommendations on request.

---

### 1.3 Agent Interaction Patterns

#### Pattern A: Synchronous Query Path (Operator asks a question)

This is the primary interactive path serving the 120 peak concurrent users
at a P95 response target under 4 seconds.

```text
Operator (React UI)
  │
  ▼
[1] Bed Management Copilot Agent (BMCA)
    → Intent classification
  │
  ▼
[2] Operations Orchestrator Agent (OOA)
    → Build execution plan
    → Parallel: invoke DFA + DCA as tools
  │
  ├──────────────────────────────────────┐
  ▼                                      ▼
[3a] Demand Forecasting Agent (DFA)    [3b] Discharge Coordination Agent (DCA)
     → Retrieve forecast output              → Retrieve discharge candidates
     → Return typed result                   → Return typed result
  │                                      │
  └──────────────────────────┬───────────┘
                             ▼
[4] Compliance & Safety Agent (CSA)
    → Policy evaluation on assembled context
    → Return: Allow / advisory constraint
                             │
                             ▼
[5] Explainability & Audit Agent (EAA)
    → Attach citations, run metadata, response ID
                             │
                             ▼
[6] BMCA assembles grounded advisory response
    → Return response with citations and timestamps
                             │
                             ▼
[7] Operator receives advisory response in React UI
    → For action-class responses: confirmation prompt shown
```

**Latency budget for P95 < 4 seconds:**

| Step | Target Duration |
| ---- | --------------- |
| BMCA intent parse + OOA plan | 100 ms |
| DFA + DCA parallel retrieval (cache hit) | 300 ms |
| DFA + DCA parallel retrieval (cache miss) | 800 ms |
| CSA policy check | 150 ms |
| Azure OpenAI inference (Switzerland region) | 1500–2500 ms |
| EAA citation assembly + response packaging | 200 ms |
| Network + frontend rendering | 200 ms |
| **Total (cache miss, 95th percentile)** | **~4 seconds** |

Redis cache hit on grounding context (session-scoped and ward-scoped)
is the primary latency lever; cache miss must not push P95 beyond threshold.

---

#### Pattern B: Asynchronous Event Path (New operational event arrives)

This path handles the 180,000 events/day baseline with 3× burst headroom.

```text
Hospital Source Systems (KIS, ADT, ED, Bed-state)
  │
  ▼
[1] Fabric ingestion and normalization pipeline
    → Raw event → Curated operational dataset
  │
  ▼
[2] Data Quality & Semantics Agent (DQSA)
    → Validate feed against ingestion contract
    → Allow → continue; Deny → alert data steward
  │
  ▼
[3] Event router (Service Bus / Fabric eventstream)
    → Route to relevant specialist agents
  │
  ├──────────────────────┬─────────────────────────┐
  ▼                      ▼                         ▼
[4a] DFA               [4b] DCA                  [4c] BMCA context refresh
     → Recompute             → Rescore                  → Invalidate grounding
       forecast                discharge                  cache for affected
       outputs                 candidates                 ward/specialty
  │                      │                         │
  └──────────┬───────────┘─────────────────────────┘
             ▼
[5] EAA
    → Persist updated run artifacts and lineage
  │
  ▼
[6] If DCA identifies approved-candidate + approved action:
    → Submit to OOA for human approval routing
  │
  ▼
[7] Human approval (Care coordinator)
  │
  ▼
[8] CSA policy check
  │
  ▼
[9] IWA executes partner workflow
  │
  ▼
[10] EAA persists full event-to-action audit trail
```

---

#### Pattern C: Policy Exception Path

When CSA issues a Deny decision and an operator requests an exception:

```text
Operator requests policy exception
  │
  ▼
CSA opens exception record (reason code, context snapshot, risk assessment)
  │
  ▼
Exception routed to Privacy/Security Owner via Service Bus notification
  │
  ▼
Owner reviews evidence and approves / rejects
  │
  ├── Approved → CSA issues time-bounded exception token;
  │              OOA re-evaluates plan; EAA records exception grant
  │
  └── Rejected → Operator receives deny with explanation;
                 EAA records final deny evidence artifact
```

---

### 1.4 Human-in-the-Loop Decision Gates

The following gates are **mandatory** for MVP and **cannot be bypassed**:

| Gate ID | Trigger Condition | Required Approver | Agent Involved |
| ------- | ----------------- | ----------------- | -------------- |
| HITL-01 | Any patient-affecting workflow trigger (discharge coordination, partner notification) | Clinician | DCA → OOA → Human |
| HITL-02 | Bed transfer or resource reprioritization recommendation | Operations lead or charge nurse | BMCA → OOA → Human |
| HITL-03 | Cross-organizational handoff initiation (Spitex, rehab, social care) | Care coordinator | IWA (pre-invocation) |
| HITL-04 | Policy exception request (CSA deny overrule) | Privacy/security owner | CSA |
| HITL-05 | Forecast-driven staffing or capacity reallocation | Capacity manager | DFA → OOA → Human |

> **Principle:** No agent invokes a side-effecting action (IWA, external partner call,
> data write beyond telemetry) without a human confirmation event being recorded.
> This satisfies `NFR-AI-001` and `CH-C10`.

---

### 1.5 Orchestration Model

#### Decision: Hybrid Centralized Planner with Decentralized Execution

This follows the `Planner-Executor` pattern from the Microsoft Agent Framework reference.

| Concern | Model | Rationale |
| ------- | ----- | --------- |
| Intent decomposition | Centralized (OOA) | Single governance point for plan construction and guardrail application |
| Response synthesis | Centralized (OOA) | Single authority for aggregating typed results and enforcing advisory framing |
| Specialist execution | Decentralized | Each agent executes bounded task independently and returns typed result |
| Policy enforcement | Centralized (CSA as mandatory gate) | All side-effect paths run through one policy engine |
| Audit evidence | Decentralized (EAA called by OOA) | Evidence generation is triggered centrally but composed from distributed agent outputs |

This hybrid avoids monolithic complexity (single-agent bottleneck), while preserving
consistent governance and traceability. It directly supports post-MVP extensibility:
adding a new specialist agent requires only registering its tool contract with OOA.

---

## 2. Technical Architecture

### 2.1 Layered Service Architecture

```text
┌──────────────────────────────────────────────────────────────────────┐
│  EXPERIENCE LAYER                                                    │
│  React Operations Channel (Azure App Service / Static Web Apps)     │
│  Role-aware UI, copilot chat, action confirmation flows             │
│  Entra-authenticated sessions, full interaction telemetry           │
└──────────────────────────────────────┬───────────────────────────────┘
                                       │ HTTPS / REST
┌──────────────────────────────────────▼───────────────────────────────┐
│  API AND AGENT RUNTIME LAYER                                         │
│  Azure Container Apps (6 min / 20 max replicas, 1 vCPU / 2 GiB)   │
│  OOA, BMCA, DFA, DCA → synchronous path (HTTP API)                  │
│  IWA, DQSA, CSA, EAA → worker path (Container Apps jobs/workers)    │
│  Azure Cache for Redis — session-scoped and ward-scoped grounding    │
│  Azure Cosmos DB / Azure SQL — conversation, audit, action logs      │
│  Azure Service Bus — async orchestration and partner event routing   │
└──────────────────┬──────────────────────────┬────────────────────────┘
                   │                          │
       ┌───────────▼──────────┐  ┌────────────▼───────────────────────┐
       │  AI DECISIONING      │  │  DATA PLATFORM LAYER               │
       │  LAYER               │  │  Microsoft Fabric + OneLake        │
       │                      │  │  (Switzerland North primary)       │
       │  Azure OpenAI        │  │                                    │
       │  (Standard/Regional  │  │  Raw zone → Bronze → Silver →      │
       │  Provisioned,        │  │  Gold (serving)                    │
       │  Switzerland North)  │  │                                    │
       │                      │  │  Semantic models for dashboards    │
       │  Azure Machine       │  │  and copilot grounding             │
       │  Learning            │  │                                    │
       │  (Forecast pipeline, │  │  Azure Health Data Services        │
       │  Discharge scoring)  │  │  FHIR normalization + healthcare   │
       │                      │  │  payload governance                │
       └──────────────────────┘  └────────────────────────────────────┘
                                            │
                         ┌──────────────────▼───────────────────────┐
                         │  INTEGRATION LAYER                       │
                         │  Azure Logic Apps (partner workflows)    │
                         │  Service Bus (reliable messaging)        │
                         │  Partner endpoints: Spitex, Rehab,       │
                         │  Social care                             │
                         └──────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  GOVERNANCE AND SECURITY LAYER (cross-cutting)                      │
│  Microsoft Entra ID + Managed Identity + PIM                        │
│  Azure Key Vault (secretless runtime)                               │
│  Azure Policy (region enforcement, deployment-type restrictions)    │
│  Azure Monitor + Log Analytics + Application Insights               │
│  Microsoft Purview (metadata, lineage, governance evidence)         │
└──────────────────────────────────────────────────────────────────────┘
```

---

### 2.2 Microsoft Service-to-Agent Mapping

| Agent | Primary Azure / Microsoft Service(s) | Runtime Model |
| ----- | ------------------------------------- | ------------- |
| OOA | Azure Container Apps (HTTP API) | Synchronous, stateless per turn |
| BMCA | Azure Container Apps + Azure OpenAI | Synchronous; OpenAI Switzerland Standard |
| DFA | Azure Container Apps + Azure Machine Learning | On-demand retrieval + AML scoring endpoint |
| DCA | Azure Container Apps + Azure Machine Learning | Scheduled rescore + event-triggered delta |
| IWA | Container Apps worker + Logic Apps + Service Bus | Asynchronous, queue-driven |
| DQSA | Container Apps job (triggered by Fabric pipeline events) | Event-triggered batch |
| CSA | Container Apps (sidecar pattern on action path) | Synchronous gate, <150 ms SLO |
| EAA | Container Apps worker + Cosmos DB / Azure SQL | Asynchronous, event-driven |

---

### 2.3 Detailed Data Flow

#### Ingestion to Serving (Data Platform)

```text
KIS / EHR / ADT / ED / Bed Management / Staffing systems
  │  (HL7 v2, FHIR R4, operational API feeds)
  ▼
Azure Health Data Services (FHIR normalization gateway)
  │
  ▼
Microsoft Fabric — Raw/Bronze zone (OneLake)
  │  Schema validation per DC-ING-ADT-v1 and related contracts
  │  DQSA monitors quality here
  ▼
Fabric Medallion Pipeline (Silver curation)
  │  Joins, deduplication, standard fields, classification tags
  │  PHI fields isolated to PHI-classified partitions
  ▼
Fabric Gold / Serving zone
  │  Semantic models for Power BI
  │  Copilot grounding views (DC-GRD-CONTEXT-v1)
  │  AI feature datasets (DC-AI-FEATURES-v1)
  ▼
Azure Machine Learning
  │  Forecast pipeline (hourly, outputs DC-AI-FORECAST-v1)
  │  Discharge scoring pipeline (48×/day + event delta)
  ▼
Fabric AI output serving views
  │
  ▼
Agent retrieval layer (DFA, DCA, BMCA grounding)
```

#### Agent Runtime to Audit Store

```text
Agent action (any tier)
  │
  ▼
EAA event collection:
  - Model run ID + version
  - Retrieval citation snapshot (dataset ref + timestamp)
  - User role and session ID
  - CSA decision record (allow/deny + reason code)
  - Human confirmation event (if applicable)
  │
  ▼
Audit store (Cosmos DB or Azure SQL, R3 retention: 24 months)
  │
  ▼
Purview lineage update (operational metadata, not PHI)
  │
  ▼
Compliance evidence artifacts (E-07: AI safety and oversight report)
```

---

### 2.4 Real-Time vs Batch Processing Split

| Pathway | Mode | Technology | Latency Target |
| ------- | ---- | ---------- | -------------- |
| Operational event ingestion (ED, ADT, bed-state) | Near-real-time | Fabric eventstream / Event Hubs | < 30 seconds end-to-end to Gold |
| Forecast inference | Batch (hourly schedule) | AML pipeline + Fabric | Publish within 15 minutes of trigger |
| Discharge rescoring | Hybrid (scheduled + event-triggered) | AML pipeline | < 10 minutes per event-triggered run |
| Copilot grounding retrieval | Synchronous on-demand | Fabric semantic model + Redis cache | P95 < 800 ms (cache miss) |
| Partner coordination workflow | Asynchronous | Logic Apps + Service Bus | Trigger within 2 minutes of human approval |
| Audit event persistence | Asynchronous | Container Apps worker → Cosmos DB | < 5 seconds after action event |
| DQSA quality check | Event-triggered + scheduled | Container Apps job + Fabric | Alert within 5 minutes of breach |

---

### 2.5 Security and Compliance Architecture (Swiss Healthcare)

#### Data Residency Controls

| Control | Implementation | Compliance Anchor |
| ------- | -------------- | ----------------- |
| PHI data stores in Switzerland regions only | Azure Policy: allowed-locations = {switzerlandnorth, switzerlandwest} | `AR-D-003`, `CH-C05`, `NFR-COMP-004` |
| PHI AI inference in Switzerland regions only | Azure Policy: block Global/DataZone/Developer deployment types | `AR-D-004`, `CH-C05` |
| Cross-region PHI failover default deny | Conditional Access + compliance runbook gate | `AR-D-003`, `CH-C05`, `NFR-COMP-007` |
| Non-PHI services (monitoring, identity) | Broad region availability acceptable | Standard Azure posture |

#### Identity Architecture (Zero Trust)

```text
Operations User
  │  Entra ID MFA + Conditional Access
  ▼
React Frontend (App Service)
  │  Entra App Registration, role-based token
  ▼
API Gateway / Container Apps
  │  Token validation, role extraction, session ID
  ▼
Agent Runtime (OOA, BMCA, etc.)
  │  Managed Identity → downstream access
  ▼
Data/AI Services (Fabric, AML, OpenAI)
  │  Resource-scoped RBAC, no static secrets
  ▼
Key Vault (secrets, model endpoint keys)
```

All workloads use **Managed Identity** — no embedded credentials per `NFR-SEC-004`
and `CH-C02`. Human admin access uses **PIM JIT elevation** per `docs/SECURITY.md`.

#### Audit Chain for Agent Actions

Every agent action produces a traceable chain:

```text
Source event ID
  → Ingestion correlation ID
    → Curated dataset version + partition
      → AI run ID + model version
        → OOA execution plan ID
          → Agent tool invocation ID
            → CSA decision record ID
              → Human confirmation event ID (if applicable)
                → IWA workflow correlation ID
                  → Partner acknowledgement ID
                    → EAA evidence bundle ID
```

This chain satisfies `FR-GOV-001`, `NFR-AI-003`, `NFR-AI-004`, `CH-C03`.

---

### 2.6 Observability Architecture

| Signal Type | Tool | Key Metrics |
| ----------- | ---- | ----------- |
| Application telemetry | Application Insights | Request latency P50/P95/P99, error rates by route, dependency latency |
| Agent-specific events | Application Insights custom events | Agent invocation count, plan execution time, CSA allow/deny ratio |
| Model pipeline health | AML telemetry + Log Analytics | Run success rate, inference latency, model drift metrics |
| Grounding cache | Redis metrics | Hit ratio, memory pressure, eviction rate |
| Integration reliability | Service Bus + Logic Apps metrics | Queue depth, dead-letter growth, workflow success rate |
| PHI compliance signals | Azure Monitor + Policy | Cross-border attempt count (target: 0), region policy violations |
| AI quality | Application Insights custom metrics | Citation coverage rate, hallucination flag rate (sampled), advisory boundary adherence |

SLO dashboard: centralized Azure Monitor Workbook with views for platform, data,
AI, integration health, and governance KPIs per `docs/OPERATIONS.md §SLI and SLO`.

---

## 3. Design Patterns

### 3.1 Agent Design Patterns

#### Pattern 1: Planner-Executor

**Where:** OOA (Planner) → DFA, DCA, BMCA, IWA, CSA, EAA (Executors)

**Structure:**
- Planner receives intent; constructs a typed execution plan.
- Planner invokes executors as tools via well-defined typed contracts.
- Planner aggregates typed results; applies synthesis and response framing.
- Planner does not embed domain logic — specialist agents own their domain.

**Why chosen:** Centralizes governance and explainability while allowing independent
specialist evolution. Supports incremental onboarding of new agents post-MVP without
re-architecting OOA (add new tool contract only).

**Reference:** Microsoft Agent Framework — `AutoGen` / `Semantic Kernel` planner
patterns; see reference §7.

---

#### Pattern 2: Retrieval-Grounded Advisory

**Where:** BMCA → Azure OpenAI + Fabric grounding serving view

**Structure:**
- BMCA retrieves relevant context from governed Fabric serving views.
- Context is injected into the Azure OpenAI prompt as grounding documents with source citations.
- Model response is constrained by system prompt to be advisory only.
- Citations from grounding documents are propagated into the user-visible response.

**Why chosen:** Prevents hallucination of clinical or operational facts; every
user-visible claim traces to a retrievable governed source. Satisfies `NFR-AI-002`
and `CH-C10`.

**Implementation note:** Use Redis cache for ward-scoped and session-scoped grounding
to meet the P95 < 4 s response objective.

---

#### Pattern 3: Policy-Guarded Tool Invocation

**Where:** CSA sits on every side-effecting action path, invoked by OOA before any
write or trigger.

**Structure:**
- Action intent + payload is submitted to CSA before execution.
- CSA evaluates against policy rule set (PHI rules, role rules, AI safety thresholds).
- CSA returns Allow + reason or Deny + reason + exception path.
- Only on Allow does OOA proceed to invoke the side-effecting agent (IWA, etc.).

**Why chosen:** Separates policy enforcement from domain logic. Policy changes do not
require modifying specialist agents. Single audit point for every governed action.
Satisfies `FR-GOV-005`, `CH-C02`, `CH-C05`.

---

#### Pattern 4: Event-Driven Recompute

**Where:** DQSA, DFA, DCA → triggered by Fabric eventstream / Service Bus

**Structure:**
- Operational state change event arrives on Service Bus / Fabric eventstream.
- DQSA validates feed quality; if quality passes, routes to specialist agents.
- DFA and/or DCA recompute outputs for affected specialty/ward.
- BMCA grounding cache is invalidated for affected context window.

**Why chosen:** Ensures operational staff always see fresh intelligence without manual
refresh. Aligns with `NFR-PERF-001` (near-real-time updates) and `NFR-PERF-003`
(multiple discharge rescorings per day).

---

#### Pattern 5: Human-Approval Side-Effect

**Where:** All action-class paths before IWA invocation.

**Structure:**
- Agent recommendation is presented to the human operator with an explicit
  "Confirm to act" interaction in the React UI.
- The human confirmation event is recorded as a durable event (Cosmos DB) with:
  timestamp, user identity, role, action description, and confirmation type.
- Only after the confirmation event is persisted does OOA invoke IWA.
- The confirmation event is part of the EAA audit chain.

**Why chosen:** Mandatory for clinical and operational safety under `NFR-AI-001`
and FADP human oversight obligations (`CH-C10`). Also the primary risk mitigation
for model drift and policy misconfiguration scenarios.

---

#### Pattern 6: Degraded-Mode Graceful Fallback

**Where:** BMCA, DFA, DCA — when upstream dependency (AML pipeline, Fabric serving
view, Redis) is unavailable.

**Structure:**
- Each agent defines a degraded-mode contract:
  - DFA unavailable: BMCA presents last-known forecast with a staleness warning;
    no new capacity recommendations until refresh.
  - DCA unavailable: BMCA presents last-known discharge candidates with staleness
    indicator; coordination workflows paused.
  - Redis unavailable: BMCA falls back to direct Fabric query (higher latency;
    P95 SLO relaxed to 8 s in degraded mode).
  - Azure OpenAI unavailable: BMCA returns dashboard fallback with pre-computed
    summary rather than conversational response.
- All degraded-mode activations are logged as operational events and surfaced in the
  monitoring workbook.

**Why chosen:** `NFR-REL-003` requires graceful degradation; `docs/SD.md §Design
Principles` requires degraded-mode support over hard failure where clinically safe.

---

### 3.2 Data and Integration Patterns

#### Pattern 7: Medallion-Style Curation (Fabric)

Four-zone OneLake structure:

| Zone | Name | Purpose | PHI Handling |
| ---- | ---- | ------- | ------------ |
| Z1 | Raw/Bronze | Landing zone: source-as-received | PHI retained, full-fidelity |
| Z2 | Silver | Normalized, validated, deduplicated | PHI minimized per use case |
| Z3 | Gold | Curated domain products | PHI isolated to classified partitions |
| Z4 | Serving | Semantic models, copilot grounding views | PHI stripped or pseudonymized for AI grounding |

AI models and copilot grounding consume only from Z4 (Serving) unless a specific
clinical feature requires PHI-classified Gold data under explicit purpose control.

---

#### Pattern 8: Contract-First Schema Governance

All producer-to-consumer boundaries use versioned contracts per `docs/DATA.md §Data
Contracts`. For the agent set, the following contracts are mandatory at MVP:

| Contract ID | Agent Consumers | Purpose |
| ----------- | --------------- | ------- |
| `DC-ING-ADT-v1` | DQSA | ADT/ED ingestion schema and quality rules |
| `DC-CUR-CAPACITY-v1` | DFA, DCA, BMCA | Curated capacity model |
| `DC-AI-FEATURES-v1` | DFA, DCA | Feature set for model inputs with lineage |
| `DC-AI-FORECAST-v1` | DFA, OOA | Forecast output schema and run metadata |
| `DC-INT-DISCHARGE-v1` | IWA | Outbound/inbound partner workflow payloads |
| `DC-GRD-CONTEXT-v1` | BMCA | Grounding context and citation metadata |

Breaking contract changes require migration plan and elevated approval per `NFR-DQ-003`.

---

#### Pattern 9: Outbox with Reliable Messaging (Integration)

For all outbound partner coordination events:

1. IWA writes the action intent to a durable outbox table in Cosmos DB before
   dispatching to Service Bus.
2. Service Bus delivers the message to the Logic Apps workflow.
3. On acknowledgement, the outbox record is marked complete.
4. On failure after max retries, the record moves to dead-letter with alert.
5. Idempotency is enforced via deterministic correlation IDs (source event ID +
   discharge candidate ID + action type).

This satisfies `NFR-DQ-004` (no silent data loss on integration failures) and
`NFR-REL-004` (retry and exception handling).

---

#### Pattern 10: Semantic Serving View Alignment

Fabric semantic models in Z4 are designed so that:

- Dashboard visuals (Power BI) and copilot grounding context are served from
  **the same semantic model** — preventing metric divergence between what an
  operator sees in the dashboard and what the copilot describes.
- This satisfies `FR-CX-005` (Power BI views) and `FR-CX-002` (grounded copilot
  answers) with a shared grounding source.

---

## 4. Bill of Materials (BOM)

### 4.1 Mandatory Components (MVP)

| Category | Component | Role in Agent Architecture | Environment |
| -------- | --------- | -------------------------- | ----------- |
| Data platform | Microsoft Fabric (GA workloads only) | Medallion curation, semantic models, grounding views, AI feature serving | Switzerland North primary |
| Data platform | OneLake | All-zone data lake for raw-to-serving lifecycle | Switzerland North primary |
| Healthcare interoperability | Azure Health Data Services (FHIR) | Healthcare payload normalization gateway | Switzerland North — validate GA before go-live |
| Agent runtime | Azure Container Apps | Hosts all 8 agents (sync API + async worker paths) | Switzerland North |
| Agent runtime | Azure Cache for Redis (Standard, zone-redundant) | Session-scoped and ward-scoped grounding cache | Switzerland North |
| AI platform | Azure OpenAI (Standard or Regional Provisioned) | BMCA inference; PHI paths only in Switzerland regions | Switzerland North |
| AI platform | Azure Machine Learning | DFA forecast pipeline; DCA discharge scoring pipeline; model lifecycle management | Switzerland North |
| Audit and conversation store | Azure Cosmos DB or Azure SQL | Conversation metadata, CSA decision records, EAA audit bundles | Switzerland North |
| Async orchestration | Azure Service Bus (Premium for isolation) | Event routing between agents; partner event outbox | Switzerland North |
| Integration | Azure Logic Apps | IWA partner workflow execution; acknowledgement callbacks | Switzerland North |
| Experience | React app (Azure App Service or Static Web Apps) | BMCA user interaction surface; action confirmation flows | Switzerland North |
| Identity | Microsoft Entra ID + Managed Identity + PIM | All agent-to-service and user-to-app identity | Multi-region governance plane |
| Secrets | Azure Key Vault | Secretless runtime; model endpoint keys; certificate management | Switzerland North |
| Policy | Azure Policy | Region enforcement; PHI deployment-type restrictions; approved SKU controls | Subscription scope |
| Observability | Azure Monitor + Log Analytics + Application Insights | All agent telemetry; SLO dashboards; CSA audit signals | Switzerland North |
| Governance | Microsoft Purview (hybrid ops model) | Lineage, classification, governance evidence lifecycle | Switzerland North primary |

---

### 4.2 Optional Components (Post-MVP or Controlled Adoption)

| Category | Component | Trigger for Adoption | Risk if adopted early |
| -------- | --------- | -------------------- | --------------------- |
| Secondary operator channel | Microsoft 365 Copilot integration | Post-MVP; when M365 Copilot licensing is in place and grounding API contracts are stable | Adds channel divergence risk; requires shared grounding contract enforcement |
| Semantic intelligence | Fabric IQ Ontology + Data Agents | Post-GA validation in Switzerland region; can reduce semantic drift across agents | Preview-only; blocked by `AR-D-002` until Swiss GA validated |
| Provisioned throughput | Azure OpenAI Provisioned capacity | When sustained 120+ concurrent users sustain high token demand consistently | Higher cost commitment before demand is measured |
| Active-active reliability | Cross-region active-active for non-PHI paths | When PHI failover runbook is approved and tested | PHI paths remain single-region regardless |
| Advanced model serving | Azure AI Foundry-hosted agents | Post-MVP, when Foundry agent hosting reaches GA in Switzerland | Blocked by `docs/AI.md §Constraints` for MVP |

---

### 4.3 High-Level Sizing Guidance

Based on the demand baseline from `docs/BVA.md` and `docs/ARCHITECTURE.md §NFR Stress Test`:

#### Azure Container Apps (Agent Runtime)

| Pool | Minimum Replicas | Maximum Replicas | Instance Size | Scale Trigger |
| ---- | ---------------- | ---------------- | ------------- | ------------- |
| Sync API (OOA, BMCA, DFA, DCA) | 6 | 20 | 1 vCPU / 2 GiB | HTTP concurrency + CPU ≥ 70% |
| Async Workers (IWA, DQSA, EAA) | 2 | 10 | 1 vCPU / 2 GiB | Service Bus queue depth |
| CSA (sidecar on sync path) | 4 | 12 | 0.5 vCPU / 1 GiB | Co-scaled with sync API |

Minimum replicas held during business hours (06:00–22:00 CET) to maintain warm
startup. Scale-to-zero permitted outside business hours for worker pools.

#### Azure OpenAI

| Scenario | Deployment Type | Capacity Basis |
| -------- | --------------- | -------------- |
| PHI-sensitive copilot inference (Switzerland North) | Standard or Regional Provisioned | 8,000 turns/day; average ~2,000 tokens/turn input+output; provision for 120 peak concurrent → ~240,000 tokens/hour peak |
| Non-PHI internal tasks (grounding pre-processing) | Standard | Lower priority; can tolerate throttling |

Start with Standard and measure TPM consumption before committing to Provisioned.

#### Microsoft Fabric

| Workload | Fabric Capacity Tier | Basis |
| -------- | ------------------- | ----- |
| Ingestion + curation (180,000 events/day + 3× burst) | F64 initial baseline | Validate with SIT load replay before PROD commit |
| Semantic model query load (120 concurrent copilot users + Power BI) | Included in F64; scale to F128 if query latency degrades | Monitor CU utilization per workspace |

#### Azure Cache for Redis

- Standard tier with zone-redundant option (Switzerland North).
- Initial cache size: 6 GB (ward-scoped grounding + session context).
- Monitor memory pressure and hit ratio; scale before hit ratio falls below 80%.

#### Azure Service Bus

- Premium tier (single tenant, predictable throughput, private endpoint support).
- Initial: 1 Messaging Unit; scale to 2 MU if queue latency exceeds SLO threshold.

---

### 4.4 Cost Context (ROM Alignment to BVA)

The BVA (`docs/BVA.md`) estimates **CHF 760,000/year** for Azure and platform
service consumption. The agent architecture adds the following consumption categories
beyond the base data platform:

| Category | ROM Annual Impact |
| -------- | ----------------- |
| Azure OpenAI inference (8,000 turns/day, GPT-4o class) | CHF 140,000–220,000 |
| Container Apps (agent runtime, always-on min replicas) | CHF 80,000–120,000 |
| Redis, Cosmos DB, Service Bus Premium | CHF 40,000–70,000 |
| AML compute (forecast + discharge pipelines) | Included in base platform estimate |
| Net agent platform additive (ROM) | **CHF 260,000–410,000/year** |

This is within the BVA's CHF 760,000/year Azure consumption envelope with room
for Fabric, monitoring, and networking costs.

---

## 5. Trade-offs, Alternatives, and Risks

### 5.1 Key Architectural Decisions and Trade-offs

#### Decision 1: Centralized Planner vs Fully Decentralized Mesh

| Factor | Centralized Planner (chosen) | Fully Decentralized Mesh |
| ------ | ----------------------------- | ------------------------ |
| Governance control | Single OOA enforces all guardrails | Distributed; risk of inconsistent guardrail application |
| Explainability | Single synthesis point for EAA | Fragmented across agents; harder to compose explanation bundles |
| Scalability | OOA is a bottleneck at very high plan complexity | Better horizontal scale for independent tasks |
| Operational complexity | Lower: one orchestration contract to understand | Higher: N² interaction contracts |
| Swiss compliance fit | Strong: policy gate (CSA) sits on one path | Weaker: policy gate must be replicated per-agent |
| **MVP verdict** | **Chosen** | Deferred: reconsider when OOA becomes a latency bottleneck |

---

#### Decision 2: Advisory-Only AI vs Autonomous Optimization

| Factor | Advisory-Only (chosen) | Autonomous Optimization |
| ------ | ----------------------- | ----------------------- |
| Patient safety | High: human always in decision loop | Lower: error propagation without human catch |
| FADP / CH-C10 compliance | Strong: mandatory human oversight for high-impact decisions | Risk: automated-decision transparency and override obligations |
| Clinical trust and adoption | Higher: clinicians retain authority | Requires mature trust-building over longer deployment period |
| Operational speed | Slightly lower: human confirmation adds 30–90 seconds | Higher: immediate execution |
| **MVP verdict** | **Chosen** | Reconsider for low-risk, lower-acuity workflows post-MVP |

---

#### Decision 3: Swiss-Region-Only PHI Inference vs Global Model Routing

| Factor | Swiss-Region Constrained (chosen) | Global Model Routing |
| ------ | ---------------------------------- | -------------------- |
| FADP/DPO compliance | Strong: data does not leave Switzerland | High risk of FADP violation |
| Resilience | Lower: single-region for PHI paths | Higher: global failover |
| Cost | Potentially higher for provisioned capacity | Lower: use cheapest available region |
| Model availability | Limited to Switzerland North; verify model availability before go-live | Access to latest model versions globally |
| **MVP verdict** | **Chosen** | Not permitted for PHI paths per `AR-D-003`, `AR-D-004` |

---

#### Decision 4: Logic Apps + Service Bus vs Custom Orchestration Engine

| Factor | Managed (Logic Apps + Service Bus) (chosen) | Custom Orchestration Code |
| ------ | -------------------------------------------- | -------------------------- |
| Reliability baseline | Built-in; managed retry, DLQ, at-least-once delivery | Requires custom implementation |
| Operational burden | Lower: managed by Microsoft | Higher: team owns runtime, upgrades, incident response |
| Flexibility | Limited to Logic Apps connector ecosystem | Unlimited extensibility |
| Audit logging | Built-in Logic Apps run history | Custom implementation required |
| **MVP verdict** | **Chosen** | Reconsider if Logic Apps connector gaps become blockers |

---

#### Decision 5: Application-Hosted Agents (Container Apps) vs Foundry-Hosted Agents

| Factor | Application-Hosted (Container Apps) (chosen) | Foundry-Hosted Agents |
| ------ | --------------------------------------------- | ---------------------- |
| GA status | GA in Switzerland North | Preview-only or no Swiss GA for agent hosting |
| Provider control | Full control over runtime | Foundry manages agent lifecycle |
| IaC coverage | Full Bicep/Terraform support | Partial: some Fabric items not fully IaC-ready |
| Post-MVP migration path | Clean migration when Foundry GA reaches Switzerland | Start here if Foundry GA arrives post-MVP |
| **MVP verdict** | **Chosen** per `docs/AI.md §Constraints` | Evaluate post-MVP when Swiss Foundry agent hosting is GA-validated |

---

### 5.2 Major Risks and Mitigations

| Risk ID | Risk | Likelihood | Impact | Mitigation |
| ------- | ---- | ---------- | ------ | ---------- |
| R-01 | **Data quality drift from KIS/ADT source feeds** causes incorrect forecast or discharge recommendations | Medium | High | DQSA continuous monitoring; data contract SLA enforcement; DFA/DCA consume only validated Gold data; clinician review gate (HITL-01) |
| R-02 | **Model drift or calibration decay** (forecast or discharge scoring) degrades AI quality over time | Medium | High | AML model drift detection; scheduled retraining cadence; model version rollback playbook; EAA tracks model version per recommendation |
| R-03 | **Azure OpenAI capacity constraints** in Switzerland North for PHI paths at peak concurrency | Medium | Medium | Monitor TPM consumption; pre-scale to Provisioned before sustained peak; degraded-mode fallback (Pattern 6) if capacity exhausted |
| R-04 | **Explainability gaps** in discharge recommendations reduce clinical trust and create governance risk | Low | High | Mandatory explanation bundle (EAA) per recommendation; confidence score and contributing factor disclosure; clinician feedback loop in UI |
| R-05 | **Policy misconfiguration** in CSA leads to non-compliant actions passing the policy gate | Low | Critical | Policy rules stored as versioned code in Git; CI validation of policy rule syntax; CSA test suite with deny-path golden tasks per `docs/TEST.md §Gate 2` |
| R-06 | **Integration partner endpoint instability** delays downstream discharge coordination | High | Medium | Queue-based retries with exponential backoff; dead-letter handling with operational escalation; care coordinator HITL gate for unresolved exceptions |
| R-07 | **Redis cache failure** degrades copilot response latency to P95 > 4 s | Low | Medium | Degraded mode: direct Fabric query with relaxed SLO; zone-redundant Redis; automatic cache warm-up on restart |
| R-08 | **Agent contract changes** (OOA ↔ specialist agents) break live workflows | Medium | High | Versioned typed contracts per agent; backward-compatible change gates in CI; blue/green deployment for contract-breaking changes |
| R-09 | **PHI cross-border exposure** from misconfigured Azure Policy or failover activation | Low | Critical | Default-deny policy enforced by Azure Policy (region + deployment-type restrictions); CSA deny-by-default for cross-border actions; `NFR-COMP-007` operational monitoring |
| R-10 | **Clinical adoption risk**: operational teams do not embed AI recommendations into daily workflow | Medium | High | Human-in-the-loop design builds trust incrementally; copilot response always provides reasoning; value KPIs tracked monthly per `docs/BVA.md` |

---

### 5.3 Architecture Limitations for MVP Scope

1. **No multi-provider shared tenancy:** One provider deployment at a time. The
   agent set must be re-deployed per provider. This is by design per `FR-OM-001`.

2. **No Fabric IQ Ontology:** Semantic consistency between agents relies on shared
   Fabric serving views and typed contracts — not a formal ontology. This is
   acceptable for MVP but may create semantic drift as the platform scales
   to new departments. Ontology onboarding is the primary post-MVP investment.

3. **No autonomous closed-loop actions:** Every side-effecting action requires
   human confirmation. This limits throughput for high-volume, low-risk actions
   (e.g., routine Spitex notifications). Consider tiered automation post-MVP once
   trust and compliance validation accumulate.

4. **Switzerland North capacity dependency:** All PHI-path services are constrained
   to Switzerland North (primary). If Switzerland North experiences regional
   impairment, PHI AI inference is unavailable until the compliance-approved
   runbook activates failover to Switzerland West. This is a deliberate safety posture.

5. **Fabric IQ Data Agents excluded from MVP:** Preview status per `AR-D-002`.
   DQSA and EAA are implemented as custom Container Apps workers using Fabric APIs
   rather than native Fabric Data Agents.

---

## 6. MVP Architecture Readiness Checklist

This design is ready for implementation planning when all criteria are confirmed:

| # | Criterion | Owner | Status |
| - | --------- | ----- | ------ |
| 1 | All 8 agent contracts are defined with typed inputs, outputs, guardrails, and retry policies | AI Engineering Lead | **Design complete — implementation pending** |
| 2 | Human approval gates (HITL-01 to HITL-05) are encoded in React UI and OOA plan logic | App + AI Lead | **Design complete — implementation pending** |
| 3 | Swiss compliance controls (CH-C01–CH-C10) are mapped to enforceable platform policies and Azure Policy assignments | Platform + Compliance Lead | **Partially complete — operationalization tasks remain** |
| 4 | Data quality SLOs and DQSA alert thresholds are operationally owned and defined | Data Platform Lead | **Design complete — SLO values to be set in implementation planning** |
| 5 | Evidence artifacts (EAA bundles, CSA records, audit logs) are automatically generated and linked to release gates | AI Governance + Platform Lead | **Design complete — implementation pending** |
| 6 | Agent golden-task test fixtures are defined for happy-path and failure-mode scenarios | AI Engineering | **Required before first production deployment per `docs/TEST.md §Gate 2`** |
| 7 | Load validation plan is confirmed (40 / 120 / 180 concurrent users) per `docs/AI.md §Load Validation Plan` | SRE + Platform Lead | **Required before MVP go/no-go** |
| 8 | Swiss region service GA validation completed for Azure Health Data Services FHIR in Switzerland North | Platform Lead | **Open: hard deployment gate per `docs/ARCHITECTURE.md`** |

---

## 7. Requirement Traceability Matrix

| Requirement | Agent(s) | Architecture Section |
| ----------- | -------- | ------------------- |
| `FR-FC-001` to `FR-FC-006` | DFA (AGT-002), OOA (AGT-001) | §1.2, §2.3 |
| `FR-DC-001` to `FR-DC-006` | DCA (AGT-003), IWA (AGT-005) | §1.2, §2.3 |
| `FR-CX-001` to `FR-CX-006` | BMCA (AGT-004), OOA (AGT-001) | §1.2, §1.3, §2.1 |
| `FR-GOV-001`, `FR-GOV-004` | EAA (AGT-008) | §1.2, §2.3 |
| `FR-GOV-005`, `FR-GOV-006` | CSA (AGT-007), IWA (AGT-005) | §1.2, §3.1 Pattern 3 |
| `FR-DATA-007` | IWA (AGT-005) | §1.2, §3.2 Pattern 9 |
| `NFR-AI-001` to `NFR-AI-005` | All agents; HITL gates §1.4 | §1.4, §2.5 |
| `NFR-DQ-001` to `NFR-DQ-004` | DQSA (AGT-006) | §1.2, §3.2 |
| `NFR-COMP-004`, `NFR-COMP-007` | CSA (AGT-007), platform policy | §2.5 |
| `NFR-REL-001` to `NFR-REL-004` | All agents; Pattern 6 (degraded mode) | §3.1 Pattern 6 |
| `NFR-PERF-001` to `NFR-PERF-005` | Latency budget §1.3; sizing §4.3 | §2.4, §4.3 |
| `NFR-SEC-001` to `NFR-SEC-004` | Identity architecture §2.5 | §2.5 |
| `CH-C01` to `CH-C10` | CSA, EAA, platform controls | §2.5, compliance controls per agent |

---

## 8. References

### Primary Baseline Documents

| Document | Version | Location |
| -------- | ------- | -------- |
| Solution Design | 1.2.0 | `docs/SD.md` |
| Product Requirements | 1.1.1 | `docs/PRD.md` |
| Architecture | 0.10.0 | `docs/ARCHITECTURE.md` |
| AI Architecture | 0.4.1 | `docs/AI.md` |
| Compliance | 0.3.1 | `docs/COMPLIANCE.md` |
| Security | 0.3.1 | `docs/SECURITY.md` |
| Data Design | 0.3.1 | `docs/DATA.md` |
| Infrastructure | 1.2.0 | `docs/INFRASTRUCTURE.md` |
| Operations | 1.0.1 | `docs/OPERATIONS.md` |
| Business Value Assessment | 1.0.1 | `docs/BVA.md` |
| ALM Plan | 0.3.0 | `docs/ALM_PLAN.md` |
| Test Strategy | 0.2.1 | `docs/TEST.md` |

### External References

| Reference | URL / Location |
| --------- | -------------- |
| **Microsoft Agent Framework** (primary agent pattern reference) | https://github.com/microsoft/agent-framework/tree/331201294bfda427b44dc49cfd730a1b41e4dedf |
| Swiss Federal Data Protection Act (FADP) | https://www.fedlex.admin.ch/eli/cc/2022/491/en |
| Data Protection Ordinance (DPO) | https://www.fedlex.admin.ch/eli/cc/2022/568/en |
| Federal Act on the Electronic Patient Record (EPDG) | https://www.fedlex.admin.ch/eli/cc/2017/203/de |
| Ordinance of the FDI on EPR (EPDV-EDI) | https://www.fedlex.admin.ch/eli/cc/2017/205/de |
| Microsoft Zero Trust security in Azure | https://learn.microsoft.com/azure/security/fundamentals/zero-trust |
| Azure Well-Architected security principles | https://learn.microsoft.com/azure/well-architected/security/principles |
| Cloud Adoption Framework, Zero Trust landing zones | https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/security-zero-trust |
| Azure Container Apps documentation | https://learn.microsoft.com/azure/container-apps/ |
| Azure OpenAI regional availability | https://learn.microsoft.com/azure/ai-services/openai/concepts/models |
| Microsoft Fabric documentation | https://learn.microsoft.com/fabric/ |

### Architecture Decision Records

| ADR ID | Decision | Location |
| ------ | -------- | -------- |
| `AR-D-001` | Fabric as core data platform; Switzerland North/West GA workloads only | `docs/ARCHITECTURE.md`, `docs/adr/ADR-0001` |
| `AR-D-002` | Fabric IQ Ontology excluded from MVP critical path | `docs/ARCHITECTURE.md`, `docs/adr/ADR-0002` |
| `AR-D-003` | PHI inference must use Standard/Regional Provisioned in Switzerland regions | `docs/ARCHITECTURE.md`, `docs/adr/ADR-0003` |
| `AR-D-004` | Global/DataZone/Developer deployment types blocked for PHI | `docs/ARCHITECTURE.md`, `docs/adr/ADR-0004` |
| `AR-D-005` | Dedicated React web app is mandatory MVP channel | `docs/ARCHITECTURE.md`, `docs/adr/ADR-0005` |
| `AR-D-006` | Preview-only services are non-production for regulated data | `docs/ARCHITECTURE.md`, `docs/adr/ADR-0006` |

---

*This document is the MVP Agent Solution Design baseline. It is intended to be
refined through implementation planning, measured SIT validation results, and
post-MVP feature wave planning.*
