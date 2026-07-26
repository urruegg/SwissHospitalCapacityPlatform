# Sprint 23 Refactor - Unified Curavias Organisation + Skills-Evidence Platform (Design)

| Field | Value |
| ----- | ----- |
| **Version** | 1.4.0 |
| **Date** | 2026-07-25 |
| **Author** | Urs Rueegg (with Copilot) |
| **Status** | Approved (brainstorming) |
| **Previous Version** | 1.3.0 (EventHub flip un-parked for PROD swn — ADR-0043) |
| **Sprint** | [Sprint 23 - Unified Curavias organisation spine + org/skills ontology (P1b)](../../sprints/sprint-23-curavias-org-spine-and-skills-ontology.md) |
| **Issue** | [#255](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255) |
| **Extends** | Idea pack [`unified-curavias-organisation-and-skills-ontology/`](../ideas/unified-curavias-organisation-and-skills-ontology/) (Steps 1-4 + 20 CSVs + generator); shared design [`2026-07-19-curavias-shared-master-data-and-ontology-design.md`](2026-07-19-curavias-shared-master-data-and-ontology-design.md) |
| **Depends on** | Sprint 22 (P1a, #254) - **landed 2026-07-19** (`gold.*` medallion + `upload_to_onelake.py` + `verify_gold_schema.py`) |
| **Mirrors** | Sprint 21 signal-provider plugin pattern (`data-platform/scripts/external-signals/`) |

> **For agentic workers:** This is the approved design for the Sprint 23 refactor. The
> implementation plan is produced separately via `superpowers:writing-plans` and executed
> via `superpowers:subagent-driven-development`. The brainstorming HARD-GATE is satisfied:
> this design was approved (interactive brainstorm, 2026-07-23) before any production code.

---

## 1. Why this refactor

The base Sprint 23 plan (#255, tasks T1-T10) folds `dim_hospital` into the Curavias
organisation spine and adds the org/skills master-data domain as `gold.*` tables, extending
the semantic model, ontology and Fabric IQ grounding. Four new requirements arrived that the
base plan does not cover:

1. **MCAPS tenant restriction.** The MCAPS tenant cannot provision the sample users /
   workforce records in Microsoft Entra. The full synthetic Curavias master data (employees,
   assertions, org spine) therefore needs a **dedicated upload location** that is loaded
   **on demand** via a Data Pipeline (Bronze -> Silver -> Gold), rather than living in Entra.
2. **Skills-evidence sources as a plugin architecture.** Skills evidence must be gathered
   from external systems through a **plugin architecture** - real-API adapters where an API
   exists, **simulators** where none does - mirroring the Sprint 21 signal-provider pattern,
   each flagged **live-vs-simulated**.
3. **Mimic the key evidence systems.** No real system is in place yet; the platform mimics
   **SuccessFactors** (HRIS), an **LMS** (learning/cert store) and **Skills-Manager with
   Work-ID** (worker-owned skills passport) as simulated sources.
4. **Bed vs Ops demand split.** The semantic + ontology surface must express which skills are
   required on the **bed** side (Pflegepersonal / nursing) and on the **ops** side (Doctors
   and specialised teams), extending the existing staff/person ontology view.

This design covers the deltas; T1-T10 of #255 remain in force and are cross-referenced.

## 2. Locked decisions (brainstorm 2026-07-23)

| # | Decision | Rationale |
| - | -------- | --------- |
| D1 | **Dedicated Azure landing zone (out-of-band upload)**, not git-committed extracts | Requirement #1; extracts are uploaded to a landing zone and loaded on demand. Data validation therefore moves from git-CI to the **pipeline silver gate**. The **generator stays git-owned** for reproducibility. |
| D2 | Landing zone surface = **ADLS Gen2 container + OneLake shortcut**, Bicep-provisioned | Enterprise-realistic, decoupled from Fabric, uploadable via `az`/portal; the pipeline reads it through a OneLake shortcut. |
| D3 | **Skills-evidence plugin package mirrors Sprint 21** (`connectors/base_connector.py` + per-source adapters + `normalize.py` + `*_synth.py` + `tests/`) | Requirement #2/#3; one proven pattern for both signals and skills evidence. All four sources **simulated now**, adapters shaped so a real API can slot in without touching the ontology. |
| D4 | **Hybrid transport** - batch extract drops to the ADLS landing zone for HRIS/LMS master data; **Eventstream** lane only for near-real-time skills events | Skills evidence is periodic master-data (HRIS/LMS export nature); the Eventstream lane covers credential expiry, consent grant/revoke and newly-confirmed assertions. Honours the standing rule: ingestion/simulation run as **Azure services (Container Apps)**, never GitHub workflows. |
| D5 | **Validation at the silver gate** (PK/FK, GLN mod-10, enum domains, load order) | Consequence of D1 - extracts are not in git, so `validate_master_data.py` logic runs inside the pipeline against landed Bronze, quarantining bad rows in Silver. |
| D6 | Reuse the Step 1-4 ontology, schema and connector design verbatim; **extend, don't replace** | The atomic unit stays `fact_skill_assertion`; the two axes (proficiency 1-5, assurance L0-L4) and the GLN golden thread are unchanged; Gold stays deny-by-default. |

## 3. Target architecture

### 3.1 Ingestion and landing zone

```text
Container Apps simulator jobs (SuccessFactors / LMS / Skills-Manager / Work-ID)
        │  (on-demand run -> batch extract files)
        ▼
ADLS Gen2  st<...>masterdata / landing/curavias-org-skills/<source>/<yyyy-mm-dd>/*.{csv,json}
        │  (OneLake shortcut)
        ▼
Fabric lakehouse  Files/landing/curavias-org-skills/...
        │  on-demand Fabric Data Pipeline
        ▼
bronze.*  (raw typed copy)
        │  Silver gate: type-cast · VALIDATE (PK/FK · GLN mod-10 · enum · load order)
        │             · dedupe · assurance L0-L4 · ESCO crosswalk · quarantine bad rows
        ▼
silver.* (typed, validated, quarantined)
        │  Gold gate: deny-by-default (assurance >= L2 valid; L4 where legally required)
        ▼
gold.*   (19 org/skills tables -> semantic model + ontology + Fabric IQ Data Agent)
```

- **Upload contract:** one folder per source per load date; files match the Step-4 CSV
  schemas (or the canonical inbound record for connector sources, section 3.2).
- **On-demand trigger:** the Fabric Data Pipeline is run on demand (manual / parameterised),
  not on a git push. SIT and PROD use the **same** parameterised pipeline (`--workspace-id`
  / `--lakehouse-id` / `--source-root`), consistent with `upload_to_onelake.py`.
- **Infra:** the ADLS account + `landing` container + the OneLake shortcut + the Container
  Apps simulator jobs are added to the Bicep landing zone (WS-A).

### 3.2 Skills-evidence plugin architecture (mirrors Sprint 21)

New package `data-platform/scripts/skills-evidence/`, shaped exactly like
`external-signals/`:

```text
data-platform/scripts/skills-evidence/
  connectors/
    base_connector.py         # shared abstract adapter (mode, fetch, to_canonical)
    successfactors.py         # HRIS adapter  (simulated now; real-API-ready)
    lms.py                    # learning/cert adapter (simulated now)
    skills_manager.py         # Skills-Manager company inventory (Step 3 modes A/B/C)
    work_id.py                # Work-ID worker passport (consent-gated, GLN-optional)
  normalize.py                # source payload -> DC-SKILL-EVIDENCE-v1 envelope
  dedup.py
  skills_evidence_synth.py    # dependency-free simulator seeder (all four sources)
  tests/
data-platform/notebooks/skills-evidence/
  ingest_bronze_skills.py  build_silver_skills.py  build_gold_skills.py
```

**Data contract `DC-SKILL-EVIDENCE-v1`** (extends the Step-3 canonical inbound record with
the Sprint-21 trust fields):

```yaml
skill_evidence_record:
  external_system:      successfactors | lms | skills_manager | work_id
  source_mode:          live | simulated        # the live-vs-simulated BADGE origin
  trust_tier:           A | B | C               # A auto-usable; B/C review (mirrors DC-EXT-SIGNAL-v1)
  external_person_ref:  string
  worker_gln:           string?                 # present only on consent (promotion key)
  external_skill_code:  string
  external_skill_label: string
  self_or_confirmed:    self | employer_confirmed   # drives L0 vs L1
  external_level:       string?                 # vendor proficiency label [confirm scale]
  consent_scope:        string?                 # Work-ID only
  captured_at:          date
```

- **Badge:** `source_mode` (and `trust_tier`) travel in the contract, are preserved through
  Bronze/Silver, and surface as a **live-vs-simulated indicator** on `gold.fact_skill_assertion`
  (and its semantic-model measure) - never invented in the UI. This is the skills analogue of
  the Sprint 21 `trustTier`/`status` badge.
- **Assurance placement (Step 3):** connector sources enter at **L0/L1** and only earn L2+ by
  GLN reconciliation against the federal registers; Gold stays deny-by-default. Simulated ==
  no override of the safety-critical floor.
- **All four simulated now**; each adapter exposes the same `base_connector` surface so a real
  SuccessFactors/LMS/Skills-Manager API is a drop-in later (`source_mode: live`).

### 3.3 Hybrid transport (D4)

| Lane | Carries | Mechanism |
| ---- | ------- | --------- |
| **Batch** | HRIS/LMS/company-inventory master-data extracts | Container Apps simulator job -> extract files -> ADLS landing zone -> on-demand Data Pipeline |
| **Eventstream** | Near-real-time skills events: credential expiry, consent grant/revoke, newly-confirmed assertion | Container Apps service -> Eventstream -> lakehouse `bronze_skills_events`. **Live in SIT via a `CustomEndpoint` source** (demo-scope, ADR-0013); the `sourceMode=EventHub` rail is **un-parked for PROD Switzerland North** ([ADR-0043](../../adr/0043-preview-tier-permitted-in-prod-swn-for-demo.md)) — Eventstream + Event Hubs are **GA in swn** and the PROD EH namespace `evh-ihzhhpf-prod-i62t` exists in-region; a **dedicated skills-events Event Hub** carries `DC-SKILL-EVENT-v1` (per-domain envelope), fed by a **simulator** until the live publisher lands (see §6). |

The Eventstream lane is intentionally narrow - only events that must move faster than the next
batch load. Everything else is batch.

### 3.4 Ontology and semantic model

- **Replace `dim_hospital`** with `dim_tenant` / `dim_org_unit` / `dim_department` (per #255 T4
  and the shared design). BVA keeps its separate `bva_dim_hospital`.
- **Skills measures:** supply / demand / gap / eligibility (per #255 T6), plus a
  **live-vs-simulated** measure driven by `source_mode`.
- **Bed vs Ops demand split (requirement #4):** modelled on `bridge_role_skill_demand_template`
  and `fact_skill_demand` via a `care_setting` dimension = `bed` (Pflegepersonal / nursing) |
  `ops` (Doctors + specialised teams). Demand templates and gap measures are reported per
  `care_setting`, so the app can answer "which nursing skills are short on ward X" separately
  from "which OR/anaesthesia skills are short in theatre Y".
- **Fabric IQ:** extend `ont_hospital_capacity` + the Data Agent grounding to cover the
  org/skills concepts and the care-setting split (per #255 T8-T9).

### 3.5 Governance and security

- **New ADR** (landing zone + skills-evidence plugin architecture + hybrid transport) - Accepted
  before merge, per the repo ADR rules; supersede/relate to the shared design where needed.
- **DSG:** tag `fact_skill_assertion` and `dim_work_id_profile` as `PII-personal`; record
  `source_system` / `consent_basis` lineage in Purview; Work-ID consent is first-class and
  revocable (Step 3 section 4).
- **PRD:** add FR/NFR rows for the landing zone, the plugin sources and the bed-vs-ops split;
  update the section 7 traceability matrix.
- **CI:** re-baseline `verify-semantic-model.yml` exact counts in the **same PR** as the model
  expansion (Sprint 22 pattern); extend `verify_gold_schema.py` parity for the new tables.
- **No PHI / synthetic only** (ADR-0013 / ADR-0016).

## 4. Sub-agent decomposition (parallel workstreams within the Sprint 23 session)

| WS | Scope | Key deliverables | Depends on |
| -- | ----- | ---------------- | ---------- |
| **WS-A Infra** | ADLS landing zone + OneLake shortcut + Container Apps simulator jobs + Eventstream lane | Bicep modules + params; `az`/portal upload runbook; `what-if` clean | - |
| **WS-B Data** | Relocate generator to `data/master-data/curavias-org-skills/`; skills-evidence plugin package + simulators + tests; Bronze/Silver/Gold pipeline notebooks; silver validation gate | Green tests; pipeline produces `gold.*`; badge preserved end-to-end | WS-A (landing zone) |
| **WS-C Semantic/Ontology** | Replace `dim_hospital`; skills + care-setting measures; ontology + crosswalk + Fabric IQ grounding; CI count rebaseline | Semantic model validates; conformance green; Data Agent cites org/skills + care-setting | WS-B (gold tables) |
| **WS-D Governance** | New ADR; PRD FR/NFR + section 7 matrix; DSG tagging; docs version bumps | Doc gates green; ADR Accepted | runs alongside |

Slice each WS into short-lived branches off `main` per ADR-0038; **human reviews + merges**
every PR; any deploy/delete hard-gated by `approved-to-apply`.

## 5. Definition of Done

- [ ] ADLS landing zone + OneLake shortcut provisioned (Bicep, `what-if` clean); upload runbook documented
- [ ] Container Apps simulator jobs for SuccessFactors / LMS / Skills-Manager / Work-ID emit batch extracts to the landing zone on demand
- [x] Eventstream lane carries the three near-real-time skills events — in-repo data lane landed 2026-07-25 (`DC-SKILL-EVENT-v1` contract + seeder + Bronze/Silver/Gold notebooks + 23 tests); **live-wired in SIT 2026-07-25** (`es-ihzhhpf-skills-events` Running, `CustomEndpoint` source → `bronze_skills_events`, `approved-to-apply` #374). *Remaining: skills-events simulator + `EventHub`-source flip (un-parked for PROD swn per [ADR-0043](../../adr/0043-preview-tier-permitted-in-prod-swn-for-demo.md); GA-in-swn, needs the Fabric-managed connection) + live publisher (fast-follow).*
- [ ] `data/master-data/curavias-org-skills/` created (generator relocated; **path mismatch in the sprint doc fixed**)
- [ ] Skills-evidence plugin package + `DC-SKILL-EVIDENCE-v1` + simulators + tests green
- [ ] On-demand Data Pipeline: Bronze -> Silver (validate + quarantine) -> Gold (deny-by-default) produces the org/skills `gold.*` tables
- [ ] `dim_hospital` replaced; facts re-keyed; consumers re-pointed (#255 T4-T5)
- [ ] Semantic model: skills + live-vs-simulated + bed-vs-ops (`care_setting`) measures; `verify-semantic-model.yml` re-baselined + green
- [ ] Ontology + crosswalk + conformance + Fabric IQ Data Agent cover org/skills + care-setting
- [ ] New ADR Accepted; PRD FR/NFR + section 7 updated; DSG tagging applied
- [ ] SIT + PROD deployed identically; live applies gated by `approved-to-apply`; PR merges human-performed
- [ ] All CI checks pass

## 6. Open items / to confirm

- **Vendor mechanics** (SuccessFactors/LMS/Skills-Manager/Work-ID API + proficiency scale) stay
  behind the adapter and are `[confirm with vendor]` (Step 3) - simulated until confirmed.
- **Eventstream event set** may grow; start with expiry / consent / new-confirmed-assertion.
- **Eventstream source transport (D4) — RESOLVED 2026-07-25; EventHub flip un-parked 2026-07-25.**
  The lane was live-wired in SIT with a **`CustomEndpoint`** source (demo-scope, ADR-0013),
  mirroring the working `es-capacity-events-sit`: fully deployable today, a publisher POSTs to the
  Eventstream ingestion endpoint. The `sourceMode=EventHub` rail is **no longer parked behind a
  "Swiss GA" milestone** — per [ADR-0043](../../adr/0043-preview-tier-permitted-in-prod-swn-for-demo.md),
  preview-tier services are approved in PROD Switzerland North for the demo and the GA-only gate is
  reserved for real go-live cut-over. In fact the EventHub flip is **GA in Switzerland North**
  (Eventstream + Event Hubs), so it does not even consume the preview exception; its only remaining
  prerequisite is the out-of-band Fabric-managed connection (`POST /v1/connections`) to
  `evh-ihzhhpf-prod-i62t`. Confirmed design points (2026-07-25): a **dedicated skills-events Event
  Hub** (per-functional-domain envelope, not shared with the capacity `events` rail); a **simulator**
  feeds it until the live publisher is ready; **SIT and PROD do not share input services**
  (`evh-ihzhhpf-sit-y26y` westus2 vs `evh-ihzhhpf-prod-i62t` swn).
  **IMPLEMENTED 2026-07-25 (deploy-class, `sprint-23/eh-flip-execution`):** the
  `data-foundation/eventhubs` module provisions the dedicated `skills-events` hub +
  `cg-skills-eventstream` group (auto-enabled when the skills lane runs `sourceMode=EventHub`);
  `prod-swn.bicepparam` sets `sourceMode=EventHub`; the post-deploy script gained an `AzureEventHub`
  source branch (`-ConnectionId` Fabric-managed connection); and `publish_skill_events.py` is the
  synthetic simulator. The `DC-SKILL-EVENT-v1` contract is unchanged (transport-only change;
  backwards-compatible default). The live PROD apply + `POST /v1/connections` remain gated by
  `approved-to-apply`.
- **`validate_master_data.py`** was not found on disk during design (only `upload_to_onelake.py`
  and `verify_gold_schema.py`); WS-B confirms whether the Sprint 22 validator exists under another
  name or must be authored for the silver gate.

## 7. References

- Idea pack: [`unified-curavias-organisation-and-skills-ontology/`](../ideas/unified-curavias-organisation-and-skills-ontology/) - Step 1 (ontology), Step 2 (Swiss sources), Step 3 (Work-ID/Skills-Manager), Step 4 (schema + 20 CSVs + generator)
- Sprint doc: [`sprint-23-curavias-org-spine-and-skills-ontology.md`](../../sprints/sprint-23-curavias-org-spine-and-skills-ontology.md) (#255)
- Shared design: [`2026-07-19-curavias-shared-master-data-and-ontology-design.md`](2026-07-19-curavias-shared-master-data-and-ontology-design.md)
- Sprint 21 pattern: `data-platform/scripts/external-signals/` + `docs/superpowers/specs/2026-07-17-sprint-21-trusted-external-signals-fabric-design.md`
- Sprint 22 (prerequisite, landed): `data/master-data/capacity/`, `data-platform/scripts/upload_to_onelake.py`, `verify_gold_schema.py`
- Governance: ADR-0013 (US demo scope), ADR-0016 (no PHI), ADR-0038 (trunk-based parallel workflow)
