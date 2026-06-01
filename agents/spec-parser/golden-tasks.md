---
agent: spec-parser
version: 1.1.0
last-reviewed: 2026-06-01
---

# Spec Parser — Golden Tasks

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (initial release; Sprint 2 MVP per [sprint-02-uc1-spec-parser-happy-path.md §S2-7](../../sprints/sprint-02-uc1-spec-parser-happy-path.md#4-user-stories--acceptance-criteria)) |

## Fixture: happy-path (repo markdown, plan-only)

### Happy-Path Input Issue Body

```text
Title: [UC1] Build subscription: usz-stg

@copilot please plan the landing zone.

spec_sources:
docs/PRD.md
docs/ARCHITECTURE.md
docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md
docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md
target_subscription: 00000000-0000-0000-0000-000000000001
stage: plan-only
requirements: FR-UC1-002, FR-UC1-004, FR-UC1-005
```

### Happy-Path Expected MCP Tool Calls

1. `github-mcp.get-issue(repo="urruegg/SwissHospitalCapacityPlatform", issue_number=<from-context>)`
2. `github-mcp.get-repo-tree(repo="urruegg/SwissHospitalCapacityPlatform")`
3. `github-mcp.read-file(path="docs/PRD.md")`
4. `github-mcp.read-file(path="docs/ARCHITECTURE.md")`
5. `github-mcp.read-file(path="docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md")`
6. `github-mcp.read-file(path="docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md")`
7. `github-mcp.create-branch(repo="urruegg/SwissHospitalCapacityPlatform", branch="copilot/spec-parser/<issue-number>-usz-stg")`
8. `github-mcp.create-or-update-file(path="infra/landing-zone/parameters/stg.bicepparam", content=<deterministic render>)`
9. `github-mcp.create-or-update-file(path="samples/run-<issue-number>-source-bundle.md", content=<source summary>)`
10. `azure-mcp.bicep-build(file="infra/landing-zone/main.bicep")`
11. `azure-mcp.deployment-what-if(...)`
12. `github-mcp.create-pull-request(...)`
13. `github-mcp.add-issue-comment(...)`

### Happy-Path Expected PR / Comment Shape

The PR and comment must state that the plan was derived from repo-managed markdown under `docs/` and `docs/specs/`, include the source bundle hash, and explicitly state that `stage=plan-only` means no apply step follows.

### Happy-Path Forbidden Behaviours

- Calling any MCP server outside the active allow-list.
- Reading spec input from outside `docs/`, `docs/specs/`, `samples/`, or committed UC1 artefacts.
- Calling `azure-mcp.deployment-create` when the issue is `plan-only`.

### Happy-Path Requirements Verified

- `FR-UC1-002`
- `FR-UC1-004`
- `FR-UC1-005`

## Fixture: missing-source-file (refusal)

### Missing-Source Input Issue Body

```text
Title: [UC1] Build subscription: missing-source

@copilot please plan the landing zone.

spec_sources:
docs/specs/does-not-exist.md
target_subscription: 00000000-0000-0000-0000-000000000001
stage: plan-only
requirements: FR-UC1-004
```

### Missing-Source Expected MCP Tool Calls

1. `github-mcp.get-issue(repo="urruegg/SwissHospitalCapacityPlatform", issue_number=<from-context>)`
2. `github-mcp.get-repo-tree(repo="urruegg/SwissHospitalCapacityPlatform")`
3. `github-mcp.add-issue-comment(...)`

### Missing-Source Expected PR / Comment Shape

The refusal must start with `REFUSE: spec-validation-failed` and identify the missing repo path.

### Missing-Source Forbidden Behaviours

- Creating a branch or PR.
- Calling `azure-mcp`.
- Inventing missing source content.

### Missing-Source Requirements Verified

- `FR-UC1-004`
- `NFR-GOV-006`
