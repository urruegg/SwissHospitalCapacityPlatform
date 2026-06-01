---
agent: drift-analyzer
version: 1.1.0
last-reviewed: 2026-06-01
---

# Drift Analyzer — Golden Tasks

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (initial release; Sprint 5 minimum-viable scope per [sprint-05-uc2-drift-analyzer.md §S5-7](../../sprints/sprint-05-uc2-drift-analyzer.md#4-user-stories--acceptance-criteria)) |

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
