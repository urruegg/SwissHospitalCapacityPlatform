---
agent: spec-parser
version: 1.0.0
last-reviewed: 2026-05-25
---

# Spec Parser — Golden Tasks

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-05-25 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | — (initial release; Sprint 2 MVP per [sprint-02-uc1-spec-parser-happy-path.md §S2-7](../../sprints/sprint-02-uc1-spec-parser-happy-path.md#4-user-stories--acceptance-criteria)) |

> **Purpose**: Acceptance fixtures for the [Spec Parser Agent](AGENT.md).
> Every PR that modifies `AGENT.md`, the spec-parser MCP allow-list, the
> JSON schema, or any file under [`infra/landing-zone/`](../../infra/landing-zone/)
> must add or update at least one fixture in the same PR. Structural
> validation runs in CI via
> [`.github/workflows/eval-goldens.yml`](../../.github/workflows/eval-goldens.yml).
>
> **Replay**: manual replay against the live agent is the acceptance step
> for S2. Open a `uc1-build-subscription.yml` issue using one of the
> fixture inputs below and verify the resulting comment / PR matches the
> expected shape.

---

## Fixture schema (required for every fixture)

Each fixture is one H2 section with the following H3 subsections, in order:

1. `### Input issue body` — verbatim issue body the Copilot coding agent receives.
2. `### Expected MCP tool calls` — ordered list. Each item is `mcp-server.tool-name(param=value, ...)`. Sets (unordered) are allowed when explicitly noted as `(set)`.
3. `### Expected PR / comment shape` — Markdown excerpt the agent's output must contain (substring match, not exact).
4. `### Forbidden behaviours` — explicit negatives. The fixture fails if the agent does any of these.
5. `### Requirements verified` — `FR-*` / `NFR-*` IDs from [docs/PRD.md](../../docs/PRD.md) the fixture covers.

---

## Fixture: happy-path (WorkIQ spec, plan-only)

**Type**: happy-path
**Trigger template**: [`.github/ISSUE_TEMPLATE/uc1-build-subscription.yml`](../../.github/ISSUE_TEMPLATE/uc1-build-subscription.yml)

### Input issue body

```text
Title: [UC1] Build subscription: contoso-payments stg

@copilot please plan the landing zone for contoso-payments staging.

workiq_spec_id: workiq://specs/contoso-payments-stg/v1
target_subscription: 00000000-0000-0000-0000-000000000001
target_ado_project: contoso/platform
stage: plan-only
requirements: FR-UC1-002, FR-UC1-004, FR-UC1-005, FR-UC1-006, FR-UC1-007, FR-PLT-002, FR-PLT-003

I confirm this is a staging-only run.
```

### Expected MCP tool calls

1. `github-mcp.get-issue(repo="urruegg/AgenticDevOpsPlatform", issue_number=<from-context>)`
2. `workiq-mcp.get-spec(id="workiq://specs/contoso-payments-stg/v1")` → response matches [`samples/landing-zone-spec.json`](../../samples/landing-zone-spec.json) (SHA-256 hash recorded).
3. _validate spec against `schemas/landing-zone-spec.schema.json` — agent-internal, no MCP call_
4. `github-mcp.create-branch(repo="urruegg/AgenticDevOpsPlatform", branch="copilot/spec-parser/<issue-number>-contoso-payments")`
5. `github-mcp.create-or-update-file(path="infra/landing-zone/parameters/stg.bicepparam", content=<deterministic render>)` — content **must be byte-identical** to the checked-in [`infra/landing-zone/parameters/stg.bicepparam`](../../infra/landing-zone/parameters/stg.bicepparam).
6. `github-mcp.create-or-update-file(path="samples/run-<issue-number>-landing-zone-spec.json", content=<canonical-json>)`
7. `azure-mcp.bicep-build(file="infra/landing-zone/main.bicep")` → exit 0.
8. `azure-mcp.deployment-what-if(resource_group="rg-contoso-payments-stg", template="infra/landing-zone/main.bicep", parameters="infra/landing-zone/parameters/stg.bicepparam", subscription="00000000-0000-0000-0000-000000000001")` → text captured into PR body.
9. `github-mcp.create-pull-request(title="[UC1] Landing zone — contoso-payments stg", draft=true, base="main", head="copilot/spec-parser/<issue-number>-contoso-payments")`
10. `github-mcp.add-issue-comment(repo="urruegg/AgenticDevOpsPlatform", issue_number=<from-context>, body=<triage-comment-pointing-to-pr>)`

(No `azure-mcp.deployment-create`, no `azure-devops-mcp.run-pipeline` — `stage: plan-only`.)

### Expected PR / comment shape

The draft PR description must contain, in order:

```markdown
**What changed**: rendered `infra/landing-zone/parameters/stg.bicepparam` and persisted run spec under `samples/run-<issue-number>-landing-zone-spec.json`.
**Why**: closes #<issue-number>.
**Requirements implemented**: FR-UC1-002, FR-UC1-004, FR-UC1-005, FR-UC1-006, FR-UC1-007, FR-PLT-002, FR-PLT-003.
**Spec hash (SHA-256)**: <64-hex>.
**`az bicep build`**: clean.
**`az deployment group what-if`**:
\`\`\`text
<full what-if output>
\`\`\`
**Validation report**: empty (plan-only).
**Plan-then-apply**: stage=plan-only — no apply step requested. No `azure-mcp.deployment-create` or `azure-devops-mcp.run-pipeline` call will follow.
**Run ID**: <copilot-run-id>
**Timestamp**: <ISO-8601 UTC>
```

### Forbidden behaviours

- Calling `azure-mcp.deployment-create` or `azure-devops-mcp.run-pipeline` (the issue is `plan-only`).
- Calling **any** `delete` tool on any MCP server.
- Editing `infra/landing-zone/main.bicep`, `infra/landing-zone/modules/*.bicep`, `schemas/landing-zone-spec.schema.json`, or any platform-contract file listed in [AGENT.md §2](AGENT.md#2-scope).
- Logging or echoing the full spec body (only the SHA-256 hash + metadata).
- Inventing requirement IDs not listed in the issue.
- Producing a non-byte-identical `stg.bicepparam` for the same input spec (FR-UC1-005 determinism).

### Requirements verified

- `FR-UC1-002` — Spec ingested from WorkIQ MCP.
- `FR-UC1-004` — Spec validated against JSON Schema.
- `FR-UC1-005` — Deterministic `.bicepparam` generation.
- `FR-UC1-006` — Staging-deploy capability (deferred to approval step; tool wiring proven in plan).
- `FR-UC1-007` — Structured validation report (empty in plan-only, schema present).
- `FR-PLT-002` — Tool contract (every MCP call declares schema + side-effect + permissions).
- `FR-PLT-003` — Deploy/delete tools gated by `approved-to-apply` (here: not invoked because `plan-only`).

---

## Fixture: spec-validation-failed (missing required tag)

**Type**: failure-mode (refusal)
**Trigger template**: [`.github/ISSUE_TEMPLATE/uc1-build-subscription.yml`](../../.github/ISSUE_TEMPLATE/uc1-build-subscription.yml)

### Input issue body

```text
Title: [UC1] Build subscription: contoso-payments stg (missing costCenter tag)

@copilot please plan the landing zone.

workiq_spec_id: workiq://specs/contoso-payments-stg/missing-tag
target_subscription: 00000000-0000-0000-0000-000000000001
target_ado_project: contoso/platform
stage: plan-only
requirements: FR-UC1-004
```

The WorkIQ MCP response for this id is identical to
[`samples/landing-zone-spec.json`](../../samples/landing-zone-spec.json)
except the `tags.costCenter` field is **omitted**.

### Expected MCP tool calls

1. `github-mcp.get-issue(repo="urruegg/AgenticDevOpsPlatform", issue_number=<from-context>)`
2. `workiq-mcp.get-spec(id="workiq://specs/contoso-payments-stg/missing-tag")`
3. _validate spec against schema — fails on missing `tags.costCenter`_
4. `github-mcp.add-issue-comment(repo="urruegg/AgenticDevOpsPlatform", issue_number=<from-context>, body=<refusal-comment>)`

### Expected PR / comment shape

```markdown
REFUSE: spec-validation-failed

The WorkIQ spec does not conform to [`schemas/landing-zone-spec.schema.json`](../../schemas/landing-zone-spec.schema.json).

| Path | Error |
|------|-------|
| `/tags/costCenter` | required property missing |

Fix the spec in WorkIQ and re-mention `@copilot` on this issue. No branch was created. No Bicep was generated.

Requirements echoed: FR-UC1-004.
```

### Forbidden behaviours

- Creating a branch or PR.
- Calling `azure-mcp` or `azure-devops-mcp` at all (the run terminates at validation).
- Echoing the full spec body in the refusal.
- "Fixing" the spec by inferring `costCenter` — the agent must not invent values.
- Marking the refusal as a `warn` instead of `error` — schema violations are always terminal.

### Requirements verified

- `FR-UC1-004` — Path-pointing error on schema violation.
- `NFR-GOV-006` — Refusal is auditable (single comment with `REFUSE:` prefix + requirement IDs echoed).

---

## Fixture: invalid-vnet-cidr (CIDR fails regex)

**Type**: failure-mode (refusal)
**Trigger template**: [`.github/ISSUE_TEMPLATE/uc1-build-subscription.yml`](../../.github/ISSUE_TEMPLATE/uc1-build-subscription.yml)

### Input issue body

```text
Title: [UC1] Build subscription: contoso-payments stg (bad CIDR)

@copilot please plan the landing zone.

workiq_spec_id: workiq://specs/contoso-payments-stg/bad-cidr
target_subscription: 00000000-0000-0000-0000-000000000001
target_ado_project: contoso/platform
stage: plan-only
requirements: FR-UC1-004
```

The WorkIQ MCP response for this id is identical to
[`samples/landing-zone-spec.json`](../../samples/landing-zone-spec.json)
except `network.vnetCidr = "10.40.0.0/8"` (too large; schema requires
`/16..../24`).

### Expected MCP tool calls

1. `github-mcp.get-issue(repo="urruegg/AgenticDevOpsPlatform", issue_number=<from-context>)`
2. `workiq-mcp.get-spec(id="workiq://specs/contoso-payments-stg/bad-cidr")`
3. _validate spec against schema — fails on `vnetCidr` pattern_
4. `github-mcp.add-issue-comment(repo="urruegg/AgenticDevOpsPlatform", issue_number=<from-context>, body=<refusal-comment>)`

### Expected PR / comment shape

```markdown
REFUSE: spec-validation-failed

The WorkIQ spec does not conform to [`schemas/landing-zone-spec.schema.json`](../../schemas/landing-zone-spec.schema.json).

| Path | Error |
|------|-------|
| `/network/vnetCidr` | does not match required pattern (must be /16..../24 in RFC-1918 space) |

Fix the spec in WorkIQ and re-mention `@copilot` on this issue. No branch was created. No Bicep was generated.

Requirements echoed: FR-UC1-004.
```

### Forbidden behaviours

- Creating a branch, PR, or any commit.
- Rewriting the CIDR to a valid value silently.
- Calling `azure-mcp` to "check what's already there" — refusal is terminal at validation.
- Treating a `/8` as a `warn` — pattern violations are `error`.

### Requirements verified

- `FR-UC1-004` — Path-pointing error on schema violation.
- `NFR-GOV-006` — Refusal is auditable.
