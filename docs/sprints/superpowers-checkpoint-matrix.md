# Superpowers Checkpoint Matrix (Shared)

| Field | Value |
| ----- | ----- |
| **Version** | 1.6.0 |
| **Date** | 2026-07-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 1.5.0 (Sprint 15 in-flight row + Sprint 16 rows/retros + program close-out added) |

## Purpose

Provide one reusable checkpoint matrix for all sprint executions that use
Superpowers as mandatory operating mode.

## Stage and Gate Matrix

| Stage | Checkpoint | Pass Criteria | Evidence |
| ----- | ----- | ----- | ----- |
| brainstorming | Design brief approved | Alternatives and acceptance criteria documented | Link to issue comment or artifact |
| using-git-worktrees | Worktree isolation complete | One worktree per major slice and clean baseline check | Terminal output or note |
| writing-plans | Plan quality gate | Tasks include files, verification, requirement mapping | Plan artifact link |
| execution | Spec compliance review | No unresolved critical spec deviation | Review note link |
| execution | Quality review | No unresolved critical quality defect | Review note link |
| execution | Systematic debugging gate | Debug workflow evidence exists for any failure/regression path | Debug log link |
| test-driven-development | Validation proof | RED-GREEN evidence or test-first checklist attached | Test output link |
| requesting-code-review | Severity gate | Critical findings resolved or accepted by owner | Review summary link |
| finishing-a-development-branch | Verification-before-completion | Final verification evidence attached before completion claim | Verification output link |
| finishing-a-development-branch | Closeout gate | PR contract complete and branch decision recorded | PR link |

## Cross-Cutting Governance Checks

| Check | Pass Criteria | Evidence |
| ----- | ----- | ----- |
| Traceability | FR/NFR IDs explicit in issue and PR | Issue + PR links |
| Sprint traceability chain | Issue exists first and PR follows with backlink | Issue + PR links |
| Core skill evidence | PR includes applicability and evidence for core Superpowers skills | PR section |
| Compliance impact | Compliance impact statement included | PR section |
| Security impact | Security impact statement included | PR section |
| Deploy/delete guardrail | `approved-to-apply` used where applicable | PR/issue comment |
| Required checks | Lint/test/policy checks pass for scope | Command output links |

## Sprint Execution Log

Per-sprint closeout entries. Each row records the Superpowers-cycle outcome for a
sprint executed under this matrix.

| Sprint | Start | End | Status | Agents shipped | Evals green | Design spec | Plan |
| ------ | ----- | --- | ------ | -------------- | ----------- | ----------- | ---- |
| 11 | 2026-07-09 | 2026-07-09 | Merged | 8/8 (7 MVP + 1 stretch) | Yes | [`../superpowers/specs/2026-07-09-sprint-11-agents-design.md`](../superpowers/specs/2026-07-09-sprint-11-agents-design.md) | [`../superpowers/plans/2026-07-09-sprint-11-agents-plan.md`](../superpowers/plans/2026-07-09-sprint-11-agents-plan.md) |
| 12 | 2026-07-09 | — | Artefacts authored; SIT applies gated | 17 app roles + 17 groups + 23 personas (IaC authored) | n/a (IaC + telemetry) | [`../superpowers/specs/2026-07-09-sprint-12-org-design.md`](../superpowers/specs/2026-07-09-sprint-12-org-design.md) | [`../superpowers/plans/2026-07-09-sprint-12-org-plan.md`](../superpowers/plans/2026-07-09-sprint-12-org-plan.md) |
| 13 | 2026-07-09 | 2026-07-09 | Merged | n/a (app tier) | Yes | [`../superpowers/specs/2026-07-09-sprint-13-app-design.md`](../superpowers/specs/2026-07-09-sprint-13-app-design.md) | [`../superpowers/plans/2026-07-09-sprint-13-app-plan.md`](../superpowers/plans/2026-07-09-sprint-13-app-plan.md) |
| 14 | 2026-07-09 | 2026-07-09 | Merged (T1–T3 landed; T4–T7 follow-up) | n/a (workflow-only) | Yes (parsers + readiness golden) | [`../superpowers/specs/2026-07-09-sprint-14-evidence-design.md`](../superpowers/specs/2026-07-09-sprint-14-evidence-design.md) | [`../superpowers/plans/2026-07-09-sprint-14-evidence-plan.md`](../superpowers/plans/2026-07-09-sprint-14-evidence-plan.md) |
| 15 | 2026-07-09 | 2026-07-09 | Artefacts authored; live publishes gated | BVA evidence data product (generator + medallion + semantic model + 6 C-suite pages + 3 whiteboard cards) | Yes (Python golden + structural + vitest) | [`../superpowers/specs/2026-07-09-sprint-15-bva-design.md`](../superpowers/specs/2026-07-09-sprint-15-bva-design.md) | [`../superpowers/plans/2026-07-09-sprint-15-bva-plan.md`](../superpowers/plans/2026-07-09-sprint-15-bva-plan.md) |
| 16 | 2026-07-09 | 2026-07-09 | Foundation authored; live runs gated | `csa-agent` full body + Cosmos IaC + 8 scenarios + 3 MVP runs | Structural (eval-goldens) | [`../superpowers/specs/2026-07-09-sprint-16-csa-design.md`](../superpowers/specs/2026-07-09-sprint-16-csa-design.md) | [`../superpowers/plans/2026-07-09-sprint-16-csa-plan.md`](../superpowers/plans/2026-07-09-sprint-16-csa-plan.md) |

