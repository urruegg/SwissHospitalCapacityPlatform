# Sprint 19 Extension — SIT↔PROD End-to-End Parity, Evidence & Curavias Product Documentation Refresh

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Every destructive step is hard-gated by `approved-to-apply` per [AGENTS.md §4](../../../AGENTS.md).

| Field | Value |
|-------|-------|
| **Version** | 1.0.1 |
| **Date** | 2026-07-24 |
| **Author** | @urruegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (ADR-0039→0040 Task A3 retarget) |

**Goal:** Close every remaining SIT↔PROD gap so the two environments are provably at parity end-to-end, produce evidence at all levels (IaC, network, data, AI/agents, app, DNS/TLS, governance), and refresh the Curavias product documentation to reflect the live PROD-deployed (Switzerland North) status with a full requirements-traceability view (covered / open / not-relevant-per-ADR).

**Architecture:** PROD was rebuilt greenfield in `switzerlandnorth` ([ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md)); SIT stays split `westus2`/`eastus2` ([ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md)). Both run synthetic data only, no PHI ([ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md)). This extension does **not** rebuild anything — it (a) reconciles governance to the three confirmed facts, (b) executes the one open infrastructure parity item (network hardening, [ADR-0039](../../adr/0039-prod-network-parity-vnet-private-endpoints.md)), (c) brings out-of-band resources under IaC, (d) captures an evidence-backed parity matrix on all levels, and (e) rewrites the product docs + traceability from the deployed reality.

**Tech Stack:** Bicep (`az bicep build` / `what-if`), `az` CLI, Fabric REST, `gh` CLI, GitHub Actions (`cd-infra-deploy-*`, `ci-infra-validate`), Markdown docs governed by §9 versioning + `document-authoring` skill.

---

## 0. Confirmed facts driving this extension

The user confirmed three facts. Each already has an ADR; this extension makes governance and docs consistent with them.

| # | Confirmed fact | Governing ADR(s) | Reconciliation action |
|---|----------------|------------------|-----------------------|
| F1 | **PROD = Switzerland (Switzerland North) DC region.** | [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md) *(Accepted)* — scoped-supersedes ADR-0032/0035 for PROD. | Retire stale `eastus2` framing in the Sprint 19 charter, issue #239 title/labels, and #275. See Task A2. |
| F2 | **No customer/patient PID/PHI — the platform is metadata/episode-driven** (Hospitalisation Episode as the control unit, pseudonymised reference dims only). | [ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md) *(Proposed)* + [ADR-0006](../../adr/0006-preview-features-non-production-rule.md) | Promote ADR-0016 to **Accepted** and make the "metadata-driven, episode-not-patient" framing explicit. See Task A1. |
| F3 | **SIT = US region is acceptable** because it uses synthetic data only, no real data. | [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md) *(Proposed)* | Promote ADR-0013 to **Accepted**; confirm the `policy/exceptions.json` `MC-RESIDENCY` window still covers SIT. See Task A1. |
| F4 | **SIT (US) permits cross-region access** — because it holds synthetic data only, the SIT split across `westus2`/`eastus2` (cross-region Foundry↔Fabric hops, `GlobalStandard` cross-geo inference) is explicitly allowed. This is the deliberate SIT↔PROD asymmetry: PROD is single-region Swiss with no cross-region hop; SIT tolerates cross-region for capability coverage. | [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md) *(Proposed)* + [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md) | Record F4 explicitly in ADR-0013 (§Decision) and in the parity matrix as an **intentional, ADR-backed asymmetry** (not a gap). See Task A1 / Phase F. |

---

## 1. Current state (verified 2026-07-24)

