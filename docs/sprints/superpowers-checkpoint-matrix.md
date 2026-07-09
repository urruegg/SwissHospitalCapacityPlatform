# Superpowers Checkpoint Matrix (Shared)

| Field | Value |
| ----- | ----- |
| **Version** | 1.3.0 |
| **Date** | 2026-07-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 1.2.0 (added Sprint 16 execution-log rows 13–16, Sprint 16 retro notes, and the Sprints 11–16 program close-out) |

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
| 13 | 2026-07-09 | — | In flight (issue #161 / PR #162) | Container Apps agent-host + whiteboard + Copilot Drawer | — | — | — |
| 14 | 2026-07-09 | — | In flight (issue #164 / PR #165) | Evidence tab + presenter whiteboard | — | — | — |
| 15 | 2026-07-09 | — | In flight (issue #167) | BVA (business-value analytics) | — | — | — |
| 16 | 2026-07-09 | — | Foundation authored; live runs gated | `csa-agent` full body + Cosmos IaC + 8 scenarios + 3 MVP runs | Structural (eval-goldens) | [`../superpowers/specs/2026-07-09-sprint-16-csa-design.md`](../superpowers/specs/2026-07-09-sprint-16-csa-design.md) | [`../superpowers/plans/2026-07-09-sprint-16-csa-plan.md`](../superpowers/plans/2026-07-09-sprint-16-csa-plan.md) |

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

### Sprint 16 retro notes

- **CSA foundation authored** (issue #170): `csa-agent` expanded from the
  Sprint 11 Prepare-only scaffold to the full **Prepare → Run → Evaluate →
  Recommend** body (`deploy` ceiling, gated), Cosmos DB IaC
  (`infra/modules/cosmos/`, 4 vector containers), 4 JSON Schemas, ~80
  response-levers, 8 seeded scenarios (F1–F8), the version-pinned tier
  classifier ([ADR-0021](../adr/0021-csa-tier-classifier-rules.md)), the pure
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
| 13 | App + agent-host | #161 | PR #162 | In flight |
| 14 | Evidence tab | #164 | PR #165 | In flight |
| 15 | Business-value analytics | #167 | — | In flight |
| 16 | CSA what-if catalogue | #170 | this PR | Foundation authored; live runs gated |

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
