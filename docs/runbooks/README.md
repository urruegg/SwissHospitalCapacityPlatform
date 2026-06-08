# Runbooks — Operational Procedures

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-08 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | N/A |

## Purpose

This folder contains operator-safe runbooks for repeatable operational tasks on the Swiss Hospital Capacity Platform repository. Each runbook provides step-by-step procedures, expected outcomes, and troubleshooting guidance.

Runbooks are distinct from application logic and infrastructure code — they capture external integrations, data intake processes, and governance workflows.

## Runbook Index

| Runbook | Scope | Operator | Outcome |
| ------- | ----- | -------- | ------- |
| [Work IQ Teams Transcript Intake](work-iq-teams-transcript-intake.md) | Read Microsoft Teams meetings with transcripts and export raw content to repository | `urruegg@microsoft.com` | Raw transcript file placed in `docs/reviews/raw/` for downstream review-session-agent processing |

## Runbook Lifecycle

1. **Authoring**: Create runbook from template below.
2. **Review**: Peer review for safety, compliance, and clarity.
3. **Testing**: Operator executes runbook once and validates expected outcomes.
4. **Publication**: Merge to `main` after review approval.
5. **Updates**: Bump version when procedure, outcomes, or guardrails change.

## Runbook Template

When creating a new runbook, use this structure:

```markdown
# <Runbook Title>

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | <YYYY-MM-DD> |
| **Author** | <Operator Name> |
| **Status** | Reviewed |
| **Previous Version** | N/A |

## Purpose

One-sentence summary of what the runbook enables.

## Scope

### In scope
- Task 1
- Task 2

### Out of scope
- Excluded area 1
- Excluded area 2

## Prerequisites

Mandatory prerequisites:
1. Prerequisite A
2. Prerequisite B

Repository prerequisites already in place:
1. Config or artefact A
2. Config or artefact B

## Security and Compliance Guardrails

1. Guardrail A
2. Guardrail B

## Operational Procedure

### Step 1: <Step title>

Description and action.

Expected outcome:
1. Outcome indicator A
2. Outcome indicator B

### Step 2: <Step title>

Description and action.

Expected outcome:
1. Outcome indicator A

## Handoff to Next Process

After this runbook is complete, proceed with:
- Next workflow or agent process

## Troubleshooting

If symptom:
1. Investigation step
2. Mitigation step

## Evidence Checklist

Before closing this runbook execution:
- [ ] Evidence item 1
- [ ] Evidence item 2
```

## Governance Rules

1. Every runbook must have a purpose, scope, prerequisites, and evidence checklist.
2. Runbooks should be operator-safe; avoid requiring code edits or secrets.
3. Runbooks should reference repository artefacts and agent definitions.
4. Runbook versions follow Semantic Versioning (X.Y.Z); bump when procedure changes.
5. CODEOWNERS approval is required for new runbooks or runbook updates that affect repository governance.

## Linked Documentation

- [docs/OPERATIONS.md](../OPERATIONS.md) — Operating model and run governance
- [agents/review-session-agent/intake-strategy.md](../../agents/review-session-agent/intake-strategy.md) — Review workflow intake pipeline
- [docs/reviews/README.md](../reviews/README.md) — Review artefact conventions
