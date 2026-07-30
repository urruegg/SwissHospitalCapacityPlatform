# Curavias — Test Strategy

| Field | Value |
| ----- | ----- |
| **Version** | 0.9.0 |
| **Date** | 2026-07-29 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 0.8.0 (updated Agent control lane row for the 2.0.0 `agents-archive/` → `agents/` restructure); this bump rebrands the doc to the Curavias customer-ready template - anchored title, product anchor, and executive summary (Sprint 34 WS-4) |

> **Curavias** is the Swiss AI-powered patient-flow and hospital-capacity
> platform — a Microsoft Frontier-Firm reference implementation grounded on
> Fabric IQ, Foundry IQ, and Work IQ.

## Executive summary

This document defines how Curavias proves quality: the test strategy, the quality
gates every change must pass, and the evidence captured at each release. It is
written so a stakeholder can see what "done and verified" means for the platform.

## Purpose

Define the baseline quality strategy, quality gates, and evidence model for
Curavias, the Swiss AI-powered patient-flow and hospital-capacity platform,
in this repository.

This plan is designed for the current repository shape where delivery is
governance-first (documents, Superpowers execution workflow, compatibility
agent prompts, workflows, and IaC outputs), with
future extension into data, AI, app, and integration code lanes.

## Source Baseline

This document is aligned to:
1. docs/PRD.md
2. docs/ARCHITECTURE.md
3. docs/AI.md
4. docs/SECURITY.md
5. docs/COMPLIANCE.md
6. docs/DATA.md
7. docs/SD.md
8. AGENTS.md

## Test Strategy

### Objectives

1. Prevent regressions in requirements traceability and architecture decisions.
2. Verify agent behavior against expected safe/unsafe outcomes.
3. Validate IaC artifacts for syntax, policy alignment, and deployment fitness.
4. Keep compliance and security evidence reviewable and auditable per release.

### Quality Lanes and Validation Methods

| Lane | Scope | Baseline Validation |
| ----- | ----- | ----- |
| Governance docs | PRD, ARCHITECTURE, AI, SECURITY, COMPLIANCE, DATA, BVA, README, sprint docs | Markdown lint, link check, traceability review |
| Superpowers execution lane | Superpowers-driven issue intake, planning, execution, and completion evidence | Execution-mode declaration, plan/verification evidence, PR contract conformance |
| Agent control lane | agents/*/AGENT.md, agents/*/manifest.yaml, and agents/*/golden-tasks.md (single source of truth after the 2.0.0 folder restructure) | Golden-task compatibility replay, refusal and side-effect checks |
| Infrastructure lane | infra/**/*.bicep and environment parameters (when present) | Bicep build, what-if validation, policy baseline checks |
| Delivery lane | .github workflows, issue templates, PR templates | Workflow lint, branch and approval rule checks |
| Future data/AI/app lanes | data-platform, ai-models, apps, integrations (when populated) | Lane-specific tests and evaluation packs defined in lane-local READMEs |

### Test Levels

1. Static validation: linting, link validation, schema or syntax checks.
2. Contract validation: requirement-to-artefact mapping and interface checks.
3. Behavioral validation: agent golden-task fixtures and refusal behavior.
4. Operational readiness validation: what-if and release gate evidence review.

## Quality Gates

### Gate 1: Documentation Integrity

Required for any change under docs/, docs/sprints/, AGENTS.md, or README.md.

1. Markdown lint passes.
2. Link check passes.
3. Version header is updated per document versioning rules.
4. Requirement and control traceability remains explicit for changed scope.

### Gate 2: Execution Method Safety

Required for execution-workflow changes under issue templates, PR templates,
agents/ or AGENTS.md.

1. Superpowers execution mode is declared for new work unless compatibility mode
	is explicitly required.
2. For legacy-agent compatibility mode, at least one happy-path and one
	failure-mode golden task are validated.
3. Side-effect ceilings remain unchanged unless explicitly approved.
4. Deploy/delete confirmation rules remain intact and testable.

### Gate 3: Infrastructure Fitness

Required for any change under infra/ (when infra lane is populated).

1. Bicep builds successfully.
2. what-if output is generated and reviewed before apply.
3. Required tags and diagnostics controls are present.
4. Security and compliance control mappings are updated if infrastructure changes scope.

### Gate 4: Release Evidence Completeness

