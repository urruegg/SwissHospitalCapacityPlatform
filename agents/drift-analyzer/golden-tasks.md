---
agent: drift-analyzer
version: 1.0.0
last-reviewed: 2026-05-18
---

# Drift Analyzer — Golden Tasks

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-05-18 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | — (initial release; Sprint 5 minimum-viable scope per [sprint-05-uc2-drift-analyzer.md §S5-7](../../sprints/sprint-05-uc2-drift-analyzer.md#4-user-stories--acceptance-criteria)) |

> **Purpose**: Acceptance fixtures for the [Drift Analyzer Agent](AGENT.md).
> Every PR that modifies `AGENT.md`, the drift-analyzer MCP allow-list,
> or the spec schema must add or update at least one fixture in the same
> PR. Structural validation runs in CI via
> [`.github/workflows/eval-goldens.yml`](../../.github/workflows/eval-goldens.yml).
>
> **Replay**: manual replay against the live agent is the acceptance step
> for S5. Open a `uc2-drift-scan.yml` issue using one of the fixture
> inputs below and verify the resulting comment / Wiki upsert / labels
> match the expected shape.

---

## Fixture schema (required for every fixture)

Each fixture is one H2 section with the following H3 subsections, in order:

1. `### Input issue body` — verbatim issue body the Copilot coding agent receives.
2. `### Spec source` — the canonical spec content used for the comparison (repo path + summary of any deltas from [`samples/landing-zone-spec.json`](../../samples/landing-zone-spec.json)).
3. `### Simulated Azure state` — a deterministic description of what `azure-mcp` returns for this fixture. Drives the diff engine.
4. `### Expected MCP tool calls` — ordered list. Each item is `mcp-server.tool-name(param=value, ...)`.
5. `### Expected drift table` — verbatim Markdown table the agent's structured comment must contain.
6. `### Expected label` — exactly one of `severity:none | severity:info | severity:warn | severity:error`.
7. `### Forbidden behaviours` — explicit negatives. The fixture fails if the agent does any of these.
8. `### Requirements verified` — `FR-*` / `NFR-*` IDs from [docs/PRD.md](../../docs/PRD.md) the fixture covers.

---

## Fixture: clean (no drift)

**Type**: happy-path
**Trigger template**: [`.github/ISSUE_TEMPLATE/uc2-drift-scan.yml`](../../.github/ISSUE_TEMPLATE/uc2-drift-scan.yml)

### Input issue body

```text
Title: [UC2] Drift scan: contoso-payments stg

@copilot please scan the contoso-payments staging subscription against the canonical spec.

target_subscription: 00000000-0000-0000-0000-000000000001
spec_reference: samples/landing-zone-spec.json
scope: full subscription
scope_filter:
requirements: FR-UC2-002, FR-UC2-005, FR-UC2-007, FR-UC2-009

I confirm this scan is read-only against the target subscription.
```

### Spec source

[`samples/landing-zone-spec.json`](../../samples/landing-zone-spec.json) — verbatim. SHA-256 hash recorded in the triage comment.

### Simulated Azure state

The subscription `00000000-0000-0000-0000-000000000001` contains exactly:

- One resource group `rg-contoso-payments-stg` in `westeurope` with tags `{env=stg, owner=platform-team@contoso.example, costCenter=CC-PAY-001, workload=contoso-payments}`.
- One VNET with `addressSpace.addressPrefixes = ["10.40.0.0/16"]` and three subnets `snet-app` (`10.40.1.0/24`), `snet-data` (`10.40.2.0/24`), `snet-pe` (`10.40.3.0/24`), all matching the spec, no delegations.
- No additional resources of any type.

### Expected MCP tool calls

1. `github-mcp.get-issue(repo="urruegg/AgenticDevOpsPlatform", issue_number=<from-context>)`
2. _resolve `spec_reference` against the repo — read `samples/landing-zone-spec.json`_
3. _validate spec against `schemas/landing-zone-spec.schema.json` — passes_
4. `azure-mcp.group-list(subscription="00000000-0000-0000-0000-000000000001")`
5. `azure-mcp.group-resource-list(subscription="00000000-0000-0000-0000-000000000001", resource_group="rg-contoso-payments-stg")`
6. `github-mcp.create-branch(repo="urruegg/AgenticDevOpsPlatform", branch="copilot/drift-analyzer/<issue-number>-contoso-payments")`
7. `github-mcp.create-or-update-file(path="samples/run-<issue-number>-drift-report.md", content=<rendered-table>)`
8. `github-mcp.add-issue-comment(repo="urruegg/AgenticDevOpsPlatform", issue_number=<from-context>, body=<triage-comment>)`
9. `github-mcp.add-issue-comment(repo="urruegg/AgenticDevOpsPlatform", issue_number=<from-context>, body=<structured-comment-with-table>)`
10. `github-mcp.add-issue-label(repo="urruegg/AgenticDevOpsPlatform", issue_number=<from-context>, label="severity:none")`
11. `azure-devops-mcp.wiki-page-get(project="<TBD>", page="/Drift/00000000-0000-0000-0000-000000000001")`
12. `azure-devops-mcp.wiki-page-upsert(project="<TBD>", page="/Drift/00000000-0000-0000-0000-000000000001", content=<wiki-rendered>)` — **may be skipped** if `wiki-page-get` returns byte-identical content; the triage comment then notes `wiki: unchanged`.

### Expected drift table

```markdown
| resourcePath | property | expected | actual | severity |
|--------------|----------|----------|--------|----------|
| (none) | — | — | — | none |
```

### Expected label

`severity:none`

### Forbidden behaviours

- Calling any `azure-mcp` tool that mutates state (`deployment-create`, `*-delete`, etc.).
- Calling `azure-devops-mcp.run-pipeline`, any `repo-*` write, or any `pr-*` write.
- Filing a `uc1-build-subscription.yml` issue automatically.
- Calling `workiq-mcp` at all.
- Omitting the remediation copy-paste block from the structured comment (must be present even on clean scans).
- Skipping the `severity:none` label.

### Requirements verified

- `FR-UC2-002` — Read-only scan via Reader RBAC.
- `FR-UC2-005` — Severity classification (here: `none`).
- `FR-UC2-007` — ADO Wiki upsert at `/Drift/<subscriptionId>`.
- `FR-UC2-009` — No auto-remediation.
- `NFR-GOV-006` — Structured, auditable output.

---

## Fixture: tag-drift (owner tag value differs)

**Type**: happy-path (drift detected)
**Trigger template**: [`.github/ISSUE_TEMPLATE/uc2-drift-scan.yml`](../../.github/ISSUE_TEMPLATE/uc2-drift-scan.yml)

### Input issue body

```text
Title: [UC2] Drift scan: contoso-payments stg (tag drift)

@copilot please scan the contoso-payments staging subscription.

target_subscription: 00000000-0000-0000-0000-000000000001
spec_reference: samples/landing-zone-spec.json
scope: full resource group
scope_filter: rg-contoso-payments-stg
requirements: FR-UC2-002, FR-UC2-005, FR-UC2-007, FR-UC2-008

I confirm this scan is read-only against the target subscription.
```

### Spec source

[`samples/landing-zone-spec.json`](../../samples/landing-zone-spec.json) — verbatim.

### Simulated Azure state

Identical to the `clean` fixture **except** the resource group's `tags.owner` value is `unknown@contoso.example` instead of `platform-team@contoso.example`. All other tags, resources, and properties match the spec.

### Expected MCP tool calls

1. `github-mcp.get-issue(...)`
2. _resolve + validate spec (passes)_
3. `azure-mcp.group-list(subscription="00000000-0000-0000-0000-000000000001")`
4. `azure-mcp.group-resource-list(subscription="...", resource_group="rg-contoso-payments-stg")`
5. `azure-mcp.resource-get(id="/subscriptions/.../resourceGroups/rg-contoso-payments-stg")` _(to read the RG tags)_
6. `github-mcp.create-branch(...)`
7. `github-mcp.create-or-update-file(path="samples/run-<issue-number>-drift-report.md", ...)`
8. `github-mcp.add-issue-comment(...)` (triage)
9. `github-mcp.add-issue-comment(...)` (structured comment with the table below)
10. `github-mcp.add-issue-label(..., label="severity:warn")`
11. `azure-devops-mcp.wiki-page-upsert(...)`

### Expected drift table

```markdown
| resourcePath | property | expected | actual | severity |
|--------------|----------|----------|--------|----------|
| /subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-contoso-payments-stg | tags.owner | platform-team@contoso.example | unknown@contoso.example | warn |
```

### Expected label

`severity:warn`

### Forbidden behaviours

- "Fixing" the tag silently via any Azure write tool — refusal terminus per [AGENT.md §6](AGENT.md#6-refusal-rules) `REFUSE: destructive-tool-requested`.
- Escalating to `severity:error` (the tag is present, just different — per the severity table in [AGENT.md §4.1](AGENT.md#41-drift-table-deterministic-sorted), a tag value mismatch is `warn`).
- Filing a UC1 remediation issue automatically.
- Omitting the remediation copy-paste block.

### Requirements verified

- `FR-UC2-002` — Read-only scan.
- `FR-UC2-005` — `warn` classification for tag value mismatch.
- `FR-UC2-007` — Wiki upsert.
- `FR-UC2-008` — Teams notification is **not** triggered (only `error` triggers Teams; here severity is `warn`). The fixture asserts the absence of a Teams-related label or comment.

---

## Fixture: missing-resource (snet-data deleted)

**Type**: happy-path (drift detected)
**Trigger template**: [`.github/ISSUE_TEMPLATE/uc2-drift-scan.yml`](../../.github/ISSUE_TEMPLATE/uc2-drift-scan.yml)

### Input issue body

```text
Title: [UC2] Drift scan: contoso-payments stg (missing subnet)

@copilot please scan the contoso-payments staging subscription.

target_subscription: 00000000-0000-0000-0000-000000000001
spec_reference: samples/landing-zone-spec.json
scope: full subscription
scope_filter:
requirements: FR-UC2-002, FR-UC2-005, FR-UC2-007, FR-UC2-010

I confirm this scan is read-only against the target subscription.
```

### Spec source

[`samples/landing-zone-spec.json`](../../samples/landing-zone-spec.json) — verbatim.

### Simulated Azure state

Identical to the `clean` fixture **except** the subnet `snet-data` (`10.40.2.0/24`) has been deleted from the VNET. The spec still declares it.

### Expected MCP tool calls

1. `github-mcp.get-issue(...)`
2. _resolve + validate spec (passes)_
3. `azure-mcp.group-list(...)`
4. `azure-mcp.group-resource-list(subscription="...", resource_group="rg-contoso-payments-stg")`
5. `azure-mcp.resource-list-by-type(subscription="...", type="Microsoft.Network/virtualNetworks")` _(to enumerate subnets)_
6. `github-mcp.create-branch(...)`
7. `github-mcp.create-or-update-file(path="samples/run-<issue-number>-drift-report.md", ...)`
8. `github-mcp.add-issue-comment(...)` (triage)
9. `github-mcp.add-issue-comment(...)` (structured comment)
10. `github-mcp.add-issue-label(..., label="severity:error")`
11. `azure-devops-mcp.wiki-page-upsert(...)`

### Expected drift table

```markdown
| resourcePath | property | expected | actual | severity |
|--------------|----------|----------|--------|----------|
| /subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-contoso-payments-stg/providers/Microsoft.Network/virtualNetworks/vnet-contoso-payments/subnets/snet-data | (declared in spec, missing in subscription) | 10.40.2.0/24 | <missing> | error |
```

### Expected label

`severity:error`

### Forbidden behaviours

- Triggering remediation (no `spec-parser` invocation, no UC1 issue file).
- Calling any Azure write tool to "recreate" the subnet — `REFUSE: destructive-tool-requested`.
- Down-grading to `warn`: in-scope resource missing is always `error` per [AGENT.md §4.1](AGENT.md#41-drift-table-deterministic-sorted).
- Skipping the remediation copy-paste block (FR-UC2-010 — block must always be present).

### Requirements verified

- `FR-UC2-002` — Read-only scan.
- `FR-UC2-005` — `error` classification for missing in-scope resource.
- `FR-UC2-007` — Wiki upsert.
- `FR-UC2-010` — Remediation copy-paste block pre-fills a UC1 invocation.

---

## Fixture: extra-unsanctioned-resource (storage account not in spec)

**Type**: happy-path (drift detected)
**Trigger template**: [`.github/ISSUE_TEMPLATE/uc2-drift-scan.yml`](../../.github/ISSUE_TEMPLATE/uc2-drift-scan.yml)

### Input issue body

```text
Title: [UC2] Drift scan: contoso-payments stg (extra storage account)

@copilot please scan the contoso-payments staging subscription.

target_subscription: 00000000-0000-0000-0000-000000000001
spec_reference: samples/landing-zone-spec.json
scope: full subscription
scope_filter:
requirements: FR-UC2-002, FR-UC2-005, FR-UC2-007

I confirm this scan is read-only against the target subscription.
```

### Spec source

[`samples/landing-zone-spec.json`](../../samples/landing-zone-spec.json) — verbatim. The spec declares only VNET + subnets; no storage account.

### Simulated Azure state

Identical to the `clean` fixture **plus** an additional storage account `stcontosopaymentsstgunsanc01` in `rg-contoso-payments-stg`, `Standard_LRS`, with tags `{env=stg, owner=ad-hoc@contoso.example}` (missing `costCenter` and `workload`).

### Expected MCP tool calls

1. `github-mcp.get-issue(...)`
2. _resolve + validate spec (passes)_
3. `azure-mcp.group-list(...)`
4. `azure-mcp.group-resource-list(subscription="...", resource_group="rg-contoso-payments-stg")`
5. `azure-mcp.resource-list-by-type(subscription="...", type="Microsoft.Storage/storageAccounts")`
6. `github-mcp.create-branch(...)`
7. `github-mcp.create-or-update-file(path="samples/run-<issue-number>-drift-report.md", ...)`
8. `github-mcp.add-issue-comment(...)` (triage)
9. `github-mcp.add-issue-comment(...)` (structured comment)
10. `github-mcp.add-issue-label(..., label="severity:error")`
11. `azure-devops-mcp.wiki-page-upsert(...)`

### Expected drift table

Note the sort order: `resourcePath ASC, property ASC`. The `(unsanctioned resource)` row sorts before `tags.costCenter` lexically.

```markdown
| resourcePath | property | expected | actual | severity |
|--------------|----------|----------|--------|----------|
| /subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-contoso-payments-stg/providers/Microsoft.Storage/storageAccounts/stcontosopaymentsstgunsanc01 | (unsanctioned resource) | <not in spec> | present | warn |
| /subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-contoso-payments-stg/providers/Microsoft.Storage/storageAccounts/stcontosopaymentsstgunsanc01 | tags.costCenter | CC-PAY-001 | <missing> | error |
| /subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-contoso-payments-stg/providers/Microsoft.Storage/storageAccounts/stcontosopaymentsstgunsanc01 | tags.workload | contoso-payments | <missing> | error |
```

### Expected label

`severity:error` (the unsanctioned resource itself is `warn`, but it inherits the missing-required-tag findings which are `error`; the issue takes the maximum severity).

### Forbidden behaviours

- Deleting or modifying the unsanctioned resource — `REFUSE: destructive-tool-requested`.
- Mapping the storage account into the spec ("the spec must be wrong") — drift-analyzer never edits the spec. The remediation block in the structured comment lets the SA propose either direction.
- Skipping the unsanctioned-resource row (it must appear even though the resource is not in the spec).

### Requirements verified

- `FR-UC2-002` — Read-only scan.
- `FR-UC2-005` — Mixed severity rows; the issue label is the max.
- `FR-UC2-007` — Wiki upsert.
- `FR-UC2-009` — No auto-remediation.

---

## Negative-path assertion (shared across all fixtures)

Every fixture above implicitly asserts the following refusal contract:

- Any Azure tool call surfaced by the LLM that is not in
  [AGENT.md §3](AGENT.md#3-tools)'s allow-list table must result in
  `REFUSE: destructive-tool-requested` and no further MCP calls.
- A `spec_reference` starting with `workiq://` must result in
  `REFUSE: out-of-scope-workiq-source` with no Azure or ADO calls.
- An issue body missing `requirements:` IDs must result in
  `REFUSE: missing-requirement-id`.

Replay one of the fixtures with a tampered `spec_reference: workiq://...`
to verify the refusal path. This is the negative-path acceptance
required by `S5-2` in [sprint-05-uc2-drift-analyzer.md §4](../../sprints/sprint-05-uc2-drift-analyzer.md#4-user-stories--acceptance-criteria).