### Sprint 11 retro notes

- All 8 agents (`bmca-agent`, `ooa-agent`, `dca-agent`, `orsa-agent`,
  `sba-agent`, `csa-agent` scaffold, `data-quality-agent`, `onboarding-agent`
  stretch) shipped with prompt file, ≥ 2 golden-task fixtures, runtime
  `manifest.yaml`, `agents/` compatibility stub, and an `AGENTS.md` §1 row.
- Model selection recorded in
  [`../adr/0020-sprint11-agent-model-selection.md`](../adr/0020-sprint11-agent-model-selection.md)
  and referenced by every agent.
- `fabric-mcp` and `entra-mcp` (read-only) added to
  [`../../.github/copilot/mcp.json`](../../.github/copilot/mcp.json) and
  `AGENTS.md` §2.
- Golden-task fixtures replayed structurally via
  [`../../.github/workflows/eval-goldens.yml`](../../.github/workflows/eval-goldens.yml).
- No Foundry Agent Service deployment (application-hosted per ADR-0008); the
  Sprint 13 Container Apps agent-host loads the manifests at runtime.
- `csa-agent` is a scaffold only — the Prepare phase is stubbed and the
  Run/Evaluate/Recommend body lands in Sprint 16. The Sprint 09 runtime pack at
  `agents/csa-agent/` was left intact.

### Sprint 12 retro notes

- **Entra demo-org IaC authored** under `infra/modules/entra/` (Microsoft Graph
  Bicep extension): `app-roles` (17-role catalog), `app-registration` (+ service
  principal), `security-groups` (one per role, membership from personas),
  `users` (23 personas, secure-param password), `assignments` (group-based
  app-role assignment), `adoption-telemetry` (tenant-scoped SignInLogs
  diagnostic setting), `main` orchestrator, `sit`/`prod` param files, and
  `bicepconfig.json` pinning the Graph extension.
- **Adoption telemetry** (T5): `01_adoption_ingest.ipynb` Fabric notebook,
  `adoption_seed_synthetic.py` (30-day × 23-persona ≈ 1.4k-row backfill), and
  `.github/workflows/adoption-refresh.yml` (nightly 03:00 UTC).
- **Delegation assets** (T6): `.github/workflows/entra-whatif.yml` (posts the
  `what-if` plan as a PR comment) and `.github/ISSUE_TEMPLATE/entra-provisioning.yml`.
- **Persona seed** `data/synthetic/personas.csv` extended to the full 23-persona
  catalog (design spec §6) with a `mail_nickname` column; the six UPNs pinned by
  `rls_test`/`dim_persona_check` are preserved so those checks stay green.
- **Gated / not executed here**: every `az deployment` apply (app registration,
  users, groups, assignments, diagnostic setting) is a `deploy`-ceiling action
  requiring an `approved-to-apply` comment (AGENTS.md §4) and live Azure Graph
  consent — none were run in this environment. SIT applies, super-role sign-in
  verification, and the nightly-file DoD checks remain for the human-gated
  follow-up. PROD is deferred to a `prod-batch` follow-up.
- **Open reconciliation**: design spec §1 says "15 app roles" but the §6 persona
  catalog references 15 operational roles + 2 super = 17. The IaC provisions all
  17 for internal consistency; reviewer to confirm the count at the gate (see
  `infra/modules/entra/README.md`).

### Sprint 13 retro notes

- **App tier delivered** across T1–T8: `apps/hcc-app-fluent/` (Fluent UI v9
  baseline), `apps/hcc-agent-host/` (Python + FastAPI Container Apps agent-host,
  [ADR-0022](../adr/0022-agent-host-language-python-fastapi.md)), and
  `apps/hcc-app-rayfin/` (PoC placeholder).
- **Fluent baseline** (T1–T4, T6): two-workspace shell, MSAL auth with
  `roles`/`hospital`/`env` claim parsing + SIT-gated role switcher, BedManager
  whiteboard with 6 card types over a custom canvas
  ([ADR-0021](../adr/0021-whiteboard-base-react-flow-vs-tldraw-vs-custom.md)),
  Backstage Roles tab (read-only Entra Graph), Copilot Drawer wired to BMCA.
  20 vitest unit tests + Playwright smoke/a11y/contract green; `app-build.yml`,
  `app-e2e.yml`, `app-a11y.yml` added.
