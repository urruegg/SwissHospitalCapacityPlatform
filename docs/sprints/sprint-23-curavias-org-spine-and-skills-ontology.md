# Sprint 23 — Unified Curavias Organisation Spine + Org/Skills Ontology (P1b)

| Field | Value |
| ----- | ----- |
| **Version** | 1.11.0 |
| **Date** | 2026-07-27 |
| **Author** | @urruegg |
| **Status** | In progress — repo scope complete + all CI gates green; **live SIT medallion clean**; **ADR-0039 Accepted**; **PROD org/skills parity APPLIED**; **skills-events near-real-time lane (WS-A4 / FR-SKILL-005) data lane landed** (DC-SKILL-EVENT-v1 + seeder + Bronze/Silver/Gold + 28 unit tests) **and LIVE-WIRED in SIT** (Eventstream `es-ihzhhpf-skills-events` Running, CustomEndpoint source → `bronze_skills_events`, `approved-to-apply` #374); **EventHub flip un-parked + IMPLEMENTED for PROD swn** (ADR-0043; live EH bind deferred on Fabric workspace-identity GA); **PROD org/skills medallion (28 gold tables) + `capacity-dashboard`/`external-signals` semantic models + report MATERIALIZED LIVE in Switzerland North** (`approved-to-apply` @urruegg, 2026-07-26/27; [PROD execution record](sprint-23/evidence/2026-07-27-prod-medallion-and-model-publish-execution-record.md)); **remaining: live skills publisher image + e2e SIT/PROD parity test + EventHub live bind (Fabric GA)** |
| **Previous Version** | 1.10.0 (skills-events near-real-time lane live-wired in SIT + EventHub flip un-parked) |

> **Sprint theme.** Fold `dim_hospital` into a unified Curavias organisation hierarchy (three Curavias tenants **replace** today's hospital rows), add the Curavias organisation + skills master-data domain as first-class `gold.*` tables, and extend the semantic model, ontology, crosswalk, and Fabric IQ Data Agent grounding. This is **Part 1b** of the Curavias shared-master-data design.

---

## 1. Sprint goal

Reconcile the operational capacity model with the real (synthetic) Curavias organisation: retire `dim_hospital`, introduce the `dim_tenant` / `dim_org_unit` / `dim_department` spine, add the workforce skills domain (supply / demand / gap / eligibility), and extend every downstream contract — semantic model, ontology, crosswalk, conformance gate, and the Fabric IQ ontology + Data Agent grounding — so both the operational agents and the Foundry IQ agents reason over one unified organisation spine.

**Success shape:**

* The 20 Curavias org/skills CSVs + generator are git-owned under `data/master-data/curavias-org-skills/`, validator-gated (GLN mod-10, enum domains, FK integrity).
* An org/skills medallion produces the 19 `gold.*` tables.
* `dim_hospital` is replaced by the three Curavias tenants (CuraNova / Curalp / Vialta) via `_hospital_to_org_crosswalk.csv`; `fact_capacity_baseline`, `encounter`, `bed_assignment`, `or_case`, and `or_schedule` are re-keyed; the semantic model, report visuals, and `sim-capacity` generators are re-pointed. **BVA keeps its separate `bva_dim_hospital`.**
* The ontology + crosswalk + conformance gate and the Fabric IQ ontology `ont_hospital_capacity` + Data Agent grounding cover the organisation + skills domain.

---

## 2. Source baseline

1. [Design Spec — Curavias shared master data + ontology](../superpowers/specs/2026-07-19-curavias-shared-master-data-and-ontology-design.md) — §4.5 (unified spine + org/skills), §5 (Part 2 agent design-only), §6 (governance)
2. [Curavias idea package](../superpowers/ideas/unified-curavias-organisation-and-skills-ontology/) — Step 1 (ontology extension), Step 2 (Swiss competency sources), Step 3 (Work-ID / Skills-Manager), Step 4 (master-data schema) + 20 CSVs + `generate_master_data.py`
3. [Sprint 22 — Golden-source + reproducible medallion (P1a)](sprint-22-curavias-golden-source-reproducible-medallion.md) — **prerequisite** (provides the modernized `gold.*` notebooks this sprint extends)
4. [`docs/ontology/`](../ontology/) — reference ontology, crosswalk, and conformance design this sprint extends
5. `data-platform/scripts/export_semantic_model_tmdl.ps1` + `.github/workflows/verify-semantic-model.yml` — the exact-count CI gate to re-baseline

> **Implementation plan:** authored **after** Sprint 22 lands, because the P1b tasks depend on the modernized `gold.*` notebooks and the re-keying crosswalk produced there.

---

## 3. Sprint scope

| # | Task | Deliverable | DoD |
|---|------|-------------|-----|
| T1 | Relocate org/skills master data | 20 CSVs + generator under `data/master-data/curavias-org-skills/` + README | Git-moved; provenance recorded |
| T2 | Extend validator | GLN mod-10, enum domains, cross-CSV FK integrity + tests | Tests fail then pass; real data valid |
| T3 | Org/skills medallion | bronze/silver/gold notebooks -> 19 `gold.*` tables | Managed tables; parity check extended |
| T4 | Replace `dim_hospital` | `_hospital_to_org_crosswalk.csv` + re-key facts to `dim_tenant` | No `dim_hospital`; facts re-keyed |
| T5 | Re-point consumers | Semantic model, report visuals, `sim-capacity` generators | Visuals render; generators emit org keys |
| T6 | Skills measures | supply / demand / gap + eligibility measures | Measures validate in the model |
| T7 | Re-baseline CI gate | Bump `verify-semantic-model.yml` exact counts | Gate green with new counts |
| T8 | Extend ontology | `docs/ontology/` + `crosswalk.md` + conformance gate | Conformance green |
| T9 | Extend Fabric IQ | `ont_hospital_capacity` + Data Agent grounding cover org/skills | Data Agent cites org/skills concepts |
| T10 | Governance | New ADR (unified spine) + PRD FR/NFR + §7 matrix | Doc gates green; ADR Accepted |
| T11 | Dedicated landing zone (refactor) | ADLS Gen2 container + OneLake shortcut (Bicep) + upload runbook | `what-if` clean; extracts load on demand |
| T12 | Skills-evidence plugins (refactor) | `data-platform/scripts/skills-evidence/` package (base connector + SuccessFactors/LMS/Skills-Manager/Work-ID adapters + simulators + tests) + `DC-SKILL-EVIDENCE-v1` | Tests green; live-vs-simulated badge preserved to gold |
| T13 | Hybrid transport (refactor) | Container Apps batch simulator jobs -> landing zone; Eventstream lane for near-real-time skills events | Batch loads + event lane demonstrated |
| T14 | Bed vs Ops demand split (refactor) | `care_setting` (bed/ops) dimension on demand templates + gap measures; ontology + Data Agent grounding | App reports nursing vs ops skill gaps separately |

> **Refactor scope (2026-07-23).** T11-T14 add the dedicated Azure landing zone + on-demand
> pipeline, the Sprint-21-style skills-evidence plugin architecture (all sources simulated now),
> the hybrid batch/Eventstream transport, and the bed-vs-ops skill-demand split. Design:
> [`2026-07-23-sprint-23-org-skills-refactor-design.md`](../superpowers/specs/2026-07-23-sprint-23-org-skills-refactor-design.md).

---

## 4. Key decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | The three Curavias tenants **replace** `dim_hospital` rows (no back-compat alias) | User-confirmed (Q1): one unified organisation spine, not a parallel dimension. |
| D2 | Facts re-keyed via a one-time `_hospital_to_org_crosswalk.csv` | Deterministic, reviewable mapping from legacy `hospital_id` to `tenant_id` / `org_unit_id`. |
| D3 | **BVA stays a separate `bva_*` domain** with its own `bva_dim_hospital` | User-confirmed (Q2): BVA's cost/value model must not be entangled with the operational spine. |
| D4 | Part 2 (agent extension) is **design-only** this sprint | Land the data + ontology spine first; wire the operational + Foundry agents to the extended ontology in a follow-up build sprint. |
| D5 | Skills competency sourced from the Step-2 Swiss references, synthetic only | ADR-0013 / ADR-0016 — demo scope, no PHI, no real workforce records. |

---

## 5. Definition of Done

> **Reconciliation (2026-07-23).** Verified against merged PRs and a full local
> gate sweep. Repo-artifact scope is complete; the two unticked items are live
> infra/governance operations that run outside this repo (Container Apps →
> Event Hub/Eventstream deploy, gated by `approved-to-apply`) or need human
> sign-off (ADR acceptance).

* [x] Sprint 22 (P1a) landed — modernized `gold.*` notebooks available
* [x] P1b implementation plan authored and approved (design PR #309; plan `docs/superpowers/plans/2026-07-23-sprint-23-org-skills-refactor-plan.md`)
* [x] Org/skills CSVs + generator under `data/master-data/curavias-org-skills/`; validator green (#314; `validate_master_data.py` + 13 tests green)
* [x] Org/skills medallion produces the `gold.*` tables; parity check extended — *build scripts + parity contract green in-repo (#330/#334/#341, gold-build 28 + contract 5 tests); **live SIT Fabric run landed 2026-07-24** (full `run_medallion.py --apply`, 9/9 notebooks green): org spine + 8 skills tables + rebranded `dim_hospital` + capacity + eventstream gold all present, verified 0 H_HSL / no real names via OneLake Delta read (see §7)*
* [x] `dim_hospital` replaced by `dim_tenant` / `dim_org_unit` / `dim_department`; all references re-pointed; facts re-keyed — *delivered via the **1:1 re-brand fold** (#330 gold, #332 semantic); the D2 `_hospital_to_org_crosswalk.csv` approach was superseded (tenant_id = hospital_id)*
* [x] Semantic model extended (skills measures); `verify-semantic-model.yml` re-baselined + green (#339/#341; verifier 35 rel / 69 measures / 8 roles)
* [x] Ontology + crosswalk + conformance gate extended and green (#344; conformance strict PASS, 0 WARN / 0 FAIL)
* [x] Fabric IQ `ont_hospital_capacity` + Data Agent grounding cover the org/skills domain — *repo grounding landed (#344, `fabric-data-agent/AGENT.md` 1.1.0); live Fabric IQ ontology regeneration is GA-gated per ADR-0014*
* [x] New ADR (unified org spine) Accepted; PRD FR/NFR rows + §7 matrix updated — *ADR-0039 **Accepted** 2026-07-24 (approved by @urruegg, "approved to proceed") + PRD `FR-ORG` / `FR-SKILL` / `NFR-SKILL` rows + §7 matrix (#320)*
* [ ] SIT + PROD deployed identically; live applies gated by `approved-to-apply`; PR merges human-performed — *live deploy **deferred** (Container Apps → Event Hub/Eventstream, not GitHub workflows); all PR merges to date human-performed*
* [x] All CI checks pass — *re-verified 2026-07-23: ontology conformance, master-data (13), skills-evidence (21), gold-build (28), gold-contract (5), semantic verifier, mojibake (1154 files), markdownlint*

---

## 6. Status log

### 2026-07-25 — Skills-events EventHub flip IMPLEMENTED for PROD swn (ADR-0043, deploy-class)

Execution slice for the un-parked flip (branch `sprint-23/eh-flip-execution`,
off `main`; stacked on the ADR-0043 governance PR). **Deploy-class — the live
PROD apply is gated by `approved-to-apply`.** Landed artefacts:

* **Dedicated per-domain skills Event Hub.** The `data-foundation/eventhubs`
  module now provisions a `skills-events` hub entity + `cg-skills-eventstream`
  consumer group (+ simulator `Data Sender` RBAC) inside the environment
  namespace whenever the skills lane runs in `sourceMode=EventHub`. `main.bicep`
  derives `enableSkillsEventHub` from the skills source mode and points the
  Eventstream at the dedicated hub (isolated from the capacity `events` rail).
* **`sourceMode=EventHub` for PROD swn** set in `prod-swn.bicepparam`
  (GA-in-region; auto-enables the dedicated hub). `az bicep build` + all three
  env `build-params` compile clean; `main.json` regenerated.
* **Post-deploy EventHub branch.** `configure-skills-eventstream.ps1` now wires
  an `AzureEventHub` source (via a `-ConnectionId` Fabric-managed connection),
  keeping the D4 three-kind guardrail + DefaultStream→Lakehouse topology; refuses
  a live EH wire without the connection id (StrictMode-safe). `-DryRun` verified.
* **Simulator.** `data-platform/scripts/skills-events/publish_skill_events.py`
  publishes synthetic `DC-SKILL-EVENT-v1` records (one AMQP message per record,
  routed by `eventKind`) to the dedicated hub via MI — mirrors the proven
  `eventhub_emitter.py` DI pattern; 5 new offline unit tests (28 skills-events
  tests + 5 gold-contract tests all green).
* **Data contract unchanged.** `DC-SKILL-EVENT-v1` is byte-identical; only the
  transport changed. `sourceMode` default stays `CustomEndpoint`, so SIT + all
  existing callers are unaffected (**backwards-compatible**).
* **Remaining live steps (post-`approved-to-apply`):** `what-if` against PROD
  swn, create the Fabric-managed connection (`POST /v1/connections`), apply,
  run the post-deploy EH branch, publish via the simulator, verify
  `bronze_skills_events` + the silver PHI gate.

### 2026-07-25 — EventHub-source flip un-parked for PROD Switzerland North (ADR-0043)

**Product-owner decision** by @urruegg: preview-tier services are approved in
**PROD Switzerland North** to demonstrate the art of the possible under
synthetic/no-PHI scope; the **GA-only gate is reserved for a real go-live
(real-PHI) cut-over**. This un-parks the skills-events `sourceMode=EventHub`
flip — recorded in
[ADR-0043](../adr/0043-preview-tier-permitted-in-prod-swn-for-demo.md)
(refines ADR-0006 + ADR-0042). Read-only verification confirmed the flip is in
fact **GA in Switzerland North**: Eventstream is GA in swn
(region-availability.yaml), Azure Event Hubs is GA there, PROD Fabric
`fabricihzhhpfprod` runs in swn, and the PROD EH namespace
`evh-ihzhhpf-prod-i62t` exists in-region — so the flip does not even consume the
preview exception. Confirmed design points: a **dedicated skills-events Event
Hub** (per-functional-domain envelope, not shared with the capacity `events`
rail); a **simulator** feeds it until the live publisher is ready; **SIT and
PROD do not share input services** (`evh-ihzhhpf-sit-y26y` westus2 vs
`evh-ihzhhpf-prod-i62t` swn). Remaining prerequisite for the live flip: the
out-of-band Fabric-managed connection (`POST /v1/connections`). Execution
(dedicated EH + managed connection + `sourceMode=EventHub` + simulator) is a
separate deploy-class slice gated by `approved-to-apply`.

### 2026-07-25 — Skills-events Eventstream lane LIVE-WIRED in SIT (WS-A4 / FR-SKILL-005)

**Approved-to-apply** by @urruegg (PR #374 approved + merged first). This slice
(branch `sprint-23/skills-events-live-wire`, off `main`) authors the **missing
post-deploy script** and live-wires the lane the #374 data lane feeds:

* **Transport decision — `CustomEndpoint` (demo-scope, ADR-0013).** The working
  `es-capacity-events-sit` lane uses a CustomEndpoint source, and it is fully
  live-deployable today (no out-of-band Fabric-managed connection). The Container
  Apps publisher (`NFR-SKILL-001`) POSTs `DC-SKILL-EVENT-v1` envelopes to the
  Eventstream ingestion endpoint. **EventHub source stays the Swiss-GA
  target-state** (needs `POST /v1/connections`). *(Superseded 2026-07-25: the
  EventHub flip is un-parked for PROD swn per ADR-0043 — see the top status-log
  entry.)* The Bicep module gained a
  backwards-compatible `sourceMode` param (`CustomEndpoint` default | `EventHub`).
* **New post-deploy script** —
  `infra/modules/integration-orchestration/skills-eventstream/post-deploy/configure-skills-eventstream.ps1`
  (the module previously referenced a non-existent path). Asserts the exactly-three
  D4 event-kind guardrail, `-DryRun` prints the topology, idempotent (skips on
  existing display name), async-safe (Fabric returns 202; id resolved by
  display-name lookup with retry). Mirrors the authoritative live schema
  (streams + `compatibilityLevel: 1.1` + 3 parts).
* **Live apply (SIT workspace `f3af9733-…`)** — created Eventstream
  **`es-ihzhhpf-skills-events`** (id `2f5826c5-f7c4-4b87-8bcf-ee727e1e4704`):
  CustomEndpoint source → DefaultStream → Lakehouse destination
  `bronze_skills_events` in `lh_ihzhhpf_sit` (`30594c20-…`). All three nodes
  verified **`status: Running`**. Re-run confirmed idempotent (clean skip).
* **No secrets committed** — the CustomEndpoint ingestion connection string
  (SharedAccessKey) is retrieved at publish-time via
  `GET …/eventstreams/{id}/sources/{sourceId}/connection` and stored in Key Vault;
  never in the repo.
* **PHI gate unchanged** — the Eventstream lands raw synthetic envelopes; the
  PHI/consent gate + kind allow-list stay in the silver notebook (deny-by-default).
* **Remaining** — wire the Container Apps publisher image to the ingestion endpoint;
  surface a live-vs-simulated event measure on the semantic model (documented
  follow-up); EventHub-source flip at Swiss GA. *(Update 2026-07-25: EventHub
  flip un-parked for PROD swn per ADR-0043 — GA-in-swn, needs the managed
  connection; see top status-log entry.)*

### 2026-07-25 — Skills-events near-real-time lane (WS-A4 / FR-SKILL-005) data lane landed

The WS-A4 Eventstream **infra** module (`es-ihzhhpf-skills-events`) already existed,
but the **data lane it feeds was empty**. This slice builds it in-repo (branch
`sprint-23/skills-events-lane`, off `main`):

* **New additive contract `DC-SKILL-EVENT-v1`** —
  `data/synthetic/schema/dc-skill-event-v1.schema.json`. Standalone; **does not
  modify** the batch `DC-SKILL-EVIDENCE-v1` contract (backwards-compatible). Carries
  the three narrow event kinds routed by `eventKind`: `credential-expiry`,
  `consent-grant-or-revoke`, `newly-confirmed-assertion`.
* **Dependency-free seeder** — `data-platform/scripts/skills-events/`
  (`normalize.py` + `skill_events_synth.py` + fixtures). The payload a Container
  Apps service publishes to the Eventstream (per `NFR-SKILL-001`, never a workflow).
* **Bronze → Silver → Gold notebooks** —
  `data-platform/notebooks/skills-events/`. Silver is the downstream **PHI/consent
  gate** the Eventstream module defers to: deny-by-default quarantine, and the
  consent-revocation invariant that **clears the GLN promotion** on `revoke`
  (`FR-SKILL-003`). Gold is a **separate `skillevt_*` star spine** (fact + source/kind
  dims) carrying the live-vs-simulated badge (`FR-SKILL-007`), mirroring the
  `external-signals` `ext_*` spine.
* **Contract-safe** — the `skillevt_*` tables are **not** Direct-Lake tables in the
  semantic model, so they are outside the derived gold contract
  (`verify_gold_schema.contract_tables`); the gold-parity gate stays green (21
  contract tables covered). Semantic-model surfacing (a live-vs-simulated event
  measure) is a documented follow-up.
* **Tests** — 23 Spark-free unit tests (9 seeder schema/consent + 14 medallion gate /
  badge). Neighbouring suites regression-clean (skills-evidence 21+43, gold-contract 5).
* **Remaining for this DoD item** — live Eventstream wiring: **DONE 2026-07-25**
  (see the LIVE-WIRED entry above; CustomEndpoint source, `es-ihzhhpf-skills-events`
  Running in SIT). Container Apps publisher image + EventHub-source flip still open.


### 2026-07-24 — PROD org/skills parity APPLIED (infra + medallion + gold evidence)

**Approved-to-apply** by @urruegg for the full PROD replay sequence. PR #368
(param flags + what-if) merged to `main` first (human-merged, `status:approved`).

* **PROD infra applied** — `az deployment group create -g rg-ihzhhpf-prod -f infra/main.bicep -p prod-swn.bicepparam` **Succeeded**. Verified live: `stmasterdataihzhhpfprod` (+ `landing` container), `cae-skills-sim-ihzhhpf-prod`, `id-skills-sim-ihzhhpf-prod` UAMI, jobs `caj-sk-{sf,wid,skm,lms}-ihzhhpf-prod` — all `Succeeded`. Matches the 10 additive Creates from the what-if; 0 deletes.
* **PROD medallion replayed** — uploaded the 5 current source sets to PROD OneLake `Files/` (capacity master-data, curavias org/skills, skills-evidence modules, eventstream seed, or-samples), then `run_medallion.py --environment PROD --apply` → **9/9 notebooks green, "Medallion rebuild complete"**. `05_gold_org_skills` was net-new to PROD (`[create]`). The 07-23 greenfield rebuild predated the H_HSL-prune fix, so re-uploading the current seed/master-data was required.
* **PROD gold parity proven** — `list_gold_tables.py --environment PROD` = **28 gold tables** (all org/skills + `dim_care_setting`); `verify_gold_schema.py` = **OK, 21 contract tables covered**.
* **Authoritative OneLake Delta evidence (SQL endpoint lags, not used)** — new reusable reader [`data-platform/scripts/fabric/read_gold_evidence.py`](../../data-platform/scripts/fabric/read_gold_evidence.py):
  * `dim_hospital` = **3 Curavias tenants only** — `H_USZ`→Uniklinik CuraNova, `H_LUKS`→Kantonsspital Curalp, `H_SZB`→Spital Vialta. Cities/cantons also fictionalised (Curalp-Stadt/CA, Vialtaberg/HN, Stadt Helvetia-Nord/HN) — **no real hospital names**.
  * **0 H_HSL orphans** across hospital-keyed gold: `dim_specialty` 81, `dim_hospital_service` 22, `fact_capacity_baseline` 17; re-keyed facts (`bed_assignment`, `or_case`, `or_schedule`, `encounter`) carry no `hospital_id` (keyed to tenant/org). Mirrors the SIT §7 result below.
* **Remaining (carried to next session):**
  1. **PROD semantic-model + report publish** — `deploy_fabric_cicd.py --environment PROD --mode publish`. **Validate OK** (PROD workspace/lakehouse/params resolve). **Blocked locally**: `fabric-cicd` requires Python `>=3.9,<3.14`; this host's default is 3.14. Python 3.11 is present (`C:\Python311`) — finish the isolated `--user` install with a clean `PYTHONPATH`/`PYTHONHOME`, or run the publish from CI/another host. Then confirm the PROD SQL analytics endpoint has caught up (async).
  2. **E2E SIT + PROD parity test** — sign-in → app → agent → data → response on both; capture a parity evidence doc; then tick the §5 DoD "SIT + PROD deployed identically" and the design-spec §5 DoD, and bump this doc.

### 2026-07-24 — PROD org/skills parity prep (T11/T13 flags + `what-if` clean)

* **Goal:** close the last open DoD item — "SIT + PROD deployed identically" — for the Sprint 23 org/skills landing surface. **PROD platform/infra is owned by Sprint 19** (switzerlandnorth greenfield rebuild, ADR-0037, 2026-07-23); that rebuild predates this sprint's org/skills spine, so PROD still runs the pre-org/skills gold. This delta is Sprint 23's to close.
* **Change (non-destructive prep):** enabled the three Sprint 23 module flags in [`infra/environments/prod-swn.bicepparam`](../../infra/environments/prod-swn.bicepparam) to mirror `sit.bicepparam` — `enableMasterdataLandingModule`, `enableSkillsSimJobsModule`, `enableSkillsEventstreamModule` = `true`, plus `simCapacityLocation = 'switzerlandnorth'` (single-region PROD; SIT uses westus2). Fabric destination IDs stay empty (scaffold, mirrors SIT); the sim-jobs image is the same public placeholder as SIT (no PROD ACR dependency).
* **Evidence:** `az bicep build` clean (pre-existing warnings only); `az deployment group what-if -g rg-ihzhhpf-prod -f infra/main.bicep -p prod-swn.bicepparam` **Succeeded** — **0 deletes**, 10 additive Creates that map exactly to the enabled modules:
  * `stmasterdataihzhhpfprod` + `blobServices/default` + `containers/landing` (T11 landing zone)
  * `cae-skills-sim-ihzhhpf-prod` + jobs `caj-sk-{lms,sf,skm,wid}-ihzhhpf-prod` + `id-skills-sim-ihzhhpf-prod` UAMI + role assignment (T13 sim-jobs)
  * skills-eventstream is scaffold-only (REST post-deploy; no ARM resource — consistent with the empty Fabric IDs)
  * The other 31 `Modify` entries are pre-existing PROD drift (agent-host, cosmos, network, KV PE) unrelated to this change; the 2 `Unsupported` are what-if lambda-expression limitations on computed role-assignment names.
* **SIT baseline confirmed deployed** (`rg-ihzhhpf-sit`): `stmasterdataihzhhpfsit`, `cae-skills-sim-ihzhhpf-sit`, `id-skills-sim-ihzhhpf-sit` present.
* **Gate:** PROD apply is **`approved-to-apply`-gated** (AGENTS.md §4). Next steps after apply: replay the org/skills medallion to PROD (prune H_HSL, verify 0 real names via OneLake Delta), publish rebaselined semantic model + report, then e2e-test SIT + PROD.

### 2026-07-24 — ADR-0039 accepted (approved to proceed)

* **ADR-0039 moved Proposed → Accepted** — `docs/adr/0039-curavias-landing-zone-and-skills-evidence-plugins.md`, approved by @urruegg ("approved to proceed"). Closes the last governance DoD gate; the only remaining open DoD item is the live PROD deploy (Container Apps → Event Hub/Eventstream, `approved-to-apply` gated).

### 2026-07-24 — Live SIT medallion proven clean + H_HSL orphan fixed (break checkpoint)

**Done this session.**

* **H_HSL orphan fix merged** — [PR #350](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/350) (closes [#349](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/349)). The Curavias 1:1 fold drops `H_HSL` (Hirslanden, no tenant) from `dim_hospital`; the fix prunes its rows from the five hospital-keyed capacity gold tables (`build_gold_org_spine.prune_orphan_hospital_rows`, wired into `run()`) and drops `H_HSL` from the eventstream seed (`gen_eventstream_seed.py`, regenerated corpus). 7 new Spark-free unit tests; 116 tests + mojibake + markdownlint green.
* **Live SIT medallion rebuilt** — full `run_medallion.py --environment SIT --apply` (`approved-to-apply` by @urruegg), 9/9 notebooks green. Uploaded the regenerated eventstream seed + updated skills-evidence modules to OneLake `Files/` first.
* **Evidence (authoritative OneLake Delta read, SQL endpoint lags and is not used):** `dim_hospital` = 3 Curavias rows (`H_USZ`→CuraNova, `H_LUKS`→Curalp, `H_SZB`→Vialta), no real names. H_HSL orphans eliminated everywhere:

  | gold table | before | after |
  | --- | --- | --- |
  | dim_specialty | 108 (27 H_HSL) | 81 (0) |
  | dim_hospital_service | 41 (19) | 22 (0) |
  | dim_ward_capacityunit | 19 (4) | 15 (0) |
  | fact_capacity_baseline | 20 (3) | 17 (0) |
  | map_disease_treatment_specialty_service | 60 (15) | 45 (0) |
  | encounter | 309 (83) | 309 (0) |
  | bed_assignment | 173 (41) | 173 (0) |

  Plus the org spine + 8 skills gold tables (`dim_org_unit`, `dim_department`, `dim_capacity_unit`, `dim_care_setting`, `dim_skill`, `dim_occupation_role`, `bridge_role_skill_demand_template`, `fact_skill_demand`, `fact_skill_gap`, `fact_skill_assertion`, `bridge_worker_unit_eligibility`).

**Next steps (starting point after the break).**

1. **ADR-0039 acceptance** — **Done** (2026-07-24): moved Proposed → Accepted, approved by @urruegg. Governance DoD gate closed.
2. **PROD deploy** — replay the same medallion against PROD once SIT is signed off (Container Apps → Event Hub/Eventstream for ingestion, not GitHub workflows; `approved-to-apply` gated).
3. **SQL analytics endpoint** — confirm the SIT SQL endpoint has caught up with the new Delta tables (it lags async), so Direct-Lake / report consumers see the rebranded, orphan-free gold.
4. **Downstream re-baseline check** — re-validate the semantic-model measures + report visuals against the freshly-landed org/skills gold (row counts shifted after the prune).
5. **T11–T14 refactor lane** — dedicated landing zone (T11), skills-evidence plugins (T12), hybrid transport (T13), bed-vs-ops split (T14) remain open per §3.

---

## 7. References

* Design: [`2026-07-19-curavias-shared-master-data-and-ontology-design.md`](../superpowers/specs/2026-07-19-curavias-shared-master-data-and-ontology-design.md)
* Idea package: [`unified-curavias-organisation-and-skills-ontology/`](../superpowers/ideas/unified-curavias-organisation-and-skills-ontology/)
* Prerequisite sprint: [Sprint 22 — Golden-source + reproducible medallion (P1a)](sprint-22-curavias-golden-source-reproducible-medallion.md)
* Ontology: [`docs/ontology/`](../ontology/)
* Issue: [#255 — Sprint 23: Unified Curavias organisation spine + org/skills ontology (P1b)](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255)
* Depends on: [#254 — Sprint 22 (P1a)](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/254)
