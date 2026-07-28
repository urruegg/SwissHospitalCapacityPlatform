# COMPLIANCE

| Field | Value |
| ----- | ----- |
| **Version** | 0.12.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 0.11.1 (repointed the Curavias ADR link ADR-0040 -> ADR-0050 (#378)); this bump adds the Sprint 31 Data Quality Agent proactive-assessment control section |

## Purpose

Define the compliance baseline for the Swiss Hospital Capacity Platform and make
Swiss legal obligations traceable to architecture controls, delivery artifacts,
and operational evidence.

> **Scope carve-out (Sprint 00, time-limited):** the new-tenant demo environment
> in tenant `1337187a-4c41-4da9-8fca-731bba7a4329` is deployed in `westus2` for
> synthetic-data proof-of-technology validation of services not yet GA in
> `switzerlandnorth`. See [ADR-0013](adr/0013-temporary-us-region-demo-scope.md)
> and the exception `EX-2026-07-02-westus2-demo` in [policy/exceptions.json](../policy/exceptions.json).
> This carve-out does NOT weaken ADR-0003 / ADR-0004 for any PHI or production scope.
>
> **PROD region (Sprint 19):** PROD was rebuilt greenfield in
> **`switzerlandnorth`** (`rg-ihzhhpf-prod`), synthetic data only, no PHI, per
> [ADR-0037](adr/0037-prod-region-switzerland-north-greenfield.md) +
> [ADR-0016](adr/0016-no-phi-in-mvp-demo-scope.md). SIT stays US-region
> (`westus2`/`eastus2`) per the carve-out above. Consolidated as-deployed +
> compliance-posture view: [CURAVIAS-PRODUCT-STATUS.md](CURAVIAS-PRODUCT-STATUS.md).

Scope of this version:
- Swiss federal privacy and health-data obligations relevant to the platform.
- Zero Trust and Responsible AI controls derived from those obligations.
- Practical evidence model for audits and release gates.

Out of scope for this version:
- Canton-specific legal analysis by canton.
- Formal legal advice.

## Regulatory Scope

Primary legal and regulatory anchors (Swiss official sources):

| Topic | Source | Why it matters for this platform |
| ----- | ----- | ----- |
| Federal Data Protection Act (FADP) | https://www.fedlex.admin.ch/eli/cc/2022/491/en | Core obligations for lawful processing of health-related personal data, data subject rights, cross-border disclosure, security, and breach handling. |
| Data Protection Ordinance (DPO) | https://www.fedlex.admin.ch/eli/cc/2022/568/en | Operational detail for technical and organisational measures, logging/traceability, and implementation expectations under FADP. |
| Federal Act on the Electronic Patient Record (EPDG) | https://www.fedlex.admin.ch/eli/cc/2017/203/de | Consent model, access rights, emergency access, identity requirements, certification duties, and mandatory logging for EPR contexts. |
| Ordinance of the FDI on EPR (EPDV-EDI) | https://www.fedlex.admin.ch/eli/cc/2017/205/de | Technical and organisational certification baselines, metadata and interoperability requirements for EPR ecosystems. |
| Federal Act on Research involving Human Beings (HRA), conditional | https://www.fedlex.admin.ch/eli/cc/2013/617/en | Applies if platform data is used for regulated research workflows; includes consent, ethics approval, safeguards, and export conditions. |
| Federal Health Insurance Act (KVG), conditional | https://www.fedlex.admin.ch/eli/cc/1995/1328_1328_1328/de | Relevant where insurer-facing data exchange, quality reporting, or statutory data-sharing duties are in scope. |

Important implementation note:
Article-level legal interpretation must be validated with legal counsel before
production deployment. This document is an engineering control baseline.

## Applicability Model

- Always in scope:
	- FADP and DPO for personal data and sensitive health data.
- In scope when EPR integration is used:
	- EPDG and EPDV-EDI controls.
- In scope for research/secondary use programs:
	- HRA controls and ethics workflow.
- In scope for insurer/statutory reimbursement or quality exchange:
	- KVG-linked data governance requirements.

## Zero Trust and Responsible AI Baseline

Zero Trust principles used in this repository:
- Verify explicitly: strong identity, least privilege, and policy-bound access.
- Use least privilege: role-scoped and time-bounded access to PHI-bearing systems.
- Assume breach: full logging, anomaly detection, and rehearsed containment.

Responsible AI principles used in this repository:
- Human oversight on clinically impactful recommendations.
- Transparency to users on AI-assisted decisions.
- Safety and performance monitoring with rollback/fallback.
- Data minimization and purpose limitation for model inputs and traces.

These principles are treated as implementation controls that support Swiss legal
obligations, especially for sensitive data handling and explainability needs.

## Control Mapping

### Compliance-to-Architecture Traceability

| Control ID | Obligation theme | Swiss legal anchor | Required platform control | Current repo alignment | Gap status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| CH-C01 | Lawfulness, purpose limitation, data minimization | FADP (principles; sensitive data) + DPO | Data processing inventory per use case, explicit purpose tags, minimised PHI fields | Directionally present in architecture narrative | Open: add machine-readable data inventory and purpose registry |
| CH-C02 | Privacy by design and default | FADP + DPO | Secure defaults, least-privilege access, deny-by-default for PHI egress | Strongly aligned via ADR decisions on PHI processing and failover deny | Partial: implement policy-as-code checks in CI |
| CH-C03 | Security and traceability | DPO + EPDG Art. 10 | End-to-end audit logs, tamper resistance, retention controls, access trail for PHI | Logging intent exists in docs | Open: define concrete log schema, retention, and evidence extraction runbook |
| CH-C04 | Data subject rights | FADP rights regime | DSR workflow: access, correction, deletion/restriction where applicable, response SLAs | Not yet operationalised | Open: create DSR process, ownership, and ticket templates |
| CH-C05 | Cross-border disclosure restrictions | FADP cross-border regime | PHI residency enforcement, transfer assessment, exception approvals, compensating controls | Strongly aligned by Swiss-only PHI processing decisions | Partial: add formal transfer-risk assessment template and legal sign-off gate |
| CH-C06 | Personal data breach notification | FADP + DPO | Incident triage for privacy events, notification decision tree, regulatory and contractual notification paths | Security/ops direction exists | Open: add privacy incident runbook with decision matrix and timers |
| CH-C07 | EPR consent and access governance | EPDG Art. 3, 7, 9 | Explicit consent capture/revocation, identity assurance, role and break-glass controls | Architecture supports gated access patterns | Open: define technical integration requirements and test cases |
| CH-C08 | EPR certification and interoperability | EPDG Art. 11-13 + EPDV-EDI | Certification boundary mapping, conformance evidence for standards/profiles | Not yet defined in detail | Open: add EPR conformance control pack and responsibility matrix |
| CH-C09 | Research use governance (conditional) | HRA (consent, ethics, export, storage) | Separate legal basis for research, ethics approvals, segregated environments and data pipelines | Not implemented | Open: create optional research lane with explicit opt-in controls |
| CH-C10 | AI oversight for high-impact workflows | FADP transparency/automated decision context + HRA principles (if research) | Human-in-the-loop, explainability notes, model risk thresholds, post-deployment monitoring | AI guidance exists in docs | Partial: add measurable AI acceptance criteria and override audit trail |

### Architecture Challenge Outcome (Compliance Lens)

Decisions already aligned:
- React-only MVP is compliance-neutral and simplifies data flow boundaries.
- PHI failover default-deny reduces unlawful disclosure risk.
- Swiss-only PHI processing policy supports cross-border risk control.

Material gaps to close:
- Formal controller/processor and subprocessor register.
- Article-linked DSR operating model.
- Policy-as-code enforcement for residency and deployment-type rules.
- Evidence automation for audits and release readiness.

### Sprint 05 Baseline Upgrade (CAF/WAF)

This baseline adds canton-specific legal applicability and explicit control ownership on
top of the federal `CH-C01`..`CH-C10` controls, per the CAF/WAF review §8/§9 and
[`docs/adr/0011-cantonal-legal-applicability-gate.md`](adr/0011-cantonal-legal-applicability-gate.md).

1. Canton-specific deltas are tracked in
   [`docs/compliance/cantonal-annex.md`](compliance/cantonal-annex.md). Federal controls
   remain the baseline; the annex records each canton's delta, owner, evidence, and
   status. Cantonal workloads are limited to SIT until their annex entries reach
   `implemented` with legal sign-off (ADR-0011 §3).
2. Control ownership roles for open CH controls follow the approval ownership baseline:
   `LEGAL`, `SEC`, `OPS`, `ARCH` (see
   [`docs/adr/0007-0011-hardening-delta-summary.md`](adr/0007-0011-hardening-delta-summary.md#approval-ownership-baseline)).

| Control ID | Owner role | Sprint 05 closure artifact |
| ----- | ----- | ----- |
| `CH-C01` | SEC | Data inventory + cantonal annex `cantonId` mapping |
| `CH-C02` | SEC | Policy-as-code checks (ADR-0010, Phase 2) |
| `CH-C03` | OPS | HITL/audit persistence evidence (ADR-0007/0009, Phase 3) |
| `CH-C04` | SEC | DSR runbook (`RV-04`, Phase 2) |
| `CH-C05` | LEGAL | Cantonal annex + transfer-risk gate (ADR-0011) |
| `CH-C06` | SEC | Privacy incident runbook (`RV-04`, Phase 2) |
| `CH-C07` | LEGAL | EPR consent/access controls (cantonal annex `VD`/`ZH`) |
| `CH-C08` | LEGAL | EPR conformance pack (deferred) |
| `CH-C09` | LEGAL | Research lane (deferred, conditional) |
| `CH-C10` | SEC | AI oversight acceptance + control-effectiveness report (`RV-10`, Phase 4) |

3. Open and partial items are tracked with owner, target phase, and evidence in
   [`docs/sprints/sprint-05/requires-validation-register.md`\](sprints/sprint-05/requires-validation-register.md).

### Sprint 6 Onboarding Minimum-Data and Re-identification Controls

Sprint 6 onboarding flows are governed by a minimum-sensitive-data design that
strengthens `CH-C01` (lawfulness, purpose limitation, data minimization) and
`CH-C05` (cross-border / residency) for the onboarding lanes. These controls map
to `NFR-COMP-011` and the register items in
[`docs/sprints/sprint-06/requires-validation-register.md`\](sprints/sprint-06/requires-validation-register.md).

| Onboarding control | Requirement | Enforcement | Owner role |
| ----- | ----- | ----- | ----- |
| Minimum-data patient onboarding contract (`DC-ONB-PATIENT-v1`) | `FR-ONB-001`, `NFR-COMP-011`, `CH-C01` | Validator rejects forbidden direct-identifier fields; pseudonym + age band only | SEC |
| Purpose limitation tags on onboarding records | `NFR-COMP-011`, `CH-C01` | `purposeTag` / `purposeTags` required by contract schema | SEC |
| Re-identification minimization (quasi-identifier control) | `NFR-COMP-011`, `CH-C01`, `CH-C05` | Banded age and day-granularity dates only; no free-text identifiers; tracked as `RV-06-04` | SEC |
| Swiss residency tag on onboarding datasets | `CH-C05` | `residency: CH` required by contract schema | LEGAL |
| Specialty metadata quality and versioning | `NFR-DQ-005` | `specialtyTaxonomyVersion` + capacity invariants in validator | ARCH |

The enforcement point is the synthesized-data gate
[`data/synthetic/validate_datasets.py`](../data/synthetic/validate_datasets.py),
run in CI by [`.github/workflows/data-contracts.yml`](../.github/workflows/data-contracts.yml).
Formal re-identification risk acceptance (`RV-06-04`) remains a Phase 2 legal /
security sign-off item; Phase 1 establishes the enforced minimization baseline.

### Demo-scope no-PHI baseline (2026-07-02)

Per [ADR-0016](adr/0016-no-phi-in-mvp-demo-scope.md), the MVP demo scope carries **no PHI** — no personal health information, no direct patient identifiers, no re-identifying combinations. Enforced at four gates:

1. **Schema gate** — CI check on `data/synthetic/schema/dc-*.schema.json`
2. **Ingestion gate** — Silver notebook PHI regex sweep (email, phone, DOB, CH AHV-13)
3. **Agent gate** — Every runtime agent prompt refuses PHI tokens; evals include a refusal fixture
4. **Dashboard gate** — Workspace RLS empty-set filter on any `phi=true` column

This ADR applies only to the demo scope defined by [ADR-0013](adr/0013-temporary-us-region-demo-scope.md). Future PROD Swiss deployments remain governed by [ADR-0003](adr/0003-swiss-regional-inference-for-phi.md) + [ADR-0004](adr/0004-block-global-and-data-zone-for-phi.md) + [ADR-0006](adr/0006-preview-features-non-production-rule.md).

### Sprint 23 Skills-Evidence DSG Tagging and Consent Lineage

Sprint 23 introduces workforce skills evidence (synthetic, no-PHI) via the
plugin architecture recorded in
[ADR-0050](adr/0050-curavias-landing-zone-and-skills-evidence-plugins.md). Although
the demo data is synthetic (`classification: personal-synthetic`), the records are
**personal in shape** (they describe individual workers), so the Swiss DSG
(revised Federal Act on Data Protection) control model is applied as if they were
real personal data. This strengthens `CH-C01` (purpose limitation, minimization)
and `CH-C05` (residency) for the skills-evidence lane.

| Skills-evidence control | Requirement | Enforcement | Owner role |
| ----- | ----- | ----- | ----- |
| Tag `gold.fact_skill_assertion` and `gold.dim_work_id_profile` as `PII-personal` | `FR-SKILL-007`, `NFR-SKILL-002`, `CH-C01` | Purview / catalog classification label on both gold assets; RLS + PHI-gate posture inherited from the demo-scope no-PHI baseline | SEC |
| Source-system + consent lineage on every assertion | `FR-SKILL-002`, `FR-SKILL-003`, `CH-C03` | `provenance.connectorVersion` + `externalSystem` record `source_system`; `consentScope` records the `consent_basis`; raw lineage in `provenance.rawHash` | ARCH |
| Work-ID consent is first-class and revocable | `FR-SKILL-003`, `CH-C01`, `CH-C05` | `worker_gln` promotion and `consentScope` are set **only** when Work-ID consent is granted (Step-3 §4); revocation removes the GLN promotion and the consented scope on the next load; Work-ID assertions stay `self`-declared (L0) regardless of consent | SEC |
| Purpose limitation on skills datasets | `NFR-SKILL-002`, `CH-C01` | `purposeTags` (`skills-evidence`, `workforce-capability`) required by the `DC-SKILL-EVIDENCE-v1` schema | SEC |
| Swiss residency tag on skills datasets | `CH-C05` | `residency: CH` required by contract (`demo-westus2` only under [ADR-0013](adr/0013-temporary-us-region-demo-scope.md)) | LEGAL |

The enforcement point for landed data is the **pipeline silver gate**
(`FR-SKILL-006`): PK/FK, GLN mod-10, enum domains, and load order are validated
against landed Bronze, quarantining bad rows in Silver rather than at PR time.
Assurance derivation (`self` -> L0, `employer_confirmed` -> L1) and the live-vs-simulated
badge are preserved end-to-end and never invented downstream (`FR-SKILL-007`).

#### Near-real-time skills-events lane consent enforcement (`FR-SKILL-005`)

The narrow WS-A4 Eventstream lane (`DC-SKILL-EVENT-v1`) carries the three
near-real-time events (credential expiry, consent grant/revoke, newly-confirmed
assertion). Its silver gate
(`data-platform/notebooks/skills-events/build_silver_skill_events.py`) is the
downstream PHI-gate the Eventstream module defers to, and it enforces the same
`CH-C01` / `CH-C05` consent posture as the batch lane at event granularity:

| Skills-event control | Requirement | Enforcement |
| ----- | ----- | ----- |
| Consent revocation removes the GLN promotion | `FR-SKILL-003`, `CH-C01` | On a `revoke` event the silver gate **defensively clears** `workerGln` + `consentScope` even if the upstream payload still carried them, so a revoked worker can never be promoted on the next load |
| Grant carries the promotion, revoke never asserts one | `FR-SKILL-003` | A `grant` event must carry both `workerGln` and `consentScope` or it is quarantined (deny-by-default); non-consent events carrying a `consentAction` are quarantined |
| Live-vs-simulated badge preserved on events | `FR-SKILL-007` | `sourceMode` (live \| simulated) + `trustTier` travel from the contract through Bronze/Silver and surface on `gold.skillevt_fact_event`; never invented downstream |
| Synthetic-only event data | `NFR-SKILL-002` | The event seeder is deterministic and git-owned; envelopes are synthetic, no-PHI (ADR-0013 / ADR-0016) |
| Live ingestion secrets never in repo | `CH-C05`, `NFR-SKILL-001` | The SIT lane is live-wired with a `CustomEndpoint` source (`es-ihzhhpf-skills-events`, demo-scope ADR-0013). Its Event-Hub-compatible ingestion connection string (SharedAccessKey) is retrieved at publish-time via `GET …/eventstreams/{id}/sources/{sourceId}/connection` and stored in Key Vault — **never committed**. The Container Apps publisher reads it from Key Vault at runtime |
| PROD-swn EventHub source uses a secretless Fabric-managed connection | `CH-C05`, `NFR-SKILL-001`, [`ADR-0043`](adr/0043-preview-tier-permitted-in-prod-swn-for-demo.md) | The PROD Switzerland North lane runs in `sourceMode=EventHub` (GA-in-region). The Eventstream binds to the dedicated skills-events hub through a **Fabric-managed connection** (`POST /v1/connections`, Entra/MI auth) — **no SharedAccessKey or connection string** is generated, stored, or committed. The simulator publishes via **Managed Identity `Azure Event Hubs Data Sender`** scoped to the dedicated hub |
| Per-domain envelope isolation on the event rail | `NFR-SKILL-002`, `CH-C03` | The `DC-SKILL-EVENT-v1` envelope lands on a **dedicated `skills-events` Event Hub entity + `cg-skills-eventstream` consumer group**, separate from the capacity `events` rail, so skills events are isolated by functional domain end-to-end |
| SIT and PROD do not share input services | `NFR-SKILL-002`, `CH-C05` | SIT (`evh-ihzhhpf-sit-*`, westus2/eastus2) and PROD (`evh-ihzhhpf-prod-i62t`, switzerlandnorth) use **separate Event Hubs namespaces, resource groups, and regions**; no input service is shared across environments |
| Synthetic-only event publishing in PROD swn | `NFR-SKILL-002`, [`ADR-0043`](adr/0043-preview-tier-permitted-in-prod-swn-for-demo.md) | Until the live HRIS/LMS connector lands, `publish_skill_events.py` emits deterministic synthetic `sourceMode=simulated` records only; the GA-only gate is reserved for a real go-live (real-PHI) cut-over |

### Sprint 31 Data Quality Agent Proactive Assessment (no-PHI, degraded-mode, audit)

Sprint 31 (issue #453,
[ADR-0053](adr/0053-dqa-trust-score-model.md)) elevates the
`data-quality-agent` from ingestion gates to proactive assessment of the
gold/serving layer via a deterministic per-domain trust score
(`DC-DQ-TRUSTSCORE-v1`) and gap detection with impact (`DC-DQ-GAP-v1`). The
agent is **advisory, human-in-the-loop, and read-only** — it never mutates
source data; the owning domain remediates.

| Data-quality control | Requirement | Enforcement | Owner role |
| ----- | ----- | ----- | ----- |
| Assessment operates on synthetic governance metadata only, no PHI | `NFR-DQA-002`, `CH-C01`, [`ADR-0016`](adr/0016-no-phi-in-mvp-demo-scope.md) | The agent scores governed metadata (freshness, completeness, lineage, conformance) over synthetic no-PHI gold assets; a golden-task fixture asserts refusal of any request to read or emit PHI | SEC |
| Below-threshold domains are withheld, never served as trusted | `FR-DQA-006`, `FR-DQA-012` | When a domain scores below its per-decision-class threshold the grounding-readiness certificate is withheld and grounding is served **degraded or withheld**, preventing a false-trusted answer | ARCH |
| Findings are GitHub-native and auditable, routed to the owner | `FR-DQA-010`, `NFR-DQA-001` | `DC-DQ-TRUSTSCORE-v1` / `DC-DQ-GAP-v1` records are emitted as auditable GitHub-native artefacts and routed to the owning domain; the agent does not self-certify grounding | SEC |
| Read-only Zero-Trust posture; owner remediates | `NFR-DQA-002`, `FR-DQA-004`, `FR-DQA-005` | The agent's side-effect ceiling stays `write` (repo artefacts only) and it refuses `edit-source-data`; remediation is owner-driven, never agent-applied | SEC |

## Microsoft Purview Coverage Evaluation (GA and IaC)

This section defines how Microsoft Purview contributes to the control set
CH-C01 to CH-C10, based on currently documented GA and automation capability.

### Purview Control Fit

| Control ID | Purview contribution | Delivery model |
| ----- | ----- | ----- |
| CH-C01 | Data catalog, classification, lineage, and metadata stewardship support purpose and minimization governance | Hybrid: IaC for account baseline + operational catalog workflows |
| CH-C03 | Auditability and lineage capabilities support traceability evidence | Hybrid: service provisioning via IaC, evidence workflows operational |
| CH-C05 | Sensitivity labels and policy frameworks can support transfer and disclosure governance signals | Mostly operational policy configuration |
| CH-C10 | Compliance and governance solutions support AI-related data governance evidence and oversight context | Mostly operational policy and reporting workflows |

### Purview GA and IaC Boundary

| Capability | Current status for this architecture | Implementation rule |
| ----- | ----- | ----- |
| Purview account resource deployment | IaC-ready | Deploy via Bicep/ARM in landing-zone baseline |
| Account-level identity/network controls | IaC-ready | Enforce in infrastructure lane before workload onboarding |
| Collections and scan onboarding | Not fully declarative end-to-end in Bicep guidance | Execute through controlled automation runbooks after infra deployment |
| Ongoing compliance policy configuration and tuning | Operational | Manage through controlled change process and evidence artifacts |

### Compliance Implementation Rule

For this repository, Purview shall be treated as:
1. A mandatory governance accelerator for metadata, lineage, and evidence
	controls where workload scope requires it.
2. A two-lane implementation model:
	- lane A: IaC for account and baseline security posture,
	- lane B: operational automation for catalog, scans, and policy lifecycle.
3. A region-gated control plane where production use for PHI controls requires
	explicit GA confirmation for the selected region and feature.

## Evidence Model

### Evidence Categories

| Evidence ID | Evidence artifact | Owner | Frequency | Gate |
| ----- | ----- | ----- | ----- | ----- |
| E-01 | Data processing inventory with purpose and legal basis tags | Data governance | Quarterly and on major release | Architecture review |
| E-02 | Access control evidence (role matrix, privileged access reviews, JIT records) | Security | Monthly | Release and audit |
| E-03 | Residency and egress policy verification report | Platform engineering | Each release | Deployment gate |
| E-04 | Logging and traceability evidence (sampled audit trails, retention proof) | Platform engineering | Monthly | Operations review |
| E-05 | DSR workflow evidence (request logs, SLA compliance, outcomes) | Privacy office | Monthly | Compliance review |
| E-06 | Privacy incident drill and real-incident postmortems | SecOps + Privacy | Quarterly and post-incident | Risk committee |
| E-07 | AI safety and oversight report (quality, drift, override and escalation stats) | AI governance | Monthly | AI change approval |
| E-08 | EPR conformance evidence package (if EPR enabled) | Integration lead | Before go-live and annually | External conformance |
| E-09 | Research governance packet (if HRA in scope) | Research governance | Per study and annual | Ethics and legal approval |

### Minimum Release Checklist

- Residency controls for PHI validated in CI and pre-deploy.
- Access and logging controls validated against CH-C03 and CH-C07.
- DSR and incident response operational checks completed.
- AI oversight controls validated for affected workflows.
- Evidence artifacts E-01 to E-07 attached to release record.

## Sources and Traceability Notes

- All legal references in this document are from Swiss federal official sources
	(Fedlex and federal administration websites where available).
- For implementation decisions, cite both:
	- legal source URL, and
	- internal control ID (CH-Cxx) in PR descriptions and ADR updates.
- When this file is updated with article-level legal interpretation,
	include reviewer sign-off from legal/compliance.

## Next Steps

1. Create a control implementation tracker in docs/compliance mapped to CH-C01 to CH-C10.
2. Add CI policy checks for residency and PHI transfer guardrails.
3. Add operational runbooks for DSR and privacy incident response.
4. Add evidence collection templates for E-01 to E-09.
5. Add canton-specific annex once target canton rollout plan is fixed.
   Seeded in [`docs/compliance/cantonal-annex.md`](compliance/cantonal-annex.md) (Sprint 05).