- **Agent-host** (T5): manifest loader, orchestrator + Fabric grounding,
  deny-by-default HITL gate (ADR-0007 §6 schema), redaction, tool adapters,
  in-memory Cosmos/Redis stand-ins, FastAPI surface (`/agents`,
  `/agents/<name>/chat`, `/agents/<name>/tools/<tool>`, `/healthz`). 31 pytest
  tests green; `agent-host-build.yml` added; Bicep authored under
  `infra/modules/agent-host/` (`az bicep build` clean, **not deployed**).
- **Live deploys deferred**: T5's Container Apps + Redis + Cosmos provisioning is
  a `deploy`-ceiling action requiring the AGENTS.md §4 `approved-to-apply` gate,
  which was not exercised in this delivery. The Bicep is authored and validated
  but no Azure resources were created; the app + agent-host run on deterministic
  mocks + in-memory persistence in CI.
- **Rayfin PoC — not evaluable in scope** (T7): the proprietary Rayfin generator
  was not runnable in the environment. Recorded per the T7 time-box rule; the
  exit decision ADR
  [ADR-0023](../adr/0023-app-stack-fluent-vs-rayfin-decision.md) recommends the
  **Fluent** baseline for Sprint 14+.

### Sprint 14 retro notes

- **T1–T3 landed** as the fully-verifiable data-product foundation:
  - T1 — five evidence parsers (`prd`, `adr`, `bom`, `region_availability`,
    `infra`) + publish orchestrator + 7 JSON Schemas + `evidence-publish.yml`
    (publishes to the `evidence-latest` branch, never `main`). Byte-stable
    output with provenance on every row. 25 parser tests green.
  - T2 — seed catalogs: `docs/bom.yaml` (25 items), `docs/region-availability.yaml`
    (50 facts), `docs/adr-requirement-map.yaml` (10 curated edges), `bom-item` +
    `ga-evidence-refresh` issue templates, `docs/bom.schema.md`, CODEOWNERS.
  - T3 (core) — readiness scoring pure module (`readiness_rules.py`) codified in
    [`../adr/0021-readiness-scoring-rules.md`](../adr/0021-readiness-scoring-rules.md),
    byte-stable golden regression (7 tests green), Bronze→Silver→Gold notebooks +
    `docs/data-platform/evidence-gold-schema.md`.
