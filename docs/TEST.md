# TEST

| Field | Value |
| ----- | ----- |
| **Version** | 0.4.0 |
| **Date** | 2026-06-09 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 0.3.0 (Sprint 05 evidence-automation checkpoints) |

## Purpose

Define the baseline quality strategy, quality gates, and evidence model for the
Swiss Hospital Capacity Platform repository.

This plan is designed for the current repository shape where delivery is
governance-first (documents, agent prompts, workflows, and IaC outputs), with
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
| Agent control lane | agents/*/AGENT.md and golden tasks | Golden-task replay, refusal and side-effect checks |
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

Required for any change under docs/, sprints/, AGENTS.md, or README.md.

1. Markdown lint passes.
2. Link check passes.
3. Version header is updated per document versioning rules.
4. Requirement and control traceability remains explicit for changed scope.

### Gate 2: Agent Change Safety

Required for any change under agents/ or AGENTS.md.

1. At least one happy-path golden task validated.
2. At least one failure-mode/refusal golden task validated.
3. Side-effect ceiling remains unchanged unless explicitly approved.
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
npx --yes markdown-link-check docs/**/*.md sprints/*.md .github/*.md
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
[`sprints/sprint-05/pr-evidence-checklist.md`](../sprints/sprint-05/pr-evidence-checklist.md):

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
[`sprints/sprint-05/phase-2-policy-gate.md`](../sprints/sprint-05/phase-2-policy-gate.md).

## Defect and Risk Handling

1. Defects are logged as GitHub issues with lane, severity, and requirement tags.
2. Critical defects affecting compliance, security, or data integrity block release.
3. Waivers require explicit owner, expiration date, and mitigation plan.

## MVP Baseline Quality Targets

1. 100 percent pass on markdown and link checks for changed docs.
2. 100 percent pass on required golden tasks for changed agents.
3. Zero unresolved high-severity security/compliance test findings at release gate.
4. Explicit requirement traceability for all changed design and governance artifacts.

## Next Steps

1. Add lane-local test commands as soon as data-platform, ai-models, apps, and
	integrations code lanes are populated.
2. Add automated golden-task replay workflow in .github/workflows.
3. Add release dashboard for gate pass rates and requirement coverage trend.
