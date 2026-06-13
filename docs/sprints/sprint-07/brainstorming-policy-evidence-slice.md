# Sprint 07 Brainstorming — policy-evidence-slice

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-12 |
| **Author** | GitHub Copilot |
| **Status** | Draft |
| **Previous Version** | 0.0.0 (new brainstorming artifact) |

## Stage and Skill

- Superpowers stage: `brainstorming` (Stage 1 of the
  [stage-runbook](stage-runbook.md)).
- Next stage: `writing-plans` (this brief is the approved design source for the
  Stage 3 task plan).

## Traceability

| Field | Value |
| ----- | ----- |
| Slice | `policy-evidence-slice` |
| Brainstorming issue | #56 |
| Parent sprint delegation issue | #54 |
| Sprint document | [sprint-07-data-platform-and-data-products-superpowers.md](../sprint-07-data-platform-and-data-products-superpowers.md) |
| Planned PR | pending |

## Requirements

| Requirement | Source | Why it applies |
| ----- | ----- | ----- |
| `NFR-GOV-006` | Repository governance baseline (every response is requirement-traceable or an auditable refusal) | The slice exists to make policy outcomes and evidence requirement-traceable. |
| `FR-GOV-004` | [docs/PRD.md](../../PRD.md) — produce governance evidence artifacts for compliance reviews | The slice generates the evidence artifacts. |
| `FR-GOV-001` | [docs/PRD.md](../../PRD.md) — auditable traceability across sources, outputs, and events | Evidence must link controls to requirements. |
| `NFR-COMP-007` | [docs/PRD.md](../../PRD.md) — default-deny PHI cross-border / failover unless explicitly approved | Residency/transfer policy is a gated control. |
| `NFR-COMP-010` | [docs/PRD.md](../../PRD.md) — maintain compliance evidence artifacts and review cadence | Evidence cadence and retention shape. |

> The final `FR-*` set is confirmed during `writing-plans`; `FR-GOV-004` and
> `NFR-GOV-006` are the anchor requirements for this brainstorming.

## Problem

Sprint 07 introduces new data-platform and data-product slices (episode model,
sample data generator, ingestion-to-serving paths). Each new slice must clear
the existing governance controls and produce **machine-checkable policy
validation** plus **auditable evidence artifacts** before promotion. Today the
policy-as-code gate ([`policy/policy_gate.py`](../../../policy/policy_gate.py))
and the synthesized-data gate
([`data/synthetic/validate_datasets.py`](../../../data/synthetic/validate_datasets.py))
already emit pass/fail results, but Sprint 07 needs a single, repeatable
**policy-and-evidence slice** that:

1. runs the relevant policy validation for a Sprint 07 slice, and
2. writes a dated evidence artifact in the established shape, with explicit
   FR/NFR/CH/RV coverage and a clear pass/fail summary.

## Design brief

### Goal

Define a thin, reusable validation-and-evidence slice that any Sprint 07
delivery slice can invoke to produce promotion evidence, reusing the existing
gates rather than introducing new tooling.

### In scope

1. Compose the existing policy-as-code gate (`policy/policy_gate.py`) and the
   synthesized-data contract gate (`data/synthetic/validate_datasets.py`) into a
   documented evidence-generation flow for Sprint 07 slices.
2. Define the Sprint 07 evidence artifact contract (fields, location, naming)
   consistent with `docs/sprints/sprint-06/evidence/*.json`.
3. Define explicit control coverage mapping (`fr`, `nfr`, `ch`, `rv`) for each
   evidence run.
4. Define the SIT-before-PROD gate sequence for this slice.

### Out of scope

1. New policy engines or replacing `policy/policy-pack.json`.
2. Any `deploy`/`delete` action against Azure or customer subscriptions.
3. Changing approval gates, residency rules, or compliance thresholds.
4. Removing or weakening existing checks for delivery speed.

### Constraints

1. **Swiss region and residency**: residency stays pinned to
   `switzerlandnorth` / `switzerlandwest`; default-deny on cross-border transfer
   (`NFR-COMP-007`). No change to allowed regions.
2. **No deploy/delete without `approved-to-apply`**: this slice is `read`/`write`
   only (runs validators, writes Markdown + JSON evidence). It must never trigger
   a gated MCP action.