Required before marking a PR ready for review.

1. Commands executed and results are documented in PR.
2. Changed requirement IDs are listed and status-labeled.
3. Risk and residual gaps are explicitly called out.
4. Compliance-impact statement is present (or explicitly none).

## Baseline Command Set

Primary baseline commands:

```bash
npx --yes markdownlint-cli2 "**/*.md" "#node_modules"
npx --yes markdown-link-check docs/**/*.md docs/sprints/*.md .github/*.md
az bicep build --file infra/main.bicep
az deployment group what-if -g <rg> -f infra/main.bicep
```

Note: If infra/main.bicep is not present in a specific sprint scope, document the
reason in the PR validation evidence.

## Requirement Coverage Validation Approach

For non-trivial changes, maintain an explicit mapping between changed artifacts and:

1. FR families affected.
2. NFR families affected.
3. Compliance controls affected (CH-Cxx).

Minimum evidence pattern:
1. Requirement IDs listed in PR description.
2. Changed artifact references.
3. Validation command output summary.
4. Residual gap and mitigation note.

## Evidence and Reporting

### PR Evidence Contract (Test Perspective)

Each PR should include:
1. Validation commands executed.
2. Pass/fail outcome summary.
3. Links to updated artifacts and golden tasks.
4. Known limitations or deferred items.

### Quality Reporting Cadence

1. Per PR: gate outcomes captured in PR template.
2. Per sprint: quality summary in sprint document.
3. Per release candidate: readiness statement including open risks and accepted waivers.

### Sprint 05 Evidence-Automation Checkpoints

Per the consolidated enforcement model in
[`docs/adr/0007-0011-hardening-delta-summary.md`](adr/0007-0011-hardening-delta-summary.md)
and the ADR-0008/0009/0010 evidence schemas, the following checkpoints are mandatory for
affected scope and are captured via the PR evidence checklist
[`docs/sprints/sprint-05/pr-evidence-checklist.md`\](sprints/sprint-05/pr-evidence-checklist.md):

| Checkpoint | Source ADR | Evidence schema | Phase |
| ----- | ----- | ----- | ----- |
| Runtime matrix conformance | ADR-0008 | Boundary contract fields + GA-region evidence | Phase 1+ |
| Policy gate run | ADR-0010 | `policyPackVersion`, `gateName`, `evaluatedResources`, `passFailSummary`, `failureDetails`, `exceptionRefs`, `executionTimestampUtc`, `pipelineRunId` | Phase 2 |
| DR rehearsal | ADR-0009 | `scenarioId`, `systemsInScope`, `targetRtoRpo`, `actualRtoRpo`, `passFailResult`, `gaps`, `owner`, `retestDate` | Phase 3 |
| Cantonal annex check | ADR-0011 | Schema completeness, owner assignment, evidence-link validity, exception status/expiry | Phase 2 |

Promotion thresholds: zero critical policy failures and 100 percent mandatory-control
coverage for SIT to PROD promotion (ADR-0010); expired exceptions are hard blockers.

The `Policy gate run` and `Cantonal annex check` checkpoints above are implemented as
the executable policy gate in [`policy/`](../policy/README.md) (`policy/policy_gate.py`,
`policy/policy-pack.json`, `policy/exceptions.json`,
`policy/schema/evidence-schema.json`). The gate runs in
[`.github/workflows/policy-gate.yml`](../.github/workflows/policy-gate.yml) and as a
blocking step on the SIT and PROD deploy workflows. Validate locally with
`python3 policy/policy_gate.py --scope sit` and `python3 -m unittest discover -s policy/tests`.
The Phase 2 SIT gate evidence is recorded in
[`docs/sprints/sprint-05/phase-2-policy-gate.md`\](sprints/sprint-05/phase-2-policy-gate.md).

### Sprint 09 evidence

Test artefacts and CI gates introduced by Sprint 09 v2.0.0 (see [sprint doc](sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md)).

#### HCC pattern conformance test

