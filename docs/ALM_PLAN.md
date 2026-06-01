# ALM_PLAN

| Field | Value |
| ----- | ----- |
| **Version** | 0.2.1 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 0.2.0 (Git-first ALM baseline with governance gates) |

## Purpose

Define the Application Lifecycle Management (ALM) baseline for planning,
building, validating, and releasing changes in this repository.

The ALM model is GitHub-native and optimized for a governance-first platform
where deliverables include requirements, architecture, agent prompts, controls,
and IaC artifacts.

## Source Baseline

This plan aligns to:
1. docs/PRD.md
2. docs/ARCHITECTURE.md
3. docs/SECURITY.md
4. docs/COMPLIANCE.md
5. docs/TEST.md
6. AGENTS.md

## Branching and Release Strategy

### Branching Model

1. Main is the long-lived integration branch and production truth.
2. Feature work is delivered via short-lived branches created from issues.
3. Copilot-generated branches are treated as standard feature branches and are
	reviewed under the same quality and governance controls.
4. Merged and stale branches are cleaned up regularly.

### Release Strategy

1. Release readiness is evidence-based and gate-driven.
2. Every release candidate must provide requirement traceability and validation evidence.
3. Breaking governance or compliance changes require explicit review sign-off.

### Commit and PR Conventions

1. Conventional Commit format is mandatory.
2. PRs must use the repository PR output contract.
3. Every changed artifact must reference impacted requirement IDs and risk statements.

## CI and CD

### CI Baseline (Current)

1. Markdown lint for all documentation changes.
2. Link validation for docs, sprint, and .github documentation.
3. Bicep build/validation for infrastructure changes.
4. Golden-task validation for agent prompt and behavior changes.
5. Security and secret scanning for repository hygiene.

### CD / Promotion Baseline

1. This repository does not host a runtime platform to deploy.
2. CD primarily means artifact promotion and control progression:
	DEV to SIT to PROD readiness for customer-targeted outputs (for example IaC packs).
3. Any deploy/delete side-effect action must follow explicit human approval gates.

### Workflow Pattern

1. Open issue with objective, lane scope, and requirement IDs.
2. Create branch and implement scoped changes.
3. Open draft PR with initial validation evidence.
4. Pass required gates (docs, tests, security, traceability).
5. Complete review and merge into main.
6. Tag release milestone or sprint outcome as needed.

## Environments

### Repository ALM Environments

The repository lifecycle uses policy and quality gates rather than hosted app
environments:

1. Draft state: issue and draft PR.
2. Validation state: quality gates and evidence completion.
3. Approval state: reviewer sign-off and compliance/security confirmations.
4. Released state: merged into main with traceable history.

### Target Solution Environment Progression

For customer-facing solution outputs, use:
1. DEV: fast feedback and contract validation.
2. SIT: integration, NFR, and control validation.
3. PROD: controlled release with approved evidence pack.

## Governance and Control Gates

### Mandatory Gate Set

1. Requirement traceability gate: changed artifacts map to FR/NFR IDs.
2. Security gate: no secret leakage and required security controls preserved.
3. Compliance gate: control mappings and evidence impact are updated.
4. Quality gate: required test and lint checks pass.
5. Change scope gate: PR scope matches approved issue scope.

### Sensitive Change Approval

Changes affecting these files or areas require explicit elevated review:
1. AGENTS.md
2. .github/copilot/mcp.json
3. .github/CODEOWNERS
4. docs/adr/*
5. security-critical workflow and policy definitions

## Traceability and Evidence Management

### Required Evidence per PR

1. Validation commands and result summary.
2. Requirement IDs impacted and coverage note.
3. Compliance and security impact statement.
4. Residual risks and mitigation plan.

### Evidence Persistence

1. GitHub issues, PRs, comments, and commit history are primary audit artifacts.
2. Sprint documents capture milestone-level quality and delivery outcomes.
3. Control evidence references must remain linked to changed artifacts.

## ALM Metrics and KPI Baseline

Track minimum ALM KPIs:
1. PR lead time (issue open to merge).
2. Change failure rate (hotfixes or rollback-triggering defects).
3. Gate pass rate at first PR submission.
4. Requirement traceability completeness ratio.
5. Open critical risk count by sprint.

## Initial Implementation Backlog

1. Add explicit CI workflows for markdown lint and link checks if missing.
2. Add golden-task replay workflow for agent changes.
3. Add release-readiness checklist artifact under docs/operations.
4. Add KPI dashboard update cadence into sprint reporting.
