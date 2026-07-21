# Step 2 — Curavias App Artefact BOM

**Sources:** `ARCHITECTURE.md` (v0.12.0) · `PRD.md` (v1.7.0) · `SD.md` (v1.4.0) ·
`SECURITY.md` (v0.5.0) · `bom.yaml` (v1.0.0).
**Scope:** everything required to stand up the Curavias **user app** — the React
command-center + grounded copilot (mandatory MVP channel per `ADR-0005`) — plus the
backend, data, integration, and governance artefacts it depends on.

**Legend — Status:** ✅ enumerated in `bom.yaml` · 🆕 to-create (app/UX layer) ·
🔒 governance/security control. **Priority:** P0 MVP-critical · P1 · P2.

---

## 2.A Experience-layer artefacts (React app + copilot UX) — 🆕

| ID | Artefact | Description | Realises | Priority |
| -- | -------- | ----------- | -------- | -------- |
| APP-EXP-01 | React SPA shell (`hcc-app-fluent`) | Fluent UI React app, Static Web App / Container Apps host | FR-CX-001, ADR-0005/0008 | P0 |
| APP-EXP-02 | Entra ID auth (MSAL) + role-aware routing | Sign-in, role→app-role mapping, session telemetry | FR-CX-001, NFR-SEC-001, SD §1 | P0 |
| APP-EXP-03 | **Copilot-Drawer** component | Natural-language query, grounded answer with citations + timestamp | FR-CX-001/002/006, exp #1 | P0 |
| APP-EXP-04 | **Whiteboard** (Live Command-Center) | Configurable KPI cards per role (occupancy %, deltas, status) | FR-CX-004/005, exp #2 | P0 |
| APP-EXP-05 | **Human-in-the-Loop approval modal** | Every outward action logged + released; advisory framing | FR-CX-003, NFR-AI-001/004, exp #3 | P0 |
| APP-EXP-06 | Citations / evidence panel | Source references + response provenance surfaced inline | FR-CX-006, NFR-AI-002/004 | P0 |
| APP-EXP-07 | Role workspaces (7) | One tailored view per agent role (see 2.B) | FR-CX-004/005 | P0 |
| APP-EXP-08 | Bed-capacity dashboard page | Occupancy, forecast pressure windows, DQ signals | FR-VIZ-001, FR-CX-005 | P0 |
| APP-EXP-09 | OR-steering dashboard page | Case utilisation, first-case on-time, cancellation, idle-slot | FR-VIZ-002, FR-CX-005 | P0 |
| APP-EXP-10 | Power BI embed frames | Embedded operational reports in-app | FR-CX-005 | P1 |
| APP-EXP-11 | Design tokens + Fluent theme | Curavias teal/green theme aligned to website CD/CI (Step 1) | REF-DS-02/03 | P0 |
| APP-EXP-12 | Degraded-mode / graceful-fallback UI | Banner + read-only mode when non-critical deps fail | NFR-REL-003 | P1 |
| APP-EXP-13 | Interaction telemetry + audit metadata | Prompt/response/action-confirmation events persisted | FR-GOV-001, NFR-GOV-001 | P0 |
| APP-EXP-14 | Localisation (DE-CH primary, EN) | i18n resource bundles | Brand §Language | P1 |
| APP-EXP-15 | Accessibility pass (WCAG 2.1 AA) | Keyboard, contrast, alt text, screen-reader labels | REF-DS-08 | P1 |

---

## 2.B Agent surfaces (7) — 🆕 UX over ✅ runtime

Each agent needs: a Whiteboard card set + Copilot-Drawer grounding + HITL gate.

