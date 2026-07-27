# Sprint Proposal — Signal Agent (SGA) & Data Quality Agent (DQA)

**Programme:** Curavias / SwissHospitalCapacityPlatform
**Type:** New-sprint starting point — functional & non-functional requirements + agent journeys
**Prepared for:** Urs Rüegg
**Status:** Draft v1.0 · for backlog grooming
**Builds on:** the AMA review corpus — the Trusted-External-Signals review (2026-07-17), the Capacity-Metadata framework (2026-06-29), the HCC/North-Star Ontology review (2026-07-01), and the Episode/Data-Governance review (2026-06-10). Both agents inherit the platform doctrine: **advisory-only + HITL, Swiss-region-pinned inference, GA-only critical path, contract-first, provenance-complete, fully audited.**

---

## 1. Context — why these two agents, now

Two ideas were triggered in the review sessions:

1. **Signal Agent (SGA)** — evaluate the current design and runtime for **missing signal channels (internal & external)**, then own the full **Channel Intake** lifecycle: discover → classify → assign the right **API adapter pattern** → onboard under a versioned contract → **test** the channel → bind it into the **right data context (ontology)** → activate & monitor. It can use **web search over public sources** to discover new external signals. Flagship example: onboarding **official certification signals** for nursing staff (Pflegepersonal) and physicians so the **skills baseline is populated automatically**, improving skills-based staff assignment.