3. **Evidence shape reuse**: evidence JSON mirrors the Sprint 05/06 schema
   (`evidenceType`, `gateName`, `environment`, `passFailSummary`,
   `controlCoverage`).
4. **Traceability first**: every evidence run names the FR/NFR/CH/RV it advances
   (`NFR-GOV-006`).

## Alternatives and recommendation

### Alternative A — Reuse and compose existing gates (recommended)

Wire the existing `policy/policy_gate.py` and
`data/synthetic/validate_datasets.py` into a documented Sprint 07
evidence flow, and add a Sprint 07 evidence artifact + phase record following
the Sprint 05/06 pattern.

- **Pros**: lowest risk; no new dependencies; consistent with stored repo
  conventions; dependency-free Python already in CI
  (`.github/workflows/policy-gate.yml`, `.github/workflows/data-contracts.yml`).
- **Cons**: requires a small amount of glue/documentation to define the Sprint 07
  evidence contract.

### Alternative B — New unified "evidence orchestrator" script

Build a new script that calls both gates and aggregates a single evidence file.

- **Pros**: one entry point; single aggregated artifact.
- **Cons**: new code surface to test and maintain; duplicates logic that the two
  gates already own; higher review and security burden for marginal benefit.

### Alternative C — Manual evidence authoring per slice

Author evidence JSON/Markdown by hand per slice without a defined contract.

- **Pros**: zero tooling change.
- **Cons**: not machine-checkable; error-prone; violates the spirit of
  `FR-GOV-004`/`NFR-GOV-006`; not repeatable.

### Recommendation

Adopt **Alternative A**. It maximizes reuse, keeps the slice `read`/`write` only,
preserves residency and approval guardrails, and produces evidence in the
already-validated shape. Defer Alternative B unless a future sprint proves the
two-command flow is a real friction point.

## Acceptance criteria

1. A Sprint 07 slice can produce promotion evidence by running the existing gates
   (`python3 policy/policy_gate.py --scope sit|prod` and
   `python3 data/synthetic/validate_datasets.py`), with both exiting `0` on
   success and `1` on critical failure.
2. The evidence artifact is written under
   `docs/sprints/sprint-07/evidence/` with a dated filename and contains
   `evidenceType`, `gateName`, `environment`, `passFailSummary`, and
   `controlCoverage` (`fr`, `nfr`, `ch`, `rv`).
3. Evidence `controlCoverage` lists at least `FR-GOV-004` and `NFR-GOV-006`, plus
   any slice-specific IDs.
4. SIT evidence is produced and passes before PROD evidence is requested
   (gate sequence honored).
5. Residency remains pinned to approved Swiss regions; no cross-border transfer
   is enabled by this slice (`NFR-COMP-007`).
6. No `deploy`/`delete` action is taken; any such action would require a separate
   `approved-to-apply` confirmation and is explicitly out of scope.
7. The brief is linked from the Sprint 07 [README](README.md) and the
   [checkpoint-matrix](checkpoint-matrix.md) brainstorming row references this
   artifact.

## Risks and assumptions

### Assumptions

1. The existing gates remain the source of truth for policy checks; no rule
   changes are needed for this slice.
2. Sprint 07 datasets/contracts will expose the fields the gates expect
   (pseudonymised identifiers, purpose tags, taxonomy version).
3. Evidence consumers accept the Sprint 05/06 JSON shape unchanged.

### Risks

| Risk | Impact | Mitigation |
| ----- | ----- | ----- |
| Evidence shape drifts from Sprint 05/06 schema | Auditors cannot compare runs | Pin the contract in the writing-plans task and validate against an existing evidence sample. |
| Slice scope creeps into new policy logic | Higher review/security burden | Hard out-of-scope list above; keep policy rules in `policy/policy-pack.json`. |
| A gated Azure action is attempted | Compliance/approval breach | Slice is `read`/`write` only; `approved-to-apply` required for any apply, which is out of scope here. |
| Residency rule accidentally relaxed | PHI cross-border exposure | No change to `allowedRegions`; `NFR-COMP-007` default-deny preserved. |
| Missing FR/NFR mapping in evidence | Traceability gap (`NFR-GOV-006`) | Acceptance criterion 3 requires explicit `controlCoverage`. |

## Next step

Promote this brief to `writing-plans` (Stage 3) to produce a 2–15 minute task
plan with file targets, validation commands, and expected evidence artifacts,
mapped to the requirement IDs above.