1. **Location:** [`apps/sim-capacity/tests/test_seasonal_profile.py`](../apps/sim-capacity/tests/test_seasonal_profile.py)
2. **Purpose:** Verify simulator's LUKS preset reproduces the HCC utilization pattern reference fixture within MAPE < 15%.
3. **Current MAPE:** 2.42% (well below threshold).
4. **Reference fixture:** [`apps/sim-capacity/tests/fixtures/hcc-utilization-pattern-luks-reference.json`](../apps/sim-capacity/tests/fixtures/hcc-utilization-pattern-luks-reference.json)
5. **Evidence location:** `docs/sprints/sprint-09/evidence/hcc-conformance-report.md` (populate at sprint close).

#### PHI regex sweep test (ADR-0016 gate 1)

1. **Location:** [`apps/sim-capacity/tests/test_no_phi.py`](../apps/sim-capacity/tests/test_no_phi.py)
2. **Purpose:** [ADR-0016](adr/0016-no-phi-in-mvp-demo-scope.md) gate 1 — simulator produces no PHI-shaped tokens across all 6 generators × 3 hospitals.
3. **Coverage:** 10 000+ envelopes swept; 4 PHI patterns (email / phone / DOB / CH AHV-13); 18 no-hit tests + 4 self-check positives.
4. **Assertion:** 0 hits.
5. **Evidence location:** `docs/sprints/sprint-09/evidence/phi-sweep-report.md`.

#### 9 agent eval fixtures (design spec §5.5)

1. **Location:** `agents/bm-copilot/golden-tasks.md`, `agents/fabric-data-agent/golden-tasks.md`, `agents/csa-agent/golden-tasks.md`.
2. **Coverage:** 3 fixtures per agent (happy path / out-of-scope refusal / PHI refusal) = 9 total.
3. **Replay:** manual today; automated harness deferred to Sprint 10.
4. **Evidence location:** `docs/sprints/sprint-09/evidence/agent-eval-replay.md`.

#### Ontology conformance CI (design spec §3.5)

1. **Location:** [`.github/workflows/ontology-conformance.yml`](../.github/workflows/ontology-conformance.yml) STRICT step.
2. **Purpose:** Every `hcp:*` reference in [`docs/ontology/crosswalk.md`](ontology/crosswalk.md) must exist in [`docs/ontology/reference-layer.ttl`](ontology/reference-layer.ttl) and be marked concrete or deferred.
3. **Enforcement:** Blocking PR check.
4. **Evidence:** CI badge on every PR touching `docs/ontology/**`.

#### RLS PHI gate verification (ADR-0016 gate 4)

1. **Location:** [`data-platform/reports/capacity-dashboard.SemanticModel/definition/model.tmdl`](../data-platform/reports/capacity-dashboard.SemanticModel/definition/model.tmdl) roles.
2. **Roles covered:** BedOps, ORPlanner, Analyst, SemanticOwner.
3. **Verification approach:** manual query per role on portal-authored TMDL export; assert 0 rows returned on PHI-tagged columns.
4. **Evidence location:** `docs/sprints/sprint-09/evidence/rls-phi-verification.md`.

#### Sprint close checklist

Per [plan § Sprint close](superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md#sprint-close-after-all-35-deliverables):

1. Full CI pipeline green on Sprint 09 v2.0.0 PRs.
2. HCC pattern conformance test locally (MAPE < 15%).
3. PHI regex sweep (0 hits over 10 000 events).
4. 9 agent eval fixtures replay green.
5. RLS PHI gate returns 0 rows for all 4 roles on PHI columns.
6. Suspend Fabric F2 SIT via `Suspend-FabricCapacity.ps1 -Environment sit` ([DX.2 runbook](runbooks/fabric-capacity-lifecycle.md)).

## Defect and Risk Handling

1. Defects are logged as GitHub issues with lane, severity, and requirement tags.
2. Critical defects affecting compliance, security, or data integrity block release.
3. Waivers require explicit owner, expiration date, and mitigation plan.

## MVP Baseline Quality Targets

1. 100 percent pass on markdown and link checks for changed docs.
2. 100 percent pass on required golden tasks for changed agents.
3. Zero unresolved high-severity security/compliance test findings at release gate.
4. Explicit requirement traceability for all changed design and governance artifacts.
5. Zero approval-gate bypasses (`approved-to-apply` remains mandatory for deploy/delete).

## Next Steps

1. Add lane-local test commands as soon as data-platform, ai-models, apps, and
	integrations code lanes are populated.
2. Keep automated legacy golden-task compatibility replay workflow in .github/workflows.
3. Add release dashboard for gate pass rates and requirement coverage trend.

