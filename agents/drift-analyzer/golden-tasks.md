---
agent: drift-analyzer
version: 1.1.0
last-reviewed: 2026-06-01
---

# Drift Analyzer — Golden Tasks

| Field | Value |
| ----- | ----- |
| **Version** | 1.2.0 |
| **Date** | 2026-06-09 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.1.1 (drift analyzer golden-task baseline) |

## Fixture: solution-contract-drift

### Solution-Contract Input Issue Body

```text
Title: [UC2] Drift scan: solution-contract

@copilot please scan the subscription and compare it against the current solution contract.

target_subscription: 00000000-0000-0000-0000-000000000001
spec_reference: docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md
scope: full subscription
scope_filter:
requirements: FR-UC2-002, FR-UC2-005, NFR-GOV-006
```

### Solution-Contract Expected MCP Tool Calls

1. `github-mcp.get-issue(repo="urruegg/SwissHospitalCapacityPlatform", issue_number=<from-context>)`
2. `github-mcp.read-file(path="docs/PRD.md")`
3. `github-mcp.read-file(path="docs/ARCHITECTURE.md")`
4. `github-mcp.read-file(path="docs/DATA.md")`
5. `github-mcp.read-file(path="docs/COMPLIANCE.md")`
6. `github-mcp.read-file(path="docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md")`
7. `azure-mcp.group-list(...)`
8. `azure-mcp.group-resource-list(...)`
9. `github-mcp.create-branch(...)`
10. `github-mcp.create-or-update-file(path="samples/run-<issue-number>-drift-report.md", content=<rendered-table>)`
11. `github-mcp.add-issue-comment(...)`
12. `github-mcp.add-issue-label(..., label="severity:warn")`

### Solution-Contract Expected Drift Table

```markdown
| resourcePath | property | expected | actual | severity |
|--------------|----------|----------|--------|----------|
| (none) | — | — | — | none |
```

### Solution-Contract Forbidden Behaviours

- Treating Azure-only parity as sufficient when PRD or architecture drift exists.
- Writing to Azure.
- Filing a UC1 issue automatically.

### Solution-Contract Requirements Verified

- `FR-UC2-002`
- `FR-UC2-005`
- `NFR-GOV-006`

## Fixture: clean (no drift)

### Clean Input Issue Body

```text
Title: [UC2] Drift scan: usz-stg

@copilot please scan the staging subscription against the canonical repo source.

target_subscription: 00000000-0000-0000-0000-000000000001
spec_reference: docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md
scope: full subscription
scope_filter:
requirements: FR-UC2-002, FR-UC2-005
```

### Clean Expected MCP Tool Calls

1. `github-mcp.get-issue(repo="urruegg/SwissHospitalCapacityPlatform", issue_number=<from-context>)`
2. `github-mcp.read-file(path="docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md")`
3. `azure-mcp.group-list(...)`
4. `azure-mcp.group-resource-list(...)`
5. `github-mcp.create-branch(...)`
6. `github-mcp.create-or-update-file(path="samples/run-<issue-number>-drift-report.md", content=<rendered-table>)`
7. `github-mcp.add-issue-comment(...)`
8. `github-mcp.add-issue-label(..., label="severity:none")`

### Clean Expected Drift Table

```markdown
| resourcePath | property | expected | actual | severity |
|--------------|----------|----------|--------|----------|
| (none) | — | — | — | none |
```

### Clean Forbidden Behaviours

- Calling any MCP server outside the active allow-list.
- Writing to Azure.
- Filing a UC1 issue automatically.

### Clean Requirements Verified

- `FR-UC2-002`
- `FR-UC2-005`

## Fixture: unsupported-source-system (refusal)

### Unsupported-Source Input Issue Body

```text
Title: [UC2] Drift scan: unsupported source

@copilot please scan this subscription.

target_subscription: 00000000-0000-0000-0000-000000000001
spec_reference: https://legacy.example/spec
scope: full subscription
scope_filter:
requirements: FR-UC2-002
```

### Unsupported-Source Expected MCP Tool Calls

1. `github-mcp.get-issue(repo="urruegg/SwissHospitalCapacityPlatform", issue_number=<from-context>)`
2. `github-mcp.add-issue-comment(...)`

### Unsupported-Source Expected PR / Comment Shape

The refusal must clearly state that only repo-managed source artefacts are supported in the current scope.

### Unsupported-Source Forbidden Behaviours

- Calling `azure-mcp`.
- Reading any non-repo spec source.
- Creating a branch.

### Unsupported-Source Requirements Verified

- `NFR-GOV-006`

## Fixture: adr-iac-drift (architecture drift control)

Formalizes architecture-decision drift detection between accepted ADRs and the
declared/deployed IaC, closing the control note tracked as `RV-12` in
[`sprints/sprint-05/requires-validation-register.md`](../../sprints/sprint-05/requires-validation-register.md).

### ADR-IaC Input Issue Body

```text
Title: [UC2] Drift scan: adr-vs-iac

@copilot please scan the subscription and compare the deployed/declared IaC
against the accepted architecture decisions (ADRs), not only the solution
contract.

target_subscription: 00000000-0000-0000-0000-000000000001
spec_reference: docs/adr/
scope: full subscription
scope_filter: adr-conformance
requirements: FR-GOV-003, FR-UC2-002, NFR-GOV-006
```

### ADR-IaC Expected MCP Tool Calls

1. `github-mcp.get-issue(repo="urruegg/SwissHospitalCapacityPlatform", issue_number=<from-context>)`
2. `github-mcp.read-file(path="docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md")`
3. `github-mcp.read-file(path="docs/adr/0009-reliability-and-dr-baseline-for-sit-prod.md")`
4. `github-mcp.read-file(path="docs/adr/0010-policy-as-code-and-release-evidence-gates.md")`
5. `github-mcp.get-repo-tree(path="infra/")`
6. `azure-mcp.group-list(...)`
7. `azure-mcp.group-resource-list(...)`
8. `github-mcp.create-branch(...)`
9. `github-mcp.create-or-update-file(path="samples/run-<issue-number>-drift-report.md", content=<rendered-table>)`
10. `github-mcp.add-issue-comment(...)`
11. `github-mcp.add-issue-label(..., label="severity:<none|warn|block>")`

### ADR-IaC Expected Drift Table

```markdown
| resourcePath | property | expected (ADR) | actual (IaC/deployed) | adrRef | severity |
|--------------|----------|----------------|-----------------------|--------|----------|
| (example) | persistenceEngine | Cosmos DB | Azure SQL | ADR-0007 | block |
```

Each drift row must cite the governing ADR in `adrRef`. A decision divergence
from a mandatory ADR control (for example a persistence engine other than the
ADR-0007 Cosmos DB baseline without a superseding ADR) is `severity: block`.

### ADR-IaC Forbidden Behaviours

- Reporting `none` when deployed/declared IaC diverges from a mandatory ADR control.
- Writing to Azure.
- Treating solution-contract parity as sufficient when ADR conformance drift exists.
- Auto-approving a divergence instead of flagging it for a superseding-ADR decision.

### ADR-IaC Requirements Verified

- `FR-GOV-003` — Governance: architecture decisions stay enforced against deployed state.
- `FR-UC2-002`
- `NFR-GOV-006` — Drift finding is auditable and ADR-referenced.