| ID | Agent surface | Role view | HITL gate | Realises |
| -- | ------------- | --------- | --------- | -------- |
| APP-AGT-BMCA | Bettenmanagement-Copilot | Bed occupancy, pressure, transfer/same-day candidates | Bettenverlegung | FR-DC-001/002, FR-CX-004 |
| APP-AGT-OOA | Belegungs- & Forecast-Copilot | 72-h arrivals & occupancy forecast per specialty | Kapazität | FR-FC-001..005 |
| APP-AGT-DCA | Entlassungs-Copilot | Ranked discharge candidates + blockers + handoff | Cross-org. Handoff | FR-DC-002..006 |
| APP-AGT-ORSA | OP-Steuerungs-Copilot | Empty OR slots, slate redistribution, cancellation risk | OP-Slate-Änderung | FR-VIZ-002 |
| APP-AGT-SBA | Personal-Balance-Copilot | Staffing-gap heatmap, roster-vs-forecast delta | Personal | FR-FC-002/003 |
| APP-AGT-CSA | Krisen- & Szenario-Copilot | Scenario scoring vs. Swiss situation classifier | Politik-Ausnahme | FR-CX-003 |
| APP-AGT-DQ | Datenqualitäts-Agent | Bronze→Silver→Gold gates, drift alerts; PHI gates non-disable | PHI-Ausnahme | NFR-DQ-001..005, NFR-GOV-003 |

---

## 2.C API & agent-runtime layer

| ID | Artefact (bom.yaml id) | Type | Realises | Status | Priority |
| -- | ---------------------- | ---- | -------- | ------ | -------- |
| APP-RT-01 | Container Apps Agent-Host (`bom-container-apps-agent-host`) | Microsoft.App/containerApps | FR-CX-001/004, ADR-0008 | ✅ | P0 |
| APP-RT-02 | HCC Operations App (`bom-app-fluent`) | Microsoft.App/staticApp | FR-CX-001/004, FR-VIZ-001 | ✅ | P0 |
| APP-RT-03 | Azure AI Foundry Agent Service (`bom-foundry-agent-service`) | ML agents | FR-CX-002/004, ADR-0007/0008 | ✅ | P0 |
| APP-RT-04 | Azure OpenAI grounded chat (`bom-azure-openai`) | CognitiveServices | FR-CX-001/002/003, ADR-0003 | ✅ | P0 |
| APP-RT-05 | Fabric Data Agent (`bom-fabric-data-agent`) | Fabric/dataAgent (read-only grounding seam) | FR-ONT-004/008, FR-CX-002 | ✅ | P0 |
| APP-RT-06 | API orchestration + policy checks | Request routing, correlation IDs, safety gates | FR-GOV-001, SD §2 | 🆕 | P0 |

---

## 2.D Data-platform layer

| ID | Artefact (bom.yaml id) | Type | Realises | Status |
| -- | ---------------------- | ---- | -------- | ------ |
| APP-DAT-01 | Microsoft Fabric Capacity F64 (`bom-fabric-capacity`) | Fabric/capacities | FR-DATA-003/005 | ✅ |
| APP-DAT-02 | Fabric Data Workspace (`bom-fabric-workspace-data`) | Fabric/workspaces | FR-DATA-003 | ✅ |
| APP-DAT-03 | OneLake (`bom-onelake`) | Fabric/onelake | FR-DATA-003/008 | ✅ |
| APP-DAT-04 | Fabric Lakehouse (`bom-lakehouse`) | Fabric/lakehouse | FR-DATA-001/003/008 | ✅ |
| APP-DAT-05 | Fabric Eventstream (`bom-eventstream`) | Fabric/eventstream | FR-DATA-001/004 | ✅ |
| APP-DAT-06 | Fabric Eventhouse (`bom-eventhouse`) | Fabric/eventhouse (time-series) | FR-DATA-001, FR-FC-006 | ✅ |
| APP-DAT-07 | Direct Lake Semantic Model (`bom-semantic-model`) | Fabric/semanticModel | FR-DATA-005, FR-VIZ-001/002 | ✅ |
| APP-DAT-08 | Power BI Operational Dashboards (`bom-powerbi-report`) | PowerBI/reports | FR-CX-005, FR-VIZ-001/002 | ✅ |
| APP-DAT-09 | Landing Storage (ADLS Gen2) (`bom-storage-account`) | Storage/storageAccounts | FR-DATA-001, NFR-COMP-004 | ✅ |
| APP-DAT-10 | Fabric IQ Operational Ontology (`bom-fabric-iq-ontology`) | Fabric/ontology | FR-ONT-002/003/004 | ✅ (GA-gated) |
| APP-DAT-11 | Reference Ontology OWL/RDF (`bom-reference-ontology`) | ontology-owl (BFO-aligned) | FR-ONT-001/005/006 | ✅ |