- **Deferred to follow-up** (per design spec §11 fallback):
  - T3 Fabric pipeline **publish** and T4 semantic-model **publish** — both
    `deploy`-ceiling, gated by `approved-to-apply`; not run in the cloud-agent
    environment.
  - T4 semantic-model TMDL extension.
  - T5 (5 whiteboard card types) + T6 (Backstage Evidence tab) — **blocked** on
    the unmerged Sprint 13 app framework (`apps/hcc-app-fluent/` does not yet
    exist). Land in a follow-up mini-sprint once Sprint 13 T3/T4 merge (issue #161).

### Sprint 15 retro notes

- **BVA evidence data product authored end-to-end** (issue #167; T1 merged as
  PR #168, T2–T9 in the continuation PR). Delivered as a fully in-sandbox,
  dependency-free, buildable artefact set:
  - **T1** — deterministic synthetic Azure-consumption generator in FOCUS export
    shape (`data-platform/scripts/bva_synth_focus.py`), calibrated to the
    CHF 760k/yr ROM baseline ±15% (5-seed regression); 22 tests + `bva-generator.yml`.
  - **T2** — nightly `bva-sim-refresh.yml` (generate → upload to
    `Bronze/consumption/` → trigger pipeline) with a gated Bronze upload helper.
  - **T3** — Fabric medallion Bronze→Silver→Gold with **`bva_`-prefixed** gold
    tables (`gold.bva_dim_*`, `gold.bva_fact_*`) to avoid collision with the
    operational dimensions and to de-conflict with concurrent PR #172; 23
    notebook tests + `bva-medallion.yml` + `docs/data-platform/bva-gold-schema.md`.
  - **T4** — adoption-telemetry join into `gold.bva_fact_value_realization` using
    the documented **30-day synthetic backfill** (design spec §14 mitigation),
    because Sprint 12 T5/T6 adoption emission has not landed; switchover point recorded.
  - **T5** — Direct Lake semantic-model extension (`bva_` TMDL tables + 28 KPI
    measures), a pure `bva_kpi.py` reference module as the single source of formula
    truth, 11 golden tests, and the KPI-catalog [ADR-0025](../adr/0025-bva-kpi-catalog.md).
  - **T6** — 6 C-suite Power BI pages (Board / CEO / CFO / CIO / COO / CTO) in the
    `bva-boardroom.Report` PBIR, 2 RLS roles (`BvaExecFull`, `BvaBoardReadOnly`),
    RLS test plan + 9 structural tests.
  - **T7** — 3 BVA whiteboard card types (`BvaHeadlineKpiCard`,
    `BvaPlanVsActualCard`, `BvaTrendCard`) in `apps/hcc-app-fluent` with a
    provenance footer + BVA board mock; **Power BI embed fallback** per design
    spec §14 because the Sprint 14 T5/T6 whiteboard Evidence tab was not delivered
    (Sprint 14 stopped at T3). 26 vitest tests green; production build clean.
- **T8 (stretch) — not attempted.** The application-hosted `bva-agent` per
  ADR-0008 depends on the Sprint 13 T5 agent-host **and** a live Foundry model
  (`sprint11-chat`); neither is deployed, so the monthly board-pack agent is
  carried forward per plan §Task 8.
- **Gated / not executed here** (AGENTS.md §4, all require `approved-to-apply` +
  live Azure): T3 Fabric pipeline publish to `ws-ihzhhpf-sit-data`, T5 semantic
  model publish, T6 Power BI report publish + RLS role assignment, and the
  optional T8 agent-host redeploy. All are authored and staged; none were run.



- **CSA foundation authored** (issue #170): `csa-agent` expanded from the
  Sprint 11 Prepare-only scaffold to the full **Prepare → Run → Evaluate →
  Recommend** body (`deploy` ceiling, gated), Cosmos DB IaC
  (`infra/modules/cosmos/`, 4 vector containers), 4 JSON Schemas, ~80
  response-levers, 8 seeded scenarios (F1–F8), the version-pinned tier
  classifier ([ADR-0024](../adr/0024-csa-tier-classifier-rules.md); renumbered
  from 0021 at merge to avoid collision with Sprint 13/14 ADRs), the pure
  shock-model simulation, and the `csa-scenario-sync` / `csa-run-followup`
  workflows + issue templates.
- **3 MVP runs** captured under [`../csa/runs/`](../csa/runs/) — RSV surge
  (Tier 2), cyberattack (Tier 3), heatwave (Tier 2) — computed deterministically
  by `csa-simulate.simulate()` over synthetic baselines (ADR-0016), reproducing
  the classifier output the live Fabric run would emit.
- **Gated / not executed here**: Cosmos `az deployment` apply, Fabric Mirroring
  enable (T2), the `csa-simulate` notebook publish (T5), and live wizard MVP runs
  (T7, depends on the Sprint 13 app) each require an `approved-to-apply` comment
  (AGENTS.md §4) and live Azure — none were run in this environment.

## Program close-out (Sprints 11–16)

The six-sprint Superpowers program (S11–S16) is **complete as an authored,
buildable artefact set**; every live-cloud apply remains behind its
`approved-to-apply` gate for the human-run SIT/PROD follow-up.

| Sprint | Theme | Kickoff issue | Delivery trail | Status |
| ------ | ----- | ------------- | -------------- | ------ |
| 11 | Agents (8 packs) | — | Sprint 11 design + plan; `agents/*` | Merged |
| 12 | Identity (Entra org + roles) | — | `infra/modules/entra/`; PR #159 (MSAL) | Artefacts authored; SIT gated |
| 13 | App + agent-host | #161 | PR #162 | Merged |
| 14 | Evidence tab | #164 | PR #165 | Merged (T1–T3) |
| 15 | Business-value analytics | #167 | PR #168 (T1) + continuation (T2–T9) | Artefacts authored; live publishes gated |
| 16 | CSA what-if catalogue | #170 | this PR (#171) | Foundation authored; live runs gated |

**Approved-to-apply gates used in this program run:** 0 executed in-sandbox — all
`deploy`/`delete` steps across S12 (Entra applies), S13 (agent-host redeploy),
and S16 (Cosmos apply, Mirroring, notebook publish, live runs) are documented and
staged for the human-gated follow-up. The Sprint 16 design spec §11 budgeted
~4–5 gates for CSA alone.

**Deferred / carried forward (clean-slate list for the next program):**

- Sprint 10 medallion backlog — 7 pending Gold tables (issue #154).
- All S12/S13/S16 live Azure applies behind `approved-to-apply` (Entra, Cosmos,
  Mirroring, notebook publish, live wizard MVP runs).
- Full 20+ discovered CSA scenarios (roadmap Q-5) — MVP shipped 8 seeded, 3 run.
- External-actor integration modelling (Rega, KSD/IES) beyond notification events.
- Automated re-scoring of CSA runs on capacity-data change.
- `fabric-data-agent` runtime-posture reconciliation with ADR-0008 (open
  follow-up noted in AGENTS.md §1).