**PROD Switzerland North rebuild is complete** — [`prod-evidence-switzerlandnorth.md`](../../sprints/sprint-19/prod-evidence-switzerlandnorth.md) v1.1.0 records all 11 Definition-of-Done criteria green (RG `rg-ihzhhpf-prod`, 3 models + 8 agents, agent-host `/agents`→7, `app.curavias.ch` HTTP 200 + TLS, Fabric F2 + workspace + 50 Delta tables, live Foundry inference `PROD-SWN-OK`, SIT untouched). CD variables repointed to swn (#311 closed).

**What is NOT yet at parity / still open:**

| Area | SIT state | PROD state | Gap | Tracker |
|------|-----------|-----------|-----|---------|
| Network | Full stack: `vnet-platform-ihzhhpf-sit`, Cosmos PE, VNet-integrated agent-host CAE | Public / network-off baseline (`enableNetworkModule=false`); KV + Cosmos policy-locked & unreachable | **Primary parity gap** — needs VNet + Cosmos PE + **KV PE**; destructive CAE recreate | [ADR-0039](../../adr/0039-prod-network-parity-vnet-private-endpoints.md) *(Proposed)*, #311 follow-up |
| IaC coverage | CSA Cosmos + ACR provisioned **out-of-band** (not in `infra/main.bicep`), not drift-checked | Same out-of-band pattern (hand-made `crihzhhpfprod`) | SIT/PROD can silently drift; CI parity gate blind to these | #252 (OPEN) |
| Fabric IQ | Ontology `ont_hospital_capacity` + Data Agent live (consumed by Foundry `ooa`) | Semantic model at parity & queryable; **Ontology blocked** `403 FeatureNotAvailable` (Preview, per-capacity) | Ontology/Data-Agent not at parity | #270 (OPEN) |
| Curavias web | (marketing site scope) | SWA not provisioned; issue references **deleted** `prod-eastus2.bicepparam` | Stale + not deployed | #275 (OPEN, stale) |
| Signal runner | `ca-signal-runner` identity work in progress | `ca-signal-runner-ihzhhpf-prod` exists (per ADR-0039) | Identity hardening in flight on current branch `sprint-19/harden-signal-runner-identity` | #290 area |
| App | — | — | `nginx` SPA history-fallback 404 on deep-links | #299 (OPEN) |

**Governance debt found while surveying:**

- ADR-0013 and ADR-0016 are still `Status: Proposed` despite being foundational and long-acted-upon.
- **Duplicate ADR numbers on disk:** two `0039-*.md` (`prod-network-parity…` and `curavias-landing-zone-and-skills-evidence-plugins`) and two `0021-*.md` (`readiness-scoring-rules` and `whiteboard-base-react-flow…`). Numbering collision breaks the "one ADR = one number" contract.
- Sprint 19 charter file is named `sprint-19-prod-eastus2-full-deployment.md` and still says `Status: Pending (blocked on Sprint 18)` / eastus2 — contradicts the shipped Switzerland North reality.

---

## 2. Decisions Register (decisions to take)

Each decision below is required for "end-to-end parity". Recommendation is given; **D1 and D4 are destructive/deploy and require an explicit `approved-to-apply` from the OWNER before any apply** per AGENTS.md §4. Confirm D1, D3, D5 before execution.

| # | Decision | Options | Recommendation | Gate |
|---|----------|---------|----------------|------|
| **D1** ✅ **CONFIRMED (a)** 2026-07-24 | Execute the ADR-0039 **network parity** (VNet + Cosmos PE + KV PE) incl. the one-time destructive `cae-ihzhhpf-prod` + `ca-agent-host` + `ca-signal-runner` recreate (~5–10 min agent-host outage; `app.curavias.ch` unaffected)? | (a) Execute now, this sprint *(recommended)* · (b) Land Bicep+ADR only, defer destructive apply · (c) Accept public PROD as "parity-waived per no-PHI" | **(a) — CONFIRMED by @urruegg 2026-07-24**: execute now, gated by `approved-to-apply`. Promote ADR-0039 to **Accepted** on apply. | `approved-to-apply` |
| **D2** | Close **IaC parity** (#252): bring CSA Cosmos + ACR into `infra/main.bicep`, gated, for **both** SIT and PROD, so they're `what-if`/drift-checked. | (a) Wire both into main.bicep + add PROD params *(recommended)* · (b) Keep out-of-band, document only | **(a)** — otherwise the SIT/PROD parity CI gate stays blind to two production-tier resources. | `approved-to-apply` for the re-deploy |
| **D3** ✅ **REVISED 2026-07-24** | **Fabric IQ Ontology** PROD parity (#270): PROD `Ontology` item was `403 FeatureNotAvailable` (Preview, per-capacity). | (a) ~~Declare N/A for parity~~ · (b) **Attempt in PROD under the new standing Preview exception (ADR-0042)** *(chosen)* | **(b) — per @urruegg 2026-07-24 + ADR-0042**: PROD Switzerland North = GA-target with a standing Preview exception to demo the full Curavias stack in-region. **Attempt** ontology + data-agent on the swn capacity; if the per-capacity `FeatureNotAvailable` gate still blocks it, record as **availability-blocked (Microsoft-side), not policy-excluded** — track under #270. | Doc + deploy |
| **D8** ✅ **CONFIRMED 2026-07-24** | **Full data-lane parity** — flip the PROD-swn data/AI/integration lane ON (`enableDataPlatformModule`, `enableFabricFoundationModule`, `enableAiPlatformModule`, `enableAiMlFoundationModule`, `enableIntegrationOrchestrationModule`, `enableFoundryHostedAgents`, `enableSimCapacityModule`, `enableFabricEventstreamModule`, `enableSkillsEventstreamModule`, `enableMasterdataLandingModule`, `enableSkillsSimJobsModule`) to match SIT — essentially executing rebuild phases **P5 (Foundry agents) + P6 (Fabric workspace/lakehouse/semantic-model/eventstreams)** in switzerlandnorth. | (a) Document-and-defer · (b) Storage/ADLS tier only · (c) **Go for full parity** *(chosen)* | **(c) — CONFIRMED by @urruegg 2026-07-24**: execute the full P5/P6 data lane as a sequence of gated deploy slices. Blocker review (below) confirms every required BOM item is GA in swn except the two Preview IQ items (covered by ADR-0042). | `approved-to-apply` per slice |
| **D4** | Promote **ADR-0013 + ADR-0016** Proposed→**Accepted**; make F2/F3 framing explicit. | (a) Promote both now *(recommended)* · (b) Leave Proposed | **(a)** — both are acted-upon and foundational; leaving them Proposed is stale governance. | CODEOWNERS review |
| **D5** | Fix the **duplicate ADR-0039 / ADR-0021** numbering collision. | (a) Renumber the newer non-network 0039 (`curavias-landing-zone…`) and one 0021 to the next free numbers, add ADR redirect stubs + fix inbound links *(recommended, MAJOR bump on moved ADRs)* · (b) Leave as-is | **(a)** — one-number-per-ADR is a hard contract; collision will bite link-check + traceability. Needs an ADR to record the renumber. | CODEOWNERS review |
| **D6** | **Curavias web PROD** (#275): rescope from deleted `prod-eastus2.bicepparam` to `prod-swn.bicepparam` and deploy, or defer. | (a) Rescope + deploy the SWA to swn this sprint · (b) Defer to Sprint 20/24 UX track *(recommended)* | **(b)** — it's a marketing-site item on the Sprint 24 track; rescope the issue but keep it out of the parity-critical path. | Doc decision |
| **D7** | **Model residency posture** — agents run `gpt-5/-mini/o3` as `GlobalStandard` (cross-geo) in swn. | (a) Keep GlobalStandard, record deferral *(recommended, no-PHI)* · (b) Downgrade to regional `Standard` (`gpt-4.1`/`gpt-4o`) | **(a)** — not binding under F2 (no PHI); record as a PHI-onboarding revisit per ADR-0037. | Doc decision |

### 2.1 Switzerland North availability-blocker review (pre-sprint parity check, re-confirmed 2026-07-24)

Source: [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md) evidence matrix (live `az` 2026-07-21) + [`docs/region-availability.yaml`](../../region-availability.yaml). **Verdict: no hard blockers to full parity.** Every BOM item the P5/P6 data lane needs is **GA** in Switzerland North; only two IQ items are Preview (covered by [ADR-0042](../../adr/0042-prod-switzerland-north-ga-target-standing-preview-exception.md)).

| Capability | swn maturity | Parity impact |
|------------|--------------|---------------|
| Fabric F2 capacity (`fabricihzhhpfprod` already provisioned) | GA (quota 0/512) | ✅ deployable |
| Fabric workspace / OneLake / lakehouse / eventstream / eventhouse / semantic-model / Power BI | GA | ✅ deployable |
| Azure OpenAI (gpt-5/-mini/o3, gpt-4.1/4o) | GA | ✅ deployable (agents via `GlobalStandard`, D7) |
| Foundry Agent Service (Responses + Agents; `ai-ihzhhpf-prod` already provisioned) | GA | ✅ deployable (no Class-A private-IP — not needed, F2) |
| Container Apps / Logic Apps / FHIR / Cosmos / Event Hubs / Service Bus / Storage / Key Vault / Purview / Log Analytics | GA | ✅ deployable |
| **Fabric IQ Ontology** | **Preview** (#270 per-capacity `FeatureNotAvailable`) | ⚠️ attempt under ADR-0042; if blocked → availability-blocked (Microsoft-side), not a parity defect |
| **Fabric Data Agent** | **Preview** | ⚠️ attempt under ADR-0042 |

Non-availability caveats (not blockers, not binding under synthetic/no-PHI F2/F3): Foundry "Class-A" private-IP agent topology absent in swn; agent-model in-region residency only via regional `Standard` (gpt-4.1/4o) — deferred to PHI onboarding per D7/ADR-0037.

---

## 3. File / artefact map

**Governance (docs lane):**
- Modify: `docs/adr/0013-temporary-us-region-demo-scope.md` (Proposed→Accepted, F3 framing)
- Modify: `docs/adr/0016-no-phi-in-mvp-demo-scope.md` (Proposed→Accepted, "metadata/episode-driven" framing)
- Modify: `docs/adr/0039-prod-network-parity-vnet-private-endpoints.md` (Proposed→Accepted after D1)
- Create: `docs/adr/0040-adr-number-collision-renumber.md` (records D5) *(number = next free after resolving the collision)*
- Rename/supersede: `docs/sprints/sprint-19-prod-eastus2-full-deployment.md` → Switzerland North charter (or add a superseding header pointing at the swn evidence)
- Create: `docs/sprints/sprint-19/sit-prod-parity-matrix.md` (the evidence deliverable)
- Modify: `docs/PRD.md` §Traceability Matrix (add this extension's coverage rows + status)
- Modify: `docs/COMPLIANCE.md`, `docs/SECURITY.md` (reflect Accepted ADR-0013/0016, network parity)

**Product docs refresh (docs lane):**
- Modify: `docs/ARCHITECTURE.md`, `docs/INFRASTRUCTURE.md`, `docs/INTEGRATION.md`, `docs/OPERATIONS.md`, `docs/DATA.md`, `docs/AI.md` — reflect the live swn PROD topology + SIT split.
- Create: `docs/CURAVIAS-PRODUCT-STATUS.md` — single "as-deployed PROD status + requirements coverage (covered/open/N-A-per-ADR)" view.

**Infra lane (IaC parity + network):**
- Modify: `infra/main.bicep` (wire CSA Cosmos + ACR modules, gated) — D2
- Modify: `infra/modules/platform-foundation/main.bicep` (KV PE — already drafted per ADR-0039)
- Modify: `infra/environments/prod-swn.bicepparam` (`enableNetworkModule=true`, `enableKeyVaultPrivateEndpoint=true`, `10.70.0.0/16`) — D1
- Modify: `infra/environments/sit.bicepparam` (optional KV-PE parity follow-up)
- Modify: `.github/workflows/ci-infra-validate.yml` (parity job already repointed to `rg-ihzhhpf-prod`; extend to cover the newly-wired resources)

**Issue hygiene (control lane):**
- Update titles/labels/scope on #239, #252, #270, #275; close superseded items.

---

## 4. Phased tasks

### Phase A — Governance reconciliation to confirmed facts (no cloud side effects)

#### Task A1: Promote foundational ADRs to Accepted (D4)

**Files:** Modify `docs/adr/0013-temporary-us-region-demo-scope.md`, `docs/adr/0016-no-phi-in-mvp-demo-scope.md`

- [ ] **Step 1:** In `0016`, change `Status: Proposed` → `Status: Accepted`; add a sentence to §Decision-1 making the confirmed framing explicit: "The control unit is the Hospitalisation Episode, not the patient; the platform is metadata/episode-driven and holds no direct or indirect patient identifiers (F2)." Bump doc header MINOR.
- [ ] **Step 2:** In `0013`, change `Status: Proposed` → `Status: Accepted`; add a note under §Decision confirming F3 (SIT US-region acceptable under synthetic-only). Bump doc header MINOR.
- [ ] **Step 3:** Verify `policy/exceptions.json` still holds a non-expired `MC-RESIDENCY` exception covering SIT; if expired, open a renewal note (do not silently extend).

Run: `npx --yes markdownlint-cli2 "docs/adr/0013-*.md" "docs/adr/0016-*.md"`
Expected: PASS

- [ ] **Step 4: Commit** `docs: promote ADR-0013/0016 to Accepted; make no-PHI/metadata-driven + SIT-US framing explicit (F2,F3)`

#### Task A2: Retire stale eastus2 framing (F1)

**Files:** Modify `docs/sprints/sprint-19-prod-eastus2-full-deployment.md`; update issues #239, #275

- [ ] **Step 1:** Add a superseding banner + `Status: Superseded by Switzerland North rebuild` header to the eastus2 charter, linking [`prod-evidence-switzerlandnorth.md`](../../sprints/sprint-19/prod-evidence-switzerlandnorth.md) and ADR-0037. Bump header MAJOR (region contract reversed) and add the rationale (points at ADR-0037 as the backing ADR). Keep the file for history.
- [ ] **Step 2:** `gh issue edit 239 --title "Sprint 19: Full PROD Deployment in Switzerland North (greenfield rebuild)"`; add a comment noting the eastus2→swn pivot (ADR-0037) and that DoD is met per the evidence doc. Update the `sprint-19` label description if needed.
- [ ] **Step 3:** `gh issue comment 275` noting the referenced `prod-eastus2.bicepparam` is deleted; rescope per D6.
- [ ] **Step 4: Commit** `docs: mark Sprint 19 eastus2 charter superseded by Switzerland North rebuild (ADR-0037)`

#### Task A3: Resolve the ADR-0039 number collision (D5, narrowed)

**Scope note (2026-07-24):** Two `0039-*.md` exist (`prod-network-parity…` dated 2026-07-22, promoted to Accepted this sprint in Phase B; and `curavias-landing-zone-and-skills-evidence-plugins` dated 2026-07-23). Resolve **only** the 0039 collision now — the **network-parity ADR keeps 0039**; the later curavias ADR is renumbered. The separate **0021 collision** (`readiness-scoring-rules` vs `whiteboard-base…`, both Sprint 13/14, unrelated to parity, with ambiguous prose references) is **recorded as a follow-up** in the new collision-resolution ADR for a dedicated hygiene PR — not churned here.

**Files:** Curavias ADR now lives at `docs/adr/0040-curavias-landing-zone-and-skills-evidence-plugins.md`; redirect stub remains at the old 0039 Curavias ADR path; create `docs/adr/0041-adr-number-collision-resolution.md`; fix inbound links.

- [ ] **Step 1:** `git mv` the curavias ADR to `0040-*`; update its H1 `# ADR-0039:` → `# ADR-0040:`; add a note "Renumbered from ADR-0039 → ADR-0040 on 2026-07-24 (collision resolution, see ADR-0041)."
- [ ] **Step 2:** Leave a one-line redirect stub at the old Curavias ADR path pointing to the new `0040-*` file.
- [ ] **Step 3:** repoint every **filename-based** Curavias ADR link (PRD traceability row, sprint-23 doc, this extension plan) to `0040-*`. For prose `ADR-0039` mentions, only repoint those that clearly refer to the **curavias landing zone** topic; leave network-parity `ADR-0039` mentions. Report any ambiguous reference instead of guessing.
- [ ] **Step 4:** Create `docs/adr/0041-adr-number-collision-resolution.md` (Status Accepted) recording: the 0039 resolution (curavias→0040, network keeps 0039); AND the **still-open 0021 collision** (readiness-scoring vs whiteboard) flagged for a dedicated follow-up hygiene PR. This ADR is the §9 backing for the identifier change.
- [ ] **Step 5:** Run `npx --yes markdown-link-check docs/adr/*.md docs/PRD.md docs/sprints/sprint-23-curavias-org-spine-and-skills-ontology.md`
Expected: PASS (no dead links). Bump PRD header PATCH for the link retarget; update Previous Version.
- [ ] **Step 6: Commit** `docs(adr): resolve ADR-0039 collision (curavias→0040); record 0021 collision follow-up (ADR-0041)`

### Phase B — Network parity (ADR-0039) — D1

> **STATUS 2026-07-24: ALREADY APPLIED IN CLOUD.** Live `az` verification shows PROD network parity is fully deployed and committed (`8213dd7`, `cb6b56c`): `vnet-platform-ihzhhpf-prod` (`10.70.0.0/16`), Cosmos CSA+platform PEs `Approved`, KV PE `Approved`, KV `publicNetworkAccess=Disabled`, and `cae-ihzhhpf-prod` VNet-integrated on `snet-cae` (`Succeeded`). The one-time destructive CAE recreate already occurred. **No `approved-to-apply` gate remains** — Phase B reduces to governance catch-up + evidence capture (B3 below).

#### Task B3: Promote ADR-0039 + capture applied evidence (governance catch-up)

- [ ] Promote `docs/adr/0039-prod-network-parity-vnet-private-endpoints.md` `Status: Proposed`→`Accepted` (Date 2026-07-24), with a note that the parity was applied and verified live on 2026-07-24 (VNet + 3 PEs Approved + VNet-integrated CAE + KV Disabled).
- [ ] Create `docs/sprints/sprint-19/evidence/2026-07-24-network-parity-verification.md` capturing the live `az` outputs.
- [ ] Fix the stale `ADR-0038` references in `infra/main.bicep` + `infra/environments/prod-swn.bicepparam` comments (they should cite **ADR-0039** for network parity; ADR-0038 is trunk-based-workflow).
- [ ] Commit `docs(adr): promote ADR-0039 to Accepted (PROD network parity applied + verified live)`.

<!-- Original gated plan retained below for the audit trail; superseded by B3 status above. -->

#### (Superseded) Task B1: Land the network-parity Bicep + params (non-destructive)

**Files:** Modify `infra/main.bicep`, `infra/modules/platform-foundation/main.bicep`, `infra/environments/prod-swn.bicepparam`

- [ ] **Step 1:** Confirm the ADR-0039 Bicep (KV PE params + `enableKeyVaultPrivateEndpoint`, `networkCaeSubnetPrefix`) is present; if not, add per ADR-0039 §Implementation notes.
- [ ] **Step 2:** Set `prod-swn.bicepparam`: `enableNetworkModule=true`, `enableKeyVaultPrivateEndpoint=true`, address space `10.70.0.0/16`.
- [ ] **Step 3:** Run `az bicep build --file infra/main.bicep` → regenerate `infra/main.json`.
Expected: build clean.
- [ ] **Step 4:** Run `az deployment group what-if -g rg-ihzhhpf-prod -f infra/main.bicep -p infra/environments/prod-swn.bicepparam`.
Expected: plan shows **delete+recreate** of `cae-ihzhhpf-prod` + `ca-agent-host` + `ca-signal-runner`, **adds** Cosmos PE + KV PE + VNet; `cae-app-fluent` untouched.
- [ ] **Step 5:** Paste the what-if into the PR / #311-follow-up issue as the plan-of-record.
- [ ] **Step 6: Commit** `feat(infra): enable PROD swn network parity (VNet + Cosmos PE + KV PE) [non-destructive artefacts]`

#### Task B2: Execute the gated destructive recreate

- [ ] **Step 1:** Wait for OWNER `approved-to-apply` on the what-if thread (approver must have repo write access and not be a bot).
- [ ] **Step 2:** Delete `ca-agent-host-ihzhhpf-prod`, `ca-signal-runner-ihzhhpf-prod`, `cae-ihzhhpf-prod` (explicit approved step).
- [ ] **Step 3:** Run `cd-infra-deploy-prod` (confirm=`approved-to-apply`, `prod` env) → ARM creates the VNet-integrated CAE + both apps clean.
- [ ] **Step 4:** Run the ADR-0029 10-check verification (private DNS resolves in-CA, PE `Approved`, DNS auto-registration, MI role bind present, agent-host→Cosmos over private link). Capture outputs.
- [ ] **Step 5:** `curl https://app.curavias.ch` → 200 (confirms app CAE unaffected); agent-host `/agents` → 7.
- [ ] **Step 6:** Promote `docs/adr/0039-prod-network-parity-vnet-private-endpoints.md` `Status: Proposed`→`Accepted`; echo approver handle + timestamp in the commit. Bump header MINOR.
- [ ] **Step 7: Commit** `feat(infra): PROD swn network parity applied; ADR-0039 Accepted (approved-to-apply by @<owner> <ts>)`

### Phase C — IaC parity for out-of-band resources (#252) — D2

> **STATUS 2026-07-24: CSA Cosmos DONE.** `main.bicep` now wires the CSA Cosmos module (`enableCsaCosmosModule=true` in `prod-swn.bicepparam` + `sit.bicepparam`) and live PROD has `pe-cosmos-csa-ihzhhpf-prod` (Approved) — #252 Gap 1/2 closed. **Remaining:** verify the ACR portion (#252 Gap 3 — no `Microsoft.ContainerRegistry/registries` *creation* module; ACR is still referenced as `existing` by name) and confirm the CI parity job covers CSA Cosmos.

**Files:** Modify `infra/main.bicep`, add `infra/modules/cosmos/parameters/prod-swn.bicepparam`, add an ACR module

- [ ] **Step 1:** Wire `infra/modules/cosmos/main.bicep` (CSA) into `infra/main.bicep` behind an `enableCsaCosmosModule` flag; set true in `sit.bicepparam` + `prod-swn.bicepparam`.
- [ ] **Step 2:** Add a `Microsoft.ContainerRegistry/registries` module; make the Container App modules resolve the ACR via `existing` with an explicit scope (fixes the cross-RG `ResourceNotFound` from #252).
- [ ] **Step 3:** `az bicep build --file infra/main.bicep`; `what-if` against **both** `rg-ihzhhpf-sit` and `rg-ihzhhpf-prod`.
Expected: no unintended deletes; CSA Cosmos + ACR recognised as existing (no recreate) or additively created.
- [ ] **Step 4:** Extend `.github/workflows/ci-infra-validate.yml` SIT↔PROD parity job to assert CSA Cosmos + ACR exist in both RGs.
- [ ] **Step 5:** Gated `approved-to-apply` re-deploy to reconcile; verify no drift.
- [ ] **Step 6:** `gh issue close 252` with evidence.
- [ ] **Step 7: Commit** `feat(infra): bring CSA Cosmos + ACR under main.bicep for SIT/PROD parity (closes #252)`

### Phase D — Fabric IQ ontology disposition (#270) — D3

- [ ] **Step 1:** Re-probe `POST …/items {type:"Ontology"}` on the swn PROD capacity to confirm the `403 FeatureNotAvailable` still holds; record DataAgent/GraphModel control probes.
- [ ] **Step 2:** Record the disposition in `#270` and the parity matrix: **"open — not-relevant to GA parity per ADR-0006 (Preview, Microsoft-side per-capacity gate); SIT remains the live IQ seam."**
- [ ] **Step 3:** Add a revisit trigger to ADR-0037 §Revisit (already present) — confirm it links #270.
- [ ] **Step 4: Commit** `docs: record PROD Fabric IQ ontology as Preview-gated (N/A for GA parity) (#270)`

### Phase E — Signal-runner identity hardening (current branch)

- [ ] **Step 1:** Complete the `ca-signal-runner-ihzhhpf-prod` managed-identity hardening on `sprint-19/harden-signal-runner-identity` (align with ADR-0036 external-trigger governance; least-privilege MI, no secrets).
- [ ] **Step 2:** Verify the signal-runner MI role bindings match SIT; capture in the parity matrix.
- [ ] **Step 3: Commit** per Conventional Commits; reference #290.

### Phase F — End-to-end SIT↔PROD parity evidence (the deliverable)

**Files:** Create `docs/sprints/sprint-19/sit-prod-parity-matrix.md`

Produce a level-by-level parity matrix with a live command + captured evidence per row. Each row = SIT value, PROD value, parity verdict (✅ parity / ⚠️ waived-per-ADR / ❌ gap), evidence pointer.

- [ ] **Step 1:** Compute the matrix rows:
  - **IaC:** `az deployment group what-if` diff (post-C) both RGs → 0 drift.
  - **Network:** VNet + Cosmos PE + KV PE present both sides; ADR-0029 10-checks (post-B).
  - **Data:** Fabric workspace, lakehouse, Delta table count (50), semantic model DAX parity (dim_hospital, [Active Encounters], [Beds Total], [Occupancy %]).
  - **AI/agents:** 3 models + 8 registered agents + agent-host `/agents`→7 both sides; live inference probe.
  - **App:** custom domain + TLS + HTTP 200 (`app.curavias.ch` PROD / `appsit` SIT).
  - **DNS/TLS:** CNAME + managed cert `SniEnabled` both.
  - **Identity:** signal-runner + agent-host MI bindings match.
  - **Governance:** policy gate green, exceptions valid, evidence co-located (NFR-GOV-005).
  - **Fabric IQ:** ⚠️ waived (D3).
- [ ] **Step 2:** Run each verification command; paste outputs under `docs/sprints/sprint-19/evidence/2026-07-24-*`.
- [ ] **Step 3:** Author the matrix doc (header v1.0.0, per §9). Every ❌ must map to a tracker; every ⚠️ must cite the ADR.
- [ ] **Step 4:** Run `npx --yes markdownlint-cli2` + link check.
- [ ] **Step 5: Commit** `docs: add evidence-backed SIT<->PROD parity matrix (all levels)`

### Phase G — Curavias product documentation + traceability refresh

**Files:** Create `docs/CURAVIAS-PRODUCT-STATUS.md`; modify `docs/ARCHITECTURE.md`, `docs/INFRASTRUCTURE.md`, `docs/INTEGRATION.md`, `docs/OPERATIONS.md`, `docs/DATA.md`, `docs/AI.md`, `docs/PRD.md`, `docs/COMPLIANCE.md`, `docs/SECURITY.md`

- [ ] **Step 1:** For each doc above, update topology/region/network statements to the **as-deployed swn PROD + SIT split** reality; bump each header per §9 (MINOR for additive, PATCH for editorial). Use the `document-authoring` skill for each edit.
- [ ] **Step 2:** Create `docs/CURAVIAS-PRODUCT-STATUS.md` — an executive "as-deployed" view: region posture (F1), data posture (F2), SIT posture (F3), the parity matrix summary (link Phase F), and a **requirements coverage table** mapping every relevant `FR-*`/`NFR-*` to one of: **Covered** (link evidence), **Open** (link tracker), **N/A-per-ADR** (link ADR). Include the Fabric-IQ-ontology N/A row (D3) and network-parity Covered row (post-B).
- [ ] **Step 2b:** For the Curavias web PROD item (#275), record it in the status doc as **Open — deferred to Sprint 20/24 UX track** (D6), and rescope the issue off the deleted eastus2 param.
- [ ] **Step 3:** Update `docs/PRD.md` §Traceability Matrix: add a row for this extension (`sprint-19/sit-prod-parity-matrix.md` + `CURAVIAS-PRODUCT-STATUS.md`) with its requirement coverage; bump PRD header MINOR; update Previous Version.
- [ ] **Step 4:** Run `npx --yes markdownlint-cli2 "**/*.md" "#node_modules"` + `markdown-link-check` on the edited docs.
Expected: PASS.
- [ ] **Step 5: Commit** `docs: refresh Curavias product docs + requirements traceability to as-deployed PROD (swn) status`

### Phase H — Close-out

- [ ] **Step 1:** Update `docs/sprints/sprint-19/prod-evidence-switzerlandnorth.md` DoD table with the new parity criteria (network, IaC, identity) → bump MINOR.
- [ ] **Step 2:** PR description lists every `FR-*`/`NFR-*` advanced (NFR-GOV-006), lane impact (governance/control/infra/data/AI), security impact (network PE, MI), compliance impact (F2/F3 Accepted).
- [ ] **Step 3:** Confirm all CI green; request CODEOWNERS review (ADR + mcp/security-touching changes).
- [ ] **Step 4:** Close #239 with the parity matrix as capstone evidence; keep #270 open (N/A-parity), #275 rescoped/deferred.

---

## 5. Definition of Done

- [ ] F1/F2/F3 reconciled in governance: ADR-0013/0016 **Accepted**; eastus2 charter + #239 superseded to swn.
- [ ] ADR number collisions (0039/0021) resolved with an ADR + fixed links.
- [ ] PROD network parity applied (VNet + Cosmos PE + KV PE); ADR-0039 **Accepted**; ADR-0029 10-checks green; `app.curavias.ch` still 200.
- [ ] CSA Cosmos + ACR under `infra/main.bicep`, drift-checked in CI for SIT **and** PROD (#252 closed).
- [ ] Fabric IQ ontology disposition recorded as N/A-for-GA-parity (D3); #270 annotated.
- [ ] Signal-runner MI hardening complete and at SIT parity.
- [ ] `docs/sprints/sprint-19/sit-prod-parity-matrix.md` committed — every level ✅/⚠️/❌ with live evidence; each ⚠️ cites an ADR, each ❌ a tracker.
- [ ] `docs/CURAVIAS-PRODUCT-STATUS.md` + refreshed product docs reflect as-deployed swn PROD; requirements coverage = Covered / Open / N/A-per-ADR, fully traceable.
- [ ] PRD §Traceability updated; all doc headers bumped per §9; markdownlint + link-check green.

---

## 6. Risk register

| Risk | Mitigation |
|------|------------|
| Destructive CAE recreate outage | ~5–10 min, agent-host only; `app.curavias.ch` on separate CAE; gated `approved-to-apply`; DR-style runbook. |
| `what-if` differs from approved plan | Re-plan + re-request approval per AGENTS.md §4. |
| IaC re-deploy causes unintended deletes | `what-if` gate on both RGs; wire resources as `existing` where already provisioned. |
| ADR renumber breaks inbound links | Redirect stubs + `markdown-link-check` gate before merge. |
| Fabric IQ gate reopens Microsoft-side | Tracked in #270 with ADR-0037 revisit trigger; independent of GA-core parity. |
| Doc drift during refresh | `document-authoring` skill judgment checks + CI mojibake/lint gates. |

---

## 7. Self-review

- **Spec coverage:** F1→A2/G; F2→A1/G; F3→A1/G; network parity→B/F; IaC parity→C/F; Fabric IQ→D/G; docs+traceability→G; evidence all levels→F. All user asks mapped.
- **Placeholders:** ADR renumber target integers and exact PROD param values are resolved at execution against the live repo (next-free ADR number, current param file) — flagged as compute-at-exec, not left as vague TODOs.
- **Consistency:** flags `enableNetworkModule` / `enableKeyVaultPrivateEndpoint` / `enableCsaCosmosModule` used consistently across B1/C1; RG names `rg-ihzhhpf-prod` (swn) and `rg-ihzhhpf-sit` used consistently.

---

## 8. References

- [ADR-0037 — PROD Switzerland North greenfield](../../adr/0037-prod-region-switzerland-north-greenfield.md)
- [ADR-0039 — PROD network parity (VNet + PEs)](../../adr/0039-prod-network-parity-vnet-private-endpoints.md)
- [ADR-0013 — Temporary US-region demo scope](../../adr/0013-temporary-us-region-demo-scope.md)
- [ADR-0016 — No PHI in MVP demo scope](../../adr/0016-no-phi-in-mvp-demo-scope.md)
- [ADR-0029 — agent-host↔Cosmos reachability (10-check)](../../adr/0029-agent-host-cosmos-reachability.md)
- [Sprint 19 PROD swn evidence](../../sprints/sprint-19/prod-evidence-switzerlandnorth.md)
- [DR-rebuild runbook](../../runbooks/sprint-19-prod-switzerland-north-dr-rebuild-runbook.md)
- Open issues: #239, #252 (IaC parity), #270 (Fabric IQ), #275 (Curavias web), #290 (signal triage), #299 (SPA fallback)