---

## 2.E Integration layer

| ID | Artefact (bom.yaml id) | Type | Realises | Status |
| -- | ---------------------- | ---- | -------- | ------ |
| APP-INT-01 | Logic Apps Integration Workflows (`bom-logic-apps`) | Logic/workflows | FR-DATA-007, FR-DC-003/004, FR-GOV-005 | ✅ |
| APP-INT-02 | Azure Health Data Services FHIR Service (`bom-fhir-service`) | HealthcareApis/fhirServices | FR-DATA-002, FR-ONT-006 | ✅ |
| APP-INT-03 | Service Bus (partner backpressure/retry) | messaging | NFR-REL-004, SD §5 | 🆕 (named in SD) |
| APP-INT-04 | Partner-endpoint contracts (authenticated) | integration boundary | NFR-SEC-003, FR-OM-004 | 🆕 |

---

## 2.F Onboarding lanes (Sprint 6)

| ID | Artefact | Description | Realises |
| -- | -------- | ----------- | -------- |
| APP-ONB-01 | Patient minimum-data lane (`DC-ONB-PATIENT-v1`) | Pseudonymous, minimum metadata, deterministic service | FR-ONB-001, NFR-COMP-011 |
| APP-ONB-02 | Specialty-capacity lane (`DC-ONB-CAPACITY-v1`) + provider extensions | Specialty-tagged capacity onboarding | FR-ONB-002/003 |
| APP-ONB-03 | Deterministic-vs-agentic classifier | Documented FR-ONB-004 criterion | FR-ONB-004 |
| APP-ONB-04 | Synthesized-data contract/schema gate | `validate_datasets.py` CI gate | NFR-DQ-005, NFR-MAINT-005 |

---

## 2.G Security & governance controls — 🔒

| ID | Artefact (bom.yaml id) | Type | Realises |
| -- | ---------------------- | ---- | -------- |
| APP-SEC-01 | Microsoft Entra ID (`bom-entra-id`) | AAD/tenant | NFR-SEC-001, FR-GOV-002 |
| APP-SEC-02 | Managed Identity / WIF (`bom-managed-identity`) | userAssignedIdentities | NFR-SEC-001/003 |
| APP-SEC-03 | Azure Key Vault (`bom-key-vault`) | KeyVault/vaults | NFR-SEC-001/002 |
| APP-SEC-04 | Microsoft Purview (`bom-purview`) | Purview/accounts | FR-GOV-001/004, NFR-COMP-005 |
| APP-SEC-05 | Log Analytics Workspace (`bom-log-analytics`) | OperationalInsights | NFR-REL-001, FR-GOV-001/004 |
| APP-SEC-06 | Policy-as-Code Release Gate (`bom-policy-as-code`) | policy-gate | FR-GOV-003/004, NFR-GOV-001 |
| APP-SEC-07 | GitHub Actions Delivery Pipeline (`bom-github-actions`) | GitHub/actions | FR-GOV-003, NFR-MAINT-001, NFR-GOV-006 |
| APP-SEC-08 | PHI Row-Level Security (workspace-level) | phi=true → empty-set all roles | NFR-GOV-003, ADR-0016 |
| APP-SEC-09 | Zero Trust network baseline (hub-spoke, private endpoints, deny-by-default) | network controls | SECURITY §Network |
| APP-SEC-10 | Azure Policy initiatives (regions, SKUs, encryption, diagnostics) | policy | SECURITY §Guardrails |

---

## 2.H App-level non-functional targets (design constraints, not shippable items)

| Target | Value | Source |
| ------ | ----- | ------ |
| Interactive response | P95 < 4 s (standard grounded paths) | SD §NFR, NFR-PERF-005 |
| Copilot peak concurrency | 120 users | SD §NFR |
| Source events | 180 000 / day baseline, 3× burst headroom | SD §NFR |
| Region | Switzerland North primary, Switzerland West failover (runbook-gated) | ARCHITECTURE §Deployment |
| PHI inference | Regional deployment types only; Global/DataZone/Developer blocked | AR-D-003/004 |
| Naming standard | `<resource-type>-ihzhhpf-<env>` | SD §Naming |