2. **Data Quality Agent (DQA)** — go **beyond ingestion gates** (today's `DQSA`) to **proactively evaluate data quality and find missing data** that limits forecast and HCC operations, **quantify each gap's impact**, and **involve the data owner** to fill it — raising the **trustworthiness of the golden-source decision layer** that grounds **Fabric IQ and Foundry IQ**.

They are complementary and close a loop: DQA finds a data gap → if a new source is required, it hands off to SGA → SGA discovers/onboards the channel → DQA re-scores trust. Together they operationalise the two most-cited review findings — *"system quality depends heavily on metadata completeness and structure"* (single-point-of-failure) and the external-signal / skills-matching opportunity.

### 1.1 Fit within the existing agent set

| New agent | Extends / relates to | Distinction |
|---|---|---|
| **SGA — Signal Agent** | Generalises the external-signals workstream (`FR-EXT-*`, `DC-EXT-SIGNAL-v1`, `TriggerRule`, trust tiers) and feeds Staffing (`FR-STAFF-*` / SBA) | Not just hazard signals — **any** channel (internal & external); adds **discovery, adapter-assignment, sandbox testing, lifecycle** |
| **DQA — Data Quality Agent** | Elevates the existing **DQSA** (Data Quality & Semantics Agent) | DQSA = ingestion **gates**; DQA = **proactive** assessment, **gap → owner → remediation**, **trust scoring** of the gold/serving layer |

---

## 2. Assumptions & open questions (stated, not invented)

- **A1 — "Foundry IQ."** Treated here as the **Azure AI Foundry knowledge / agent-grounding layer** (the Foundry-side counterpart to Fabric IQ's operational ontology). Foundry-hosted agents are currently constrained on the MVP critical path (application-hosted baseline; Foundry-hosted deferred pending Swiss-region GA), so DQA's "grounding-ready" certification for Foundry IQ is **GA-gated** the same way Fabric IQ is (ADR-0014). *Confirm the exact Foundry IQ scope and Swiss-region GA status before committing it to the critical path.*
- **A2 — Certification registries.** Candidate Swiss certification/qualification sources (illustrative, **to validate at build**): **FMH** (physicians), **SRK/Swiss Red Cross** diploma recognition, the national healthcare-professions registers (**NAREG / Gesundheitsberuferegister**), cantonal practice authorisations (Berufsausübungsbewilligung), professional bodies (SBK/ASI). API availability, licence terms, and whether they expose per-professional credential status must be verified — do **not** assume machine-readable feeds exist.
- **A3 — Web search at runtime.** SGA's discovery capability assumes a **governed web-search / public-source retrieval tool** is available to the agent at runtime, with results treated as **untrusted** (candidate identification only — never an authoritative data feed).
- **A4 — Staff data is not PHI-free.** Certification/skills data is **staff-identifiable personal data** under nDSG (not patient PHI, but still regulated). It is handled pseudonymised via staff work-IDs, Swiss-region, with credential↔identity linkage only at the endpoint.
- **A5 — Sprint slot.** Labelled "proposed sprint"; it sequences **after** the Sprint-16 CSA design and the external-signals workstream. Slot the actual number in grooming.

Open questions are listed per agent (§3.7, §4.7) and consolidated in §7.

---

## 3. Agent 1 — Signal Agent (SGA)

### 3.1 Purpose & scope
A meta-agent that keeps the platform's **signal coverage** complete and current. It continuously asks *"which signals would make our forecast, HCC steering and staffing better, and are we consuming them?"* — then manages onboarding end-to-end. **In scope:** internal system feeds and external trusted public sources; discovery, classification, adapter assignment, contract + ontology onboarding, sandbox testing, activation, lifecycle. **Out of scope:** acting on signals (that stays with CSA/consuming agents), and any autonomous activation without human approval.

### 3.2 Functional requirements (`FR-SIG-*`)

| ID | Requirement |
|---|---|
| `FR-SIG-001` | **Signal-gap discovery (design + runtime).** Evaluate PRD, DATA, the DC-* contract family, agent input specs, the ontology, and runtime telemetry to detect channels that are referenced-but-unwired, present-but-degraded, or available-but-unconsumed; emit a ranked **Signal Gap Register**. |
| `FR-SIG-002` | **External-source discovery via web search.** Use governed web search / public-source retrieval to identify candidate **new external** signal sources, classify by domain family (hazard, certification, capacity, referral, demographic, epidemiological), and propose them for onboarding (advisory). |
| `FR-SIG-003` | **Classification & trust grading.** For each candidate assign: domain family; signal type — **native-alert/event** vs **derive/threshold** vs **batch-reference**; trust tier (A federal · B para-federal/cantonal/research · C aggregator/proxy); and PHI / staff-PII / non-PHI classification. |
| `FR-SIG-004` | **Adapter-pattern assignment.** Select the correct integration adapter from the platform connector catalogue: CAP/OASIS alert poll, FDSN query, STAC/OGC catalogue, DATEX II, CKAN (opendata.swiss), FHIR terminology/registry, webhook/Event-Grid push, scheduled REST pull, or file drop — realised via Logic Apps / Azure Functions / Fabric Eventstream. |
| `FR-SIG-005` | **Contract-first onboarding.** Generate or extend a **versioned data contract** for the channel with full governance tags (classification, residency, legal_basis, retention, trust_tier, provenance, licence). Reuse `DC-EXT-SIGNAL-v1` for hazards; introduce **`DC-REF-CERTIFICATION-v1`** for credentials; **`DC-INT-*`** for internal channels. |
| `FR-SIG-006` | **Ontology binding (right data context).** Bind the channel's entities into the two-layer ontology (BFO/OBO reference ↔ Fabric IQ operational), reusing/extending classes — e.g. `TrustedSource`/`ExternalSignal` for hazards; **`Certification`/`Qualification`/`Credential`/`Competency`** for skills — and register the reference↔operational **crosswalk + CI conformance** (per `NFR-ONT-001`). |
| `FR-SIG-007` | **Automated channel testing (sandbox).** Before activation, run the channel through a test harness in an isolated SIT/T-SHOW environment: schema conformance, sample fetch, provenance completeness, trigger/threshold correctness, latency, dedup & noise filters — emitting a **Channel Readiness Scorecard**. |
| `FR-SIG-008` | **Certification → skills-baseline enrichment (flagship).** On onboarding a certification/qualification channel, resolve each credential to the **competency taxonomy** and populate/refresh the **skills baseline** (`StaffingPool.skill_tags`) for affected staff using **pseudonymised work-IDs only**, improving skills-based assignment (feeds `FR-STAFF-003` / SBA). |
| `FR-SIG-009` | **Activation & lifecycle management.** Activate approved channels; maintain a **Channel Registry**; monitor health (endpoint availability, licence validity, schema/semantic drift); version, deprecate and retire stale channels. |
| `FR-SIG-010` | **Advisory / HITL.** Onboarding, ontology changes, and activation require human approval (**data owner + security/compliance**). SGA proposes; a human approves each channel and each ontology change. No channel enters decision context without a recorded approval. |
| `FR-SIG-011` | **Provenance & auditability.** Every onboarded channel and every emitted signal carries mandatory provenance (`sourceAuthority`, identifier, `trustTier`, licence, onboarded-by, approval-ref), surfaced downstream (reuses `FR-EXT-004`). |
| `FR-SIG-012` | **Cost & value scoring.** Estimate integration effort, run cost, and expected decision value (which agent/KPI it improves) per candidate to prioritise the intake backlog. |
| `FR-SIG-013` | **Internal-signal coverage.** Detect missing/under-used **internal** signals (OR anaesthesia-consultation status, rostering feed, device PM windows, transfer events) and route them to the correct `DC-*` contract and consuming agent. |

### 3.3 Non-functional requirements (`NFR-SIG-*`)

| ID | Requirement |
|---|---|
| `NFR-SIG-001` | **Zero Trust ingest.** External input is untrusted by definition: connectors use **workload identity**, no static secrets, and **validate/sanitise every payload at the boundary** before it reaches any stream. |
| `NFR-SIG-002` | **Residency & data class.** Public hazard signals = non-PHI, light residency. **Certification/skills data = staff-PII (nDSG)** → pseudonymised, Swiss-region, linkage only at endpoint. No PHI enters via a channel without explicit classification + control. |
| `NFR-SIG-003` | **Provenance completeness.** 100% of channels and signals carry complete provenance + current licence status. |
| `NFR-SIG-004` | **GA-only & governance.** New connectors are GA on the critical path; Fabric IQ ontology binding is **GA-gated** (ADR-0014); a **new ADR** governs the signal-channel lifecycle (extends the proposed external-trigger ADR, `FR-EXT-GOV-001`). |
| `NFR-SIG-005` | **Reliability.** Per-channel health checks, graceful degradation, and redundant channels for high-value signals; **no silent channel loss** (health-check + alert per connector). |
| `NFR-SIG-006` | **Licence/compliance.** Production licence + attribution confirmed per source before activation; a **build-time endpoint/licence verification list** is maintained as a living artefact. |
| `NFR-SIG-007` | **Performance.** Candidate evaluation + adapter assignment complete within a bounded window; the test harness completes within the SIT cycle. |
| `NFR-SIG-008` | **Explainability.** Every onboarding recommendation cites the discovered source, the adapter-choice rationale, and the ontology mapping. |
| `NFR-SIG-009` | **Web-search safety.** Web results are untrusted — used only to **identify candidate sources**, never followed as instructions and never treated as an authoritative feed; copyright/repro rules respected. |
| `NFR-SIG-010` | **Multi-provider reuse.** Channel patterns and adapters are reusable across providers via the provider-extension pattern (`NFR-MAINT-004`). |

### 3.4 New / extended data contracts
- **`DC-REF-CERTIFICATION-v1`** *(new)* — credential ↔ competency crosswalk (issuer, credential type, competency codes, validity window, verification status); staff-PII, pseudonymised.
- **`DC-INT-<domain>-v1`** *(new family)* — internal channel intake contracts (e.g. anaesthesia-consultation status, rostering).
- Reuse **`DC-EXT-SIGNAL-v1`** (hazards) and the `_classification / _residency / _legal_basis / _retention / _provenance / _pseudonymisation` governance tag set.

### 3.5 Ontology additions (reference ↔ Fabric IQ)
`Certification`, `Qualification`, `Credential` (IAO information content entities), `Competency`/`SkillTag` (quality), `IssuingAuthority` (organisation bearing an authority role) — related to the existing `StaffShift`/`StaffingPool` capacity-unit subtype: *HealthWorker `holds` Credential; Credential `certifies` Competency; Competency `qualifies_for` CapacityUnit/Task.* Governed by the semantic owner with a CI crosswalk check.

### 3.6 Agent journey (SGA)
> **Discover → Evaluate → Classify → Propose → Adapt → Onboard → Test → Approve → Activate → Monitor**

1. **Discover** — scan design + runtime for gaps (`FR-SIG-001`); run governed web search for external candidates (`FR-SIG-002`).
2. **Evaluate & rank** — score each candidate by value × effort × trust (`FR-SIG-012`).
3. **Classify & trust-grade** — domain, signal type, trust tier, data class (`FR-SIG-003`).
4. **Propose** — present a ranked intake proposal → **HITL: data owner + compliance approve** (`FR-SIG-010`).
5. **Assign adapter** — pick the connector pattern (`FR-SIG-004`).
6. **Onboard** — draft the versioned contract + ontology binding + crosswalk (`FR-SIG-005/006`).
7. **Test** — sandbox harness → Channel Readiness Scorecard (`FR-SIG-007`).
8. **Approve activation** — **HITL** sign-off on scorecard (`FR-SIG-010`).
9. **Activate & bind** — register channel, wire to consuming agents, populate context (e.g. skills baseline, `FR-SIG-008`).
10. **Monitor / version / retire** — health, licence, drift; lifecycle (`FR-SIG-009`).

**Worked example — nurse & physician certifications → skills baseline.** SGA discovers an official certification register (web search, Tier-A/B), classifies it as **staff-PII, batch-reference**, assigns a **FHIR-registry/REST adapter**, drafts `DC-REF-CERTIFICATION-v1`, binds `Credential/Competency` into the ontology, tests in SIT (schema + provenance + a sample credential resolves to a competency), the **data owner approves**, and on activation the **skills baseline (`StaffingPool.skill_tags`) is auto-populated by pseudonymised work-ID** — directly improving the **skills-based OR/ward assignment** the ops-lead review called out (physicians *and* nursing, incl. APN competencies). All advisory; the roster owner still confirms assignments.

### 3.7 SGA open questions (require validation)
- Which certification registers expose **machine-readable, per-professional** credential status, and under what **licence**? (A2)
- Governed **web-search tool** availability + guardrails at runtime? (A3)
- Competency **taxonomy** source of truth (FMH disciplines + nursing/APN competency framework)?
- Approval RACI for channel onboarding (who is the **channel owner**)?

---

## 4. Agent 2 — Data Quality Agent (DQA)

### 4.1 Purpose & scope
A proactive data-quality and gap-remediation agent that **certifies the trustworthiness of the golden-source decision layer** grounding Fabric IQ and Foundry IQ. It continuously assesses quality, finds missing/weak data that caps forecast and HCC performance, **quantifies impact**, and drives remediation **through the accountable data owner**. **In scope:** assessment, gap detection, trust scoring, owner-routed remediation, grounding-readiness certification. **Out of scope:** editing source data (read-only), and replacing DQSA's ingestion gates (it complements them).

### 4.2 Functional requirements (`FR-DQA-*`)

| ID | Requirement |
|---|---|
| `FR-DQA-001` | **Continuous quality assessment (beyond gates).** Score gold/serving datasets on completeness, timeliness, validity, uniqueness, consistency, and lineage-integrity — continuously, not only at ingestion. |
| `FR-DQA-002` | **Gap identification + impact analysis.** Detect missing/degraded data (e.g. absent bed/ward counts for USZ/Hirslanden, no ED→inpatient conversion, missing staffing ratios, unwired seasonality/epidemic features) and **quantify each gap's impact** on forecast accuracy and specific HCC decisions/KPIs. |
| `FR-DQA-003` | **Trust score for the golden decision layer.** Compute and publish a **per-domain and overall Trust Score** for the gold/serving layer that grounds Fabric IQ / Foundry IQ, with dimension drivers and trend. |
| `FR-DQA-004` | **Data-owner involvement & remediation workflow.** Map each gap to the accountable **data owner/steward** (data-governance RACI); open a remediation request stating *what's needed, why, and expected impact*; track to closure (**HITL** — the owner provides/approves). |
| `FR-DQA-005` | **Root-cause & source recommendation.** For each gap recommend the concrete fill source (bed counts ← KIS/bed-management ADT; ED conversion ← ED+ADT linkage; staffing ratios ← rostering). **Where a new channel is needed, hand off to SGA.** |
| `FR-DQA-006` | **Decision-readiness gating (advise, don't silently serve).** When a dataset's trust score falls below the threshold for a decision class, flag it and advise **degraded-mode** (e.g. specialty-level fallback vs disease-level) rather than serving low-trust data silently. |
| `FR-DQA-007` | **Contract & taxonomy conformance.** Verify gold entities conform to the metadata taxonomy and `DC-*` contracts and that governance tags are complete; surface **taxonomy drift**. |
| `FR-DQA-008` | **Ontology/semantic completeness.** Check that gold entities map to reference-ontology classes (reference↔operational crosswalk) so grounding is concept-complete; flag unmapped entities to the **semantic owner**. |
| `FR-DQA-009` | **Prioritised remediation backlog.** Rank gaps by *impact × decision value × effort* for the data-governance team. |
| `FR-DQA-010` | **Advisory / HITL + audit.** DQA proposes assessments and remediations; owners act; DQA **never edits source data**. Every assessment, gap, and remediation is logged as an evidence artefact (reuses the EAA pattern). |
| `FR-DQA-011` | **Feed quality into AI confidence.** Propagate data-quality signals into DFA/DCA/OR agents so low-trust inputs surface as wider confidence intervals or staleness warnings (ties to DFA drift indicators). |
| `FR-DQA-012` | **Fabric IQ / Foundry IQ grounding-readiness certification.** Certify a domain "grounding-ready" (trust score + completeness + provenance + ontology mapping all above threshold) **before** it is exposed as a golden source to the copilot/agents. |

### 4.3 Non-functional requirements (`NFR-DQA-*`)

| ID | Requirement |
|---|---|
| `NFR-DQA-001` | **Reproducible, explainable trust score.** Versioned, deterministic; every score decomposes to its dimension drivers. |
| `NFR-DQA-002` | **Non-intrusive / Zero Trust.** Read-only over data; least-privilege; no writes to source; operates on metadata/aggregates and honours existing PHI controls. |
| `NFR-DQA-003` | **Traceability.** Every gap → owner → remediation → closure is fully auditable; lineage via Purview. |
| `NFR-DQA-004` | **Performance/scale.** Continuous assessment within event volumes (≈180k events/day + burst); bounded assessment latency; scorecards on a defined cadence. |
| `NFR-DQA-005` | **GA-only & governance.** GA on the critical path; Fabric IQ / **Foundry IQ readiness respects the GA gate** (ADR-0014, A1); an **ADR** governs the trust-score model + thresholds. |
| `NFR-DQA-006` | **Explainability / HITL.** Every remediation request is human-readable, owner-addressed, and impact-quantified; advisory-only. |
| `NFR-DQA-007` | **Reliability / safety.** Degraded-mode advice rather than silent low-trust serving; **no false "trusted" certification**. |
| `NFR-DQA-008` | **Multi-provider maintainability.** Trust model + taxonomy conformance reusable across USZ/LUKS/Hirslanden/Zollikerberg via the provider-extension pattern. |

### 4.4 Trust-score model (proposed)
`TrustScore(domain) = f(completeness, timeliness, validity, uniqueness, consistency, lineage_integrity, provenance, ontology_mapping)` — weighted per decision class, versioned, and published as a governance artefact (`DC-DQ-TRUSTSCORE-v1`, **new**). Thresholds per decision class recorded in the governing ADR.

### 4.5 New data contracts
- **`DC-DQ-TRUSTSCORE-v1`** *(new)* — per-domain trust score + dimension breakdown + as-of.
- **`DC-DQ-GAP-v1`** *(new)* — identified gap, impacted KPI/agent, owner, recommended source, effort, status.

### 4.6 Agent journey (DQA)
> **Assess → Detect → Score → Prioritise → Route → Remediate → Re-assess → Certify → Feed-back**

1. **Assess** — continuous quality scan of gold/serving (`FR-DQA-001`).
2. **Detect + impact** — find gaps, quantify decision/forecast impact (`FR-DQA-002`).
3. **Score trust** — per-domain + overall Trust Score (`FR-DQA-003`).
4. **Prioritise** — impact × value × effort backlog (`FR-DQA-009`).
5. **Route to owner** — **HITL** remediation request with source recommendation (`FR-DQA-004/005`); *if new source needed →* **hand to SGA**.
6. **Remediate** — owner provides/approves the data (tracked).
7. **Re-assess** — recompute trust; update trend.
8. **Certify grounding-readiness** — gate Fabric IQ / Foundry IQ exposure (`FR-DQA-012`).
9. **Feed back** — push quality into forecast/HCC confidence (`FR-DQA-011`); advise degraded-mode where needed (`FR-DQA-006`). *(loop)*

### 4.7 DQA open questions (require validation)
- **Foundry IQ** scope + Swiss-region GA (A1) — does DQA certify one or two grounding layers?
- Trust-score **weights + thresholds** per decision class — who ratifies (ADR)?
- Data-governance **RACI** completeness — is every gold domain owned?
- Ground-truth for **impact quantification** (does a forecast-accuracy backtest harness exist to measure a gap's real effect)?

---

## 5. How SGA and DQA work together (closed loop)

```text
        ┌──────────────────────────────────────────────┐
        │  DQA: assess gold/serving → find a data gap   │
        │  (e.g. staffing skill coverage incomplete)    │
        └───────────────┬──────────────────────────────┘
                        │ gap needs a NEW source
                        ▼
        ┌──────────────────────────────────────────────┐
        │  SGA: discover → adapter → contract →          │
        │  ontology-bind → test → (HITL) activate         │
        │  (e.g. certification register → skills baseline)│
        └───────────────┬──────────────────────────────┘
                        │ channel live, context populated
                        ▼
        ┌──────────────────────────────────────────────┐
        │  DQA: re-assess → trust score up →             │
        │  certify domain grounding-ready (Fabric/Foundry IQ)│
        └──────────────────────────────────────────────┘
```

DQA states *what* is missing and *why it matters*; SGA supplies the *how* (the channel). The result is a self-healing golden-source layer whose trust is measured, not assumed — directly retiring the "metadata-quality single-point-of-failure" risk.

---

## 6. Sprint starting point

### 6.1 Sprint goal
Stand up the **first slice** of SGA and DQA as **advisory, HITL, GA-only** agents that (a) produce a **Signal Gap Register** and onboard **one certification channel** end-to-end into the skills baseline, and (b) publish a **Trust Score** for the gold decision layer with an **owner-routed remediation** loop — proven on one worked example each.

### 6.2 Scope

#### In scope (MVP slice)
- SGA: gap discovery (`FR-SIG-001`), classification/trust-grading (`FR-SIG-003`), adapter assignment (`FR-SIG-004`), `DC-REF-CERTIFICATION-v1` + ontology binding (`FR-SIG-005/006`), sandbox test + scorecard (`FR-SIG-007`), the certification→skills worked example (`FR-SIG-008`), HITL + provenance + registry (`FR-SIG-009/010/011`).
- DQA: continuous assessment (`FR-DQA-001`), gap + impact (`FR-DQA-002`), Trust Score `DC-DQ-TRUSTSCORE-v1` (`FR-DQA-003`), owner remediation `DC-DQ-GAP-v1` (`FR-DQA-004/005`), SGA hand-off seam, grounding-readiness certification behind the GA gate (`FR-DQA-012`), HITL + audit (`FR-DQA-010`).
- Governing **ADR** (signal-channel lifecycle + trust-score model/thresholds); PRD extension with `FR-SIG-*` / `FR-DQA-*` + traceability rows.

#### Out of scope (later)
- Live web-search discovery at scale (`FR-SIG-002`) — start with a curated candidate list; add discovery once the guardrail (A3) is confirmed.
- Secondary internal channels (`FR-SIG-013`) beyond the worked example.
- Foundry IQ certification if its Swiss-region GA is unconfirmed (A1) — Fabric IQ first, Foundry IQ behind the same GA gate.
- Auto-propagation of quality into AI confidence intervals (`FR-DQA-011`) — design in this sprint, wire next.

### 6.3 Workstreams & sequencing
Two parallel tracks with one integration seam:
- **Track A (SGA)** and **Track B (DQA)** run concurrently.
- **Integration seam:** DQA's `DC-DQ-GAP-v1` "new-source-needed" flag → SGA intake proposal. Define the seam contract first so both tracks build against it.
- **Governance track:** ADR + PRD/traceability + RACI (channel owner, semantic owner, data owners) in parallel from day 1.

### 6.4 Acceptance evidence (Definition of Done)
- Signal Gap Register produced from a real design+runtime scan; ranked.
- One certification channel onboarded end-to-end: contract merged, ontology crosswalk + **CI conformance check** green, Channel Readiness Scorecard passed, **HITL approval recorded**, skills baseline populated by pseudonymised work-ID on a sample.
- Trust Score published for ≥1 gold domain with dimension breakdown; one gap opened, **routed to a named owner**, and closed on a sample; re-assessment shows score change.
- Grounding-readiness certification demonstrably **gates** exposure (a below-threshold domain is withheld/degraded, not served).
- ADR merged; `FR-SIG-*` / `FR-DQA-*` + traceability rows merged; provenance + audit records complete for every action.
- All new connectors **GA**; no PHI in any new index/channel (classification gate green).

### 6.5 Success metrics / KPIs
- **Signal coverage %** (consumed vs identified-valuable channels); time-to-onboard a channel.
- **Skills-baseline completeness %** for nursing/physicians after certification onboarding.
- **Gold-layer Trust Score** (per-domain + overall) and its **trend**; number/resolution-rate of gaps closed with owner.
- **Grounding-readiness** coverage (% of gold domains certified) for Fabric IQ / Foundry IQ.
- Forecast-accuracy delta attributable to a closed gap (needs the backtest harness — §6.7 G4).
- 100% advisory/HITL compliance; 100% provenance + audit completeness; zero PHI-in-channel incidents.

### 6.6 Risks & mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Certification feeds lack machine-readable per-professional status (A2) | SGA flagship blocked | Start with the richest available register; fall back to a manual-attested credential import via the same contract; keep the adapter pattern generic |
| Web-search discovery surfaces low-trust/poisoned sources (A3) | Bad channel onboarded | Untrusted-by-default; trust-grading + HITL approval + sandbox test gate before any activation |
| Staff-PII mishandled as "non-PHI" (A4) | nDSG breach | Explicit staff-PII class; pseudonymised work-ID; Swiss-region; endpoint-only linkage; DPO sign-off in HITL |
| Trust-score gaming / false "trusted" | Wrong golden-source decisions | Reproducible, explainable score; ADR-ratified thresholds; no self-certification without owner remediation |
| Foundry IQ not Swiss-GA (A1) | Certification scope slips | Fabric IQ first; Foundry IQ behind the GA gate; property-graph/fallback interim |
| Scope creep (both agents are broad) | Timeline slip | One worked example each; discovery + secondary channels deferred |

### 6.7 Gaps that block build

| Gap | Blocks |
|---|---|
| **G1 — Certification source + licence (A2)** | SGA flagship end-to-end onboarding |
| **G2 — Governed web-search tool + guardrails (A3)** | `FR-SIG-002` discovery |
| **G3 — Data-governance RACI completeness** | DQA owner-routed remediation (`FR-DQA-004`) |
| **G4 — Forecast-accuracy backtest harness** | Quantifying gap impact (`FR-DQA-002`) and the forecast-delta KPI |
| **G5 — Foundry IQ scope + Swiss-region GA (A1)** | Foundry IQ grounding-readiness certification (`FR-DQA-012`) |
| **G6 — Competency taxonomy source of truth** | Credential→competency resolution (`FR-SIG-008`) |
| **G7 — Governing ADR (channel lifecycle + trust-score thresholds)** | Ratified activation & certification behaviour |

---

## 7. Consolidated open questions
1. Which Swiss certification registers are machine-readable and production-licensable? (G1)
2. Is a governed, guard-railed web-search tool available to SGA at runtime? (G2)
3. Is every gold domain assigned an accountable data owner? (G3)
4. Does a forecast backtest harness exist to measure a gap's real impact? (G4)
5. What is Foundry IQ's scope and Swiss-region GA date? (G5)
6. What is the authoritative competency taxonomy (physician + nursing/APN)? (G6)
7. Who ratifies channel-lifecycle governance and trust-score thresholds (ADR)? (G7)

**Readiness verdict:** both agents sit inside the platform's proven governance envelope and reuse established patterns (advisory/HITL, provenance, two-layer ontology, GA-gating, contract-first, audit). They are **buildable as an advisory MVP now** for the two worked examples; production breadth is gated on G1–G7. The recommended first slice proves the closed loop (DQA finds → SGA onboards → DQA re-scores) on one certification channel and one gold domain — the smallest end-to-end demonstration of a self-healing, trust-measured golden-source layer.
