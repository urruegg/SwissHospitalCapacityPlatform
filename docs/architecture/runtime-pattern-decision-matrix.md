# Agent Runtime Pattern Decision Matrix

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Draft |
| **Previous Version** | N/A |

## Purpose

Resolve the runtime pattern drift between the application-hosted agent baseline
(`docs/AI.md`) and externally referenced Foundry-hosted patterns, by recording an
explicit, reviewable runtime decision per workload class. This is the Phase 1
deliverable for the runtime pattern scope gate in
[`docs/adr/0008-agent-runtime-pattern-scope-and-selection.md`](../adr/0008-agent-runtime-pattern-scope-and-selection.md)
and closes register item `RV-05` in
[`sprints/sprint-05/requires-validation-register.md`](../../sprints/sprint-05/requires-validation-register.md).

It addresses CAF/WAF review findings §3.4, §4.1, and §5.1 and removes the
DoD-blocking contradiction between
[`docs/AI.md`](../AI.md) and [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) runtime
pattern decisions.

## Decision Baseline

Per ADR-0008, the binding default is:

1. **Application-hosted agent runtime is the default pattern** for all regulated MVP
   paths.
2. **Foundry Agent Service** is permitted only when explicitly scoped for the workload,
   with a hard go/no-go rule: the required Foundry service/capability must be **GA in the
   selected target region**. If it is not GA in-region, the Foundry path is **no-go**.
3. **Hybrid runtime** is permitted only with an explicit boundary contract (see below).
4. Every runtime choice is reflected consistently across `docs/ARCHITECTURE.md`,
   `docs/AI.md`, `docs/SD.md`, and release traceability/test evidence.

## Workload Class Decision Matrix

Runtime mode values: `application-hosted` (default), `foundry-hosted`, `hybrid`.

| Workload class | Example flows | PHI / data class | Runtime mode | GA-region requirement | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| WC-1 Interactive PHI copilot | Bed/flow Q&A, discharge coordination support (FR-CX) | PHI-sensitive | `application-hosted` | Azure OpenAI Standard/Regional GA in Switzerland regions only | Accepted |
| WC-2 Operational recommendations | Forecast-aware operational recommendations (FR-FC) | PHI-sensitive | `application-hosted` | Azure OpenAI Standard/Regional GA in Switzerland regions only | Accepted |
| WC-3 Non-PHI assistive/reporting | Aggregated, de-identified reporting assistance | Non-PHI | `application-hosted` | Default; Foundry-hosted only if GA-in-region and scoped | Accepted (Foundry candidate, deferred) |
| WC-4 Experimental / evaluation | Pattern benchmarking against Foundry reference architecture | Non-PHI, isolated | `hybrid` (evaluation only) | Foundry segment requires GA-in-region evidence + boundary contract | Deferred to post-MVP, requires ADR if promoted |

> No PHI-sensitive workload class is approved for a Foundry-hosted or hybrid runtime in
> Sprint 5. Any future change to a PHI-sensitive class requires a superseding ADR per
> ADR-0008.

## Hybrid Boundary Contract Template

Per ADR-0008, every hybrid flow requires a boundary contract with all fields below.
A hybrid flow without a complete contract is denied at the runtime gate.

| Field | Description |
| ----- | ----- |
| `flowId` | Unique flow identifier and business capability. |
| `runtimeMode` | Runtime mode per segment (`application-hosted` or `foundry-hosted`). |
| `dataClass` | Data class and PHI handling rule for each segment. |
| `regionGaEvidence` | Region and GA capability evidence reference for any Foundry segment. |
| `controlOwner` | Control owner and approver roles. |
| `evidenceArtifacts` | Required evidence artifacts and test cases. |
| `failureHandling` | Failure mode, fallback path, and rollback trigger. |

### Hybrid Boundary Contract Register

| `flowId` | Segments | Status |
| ----- | ----- | ----- |
| _none_ | No hybrid flows approved in Sprint 5 | n/a |

## Enforcement Gates

Per ADR-0008, runtime decisions are enforced at:

1. **CI gate** — runtime-matrix update required when runtime-related files change.
2. **SIT gate** — boundary contract, GA-region evidence, and test evidence required for
   any non-default runtime path.
3. **PROD gate** — all SIT evidence plus explicit human approvals and residual-risk
   statement.
4. **Runtime gate** — side-effecting paths enforce selected runtime boundaries and deny
   execution on contract violations.

## Approval Ownership

1. **ARCH** — Architecture Owner approves runtime pattern and boundary contract.
2. **SEC** — Security and Compliance Owner approves data-class, residency, and control
   mapping.
3. **OPS** — Operations and Release Owner approves production readiness, fallback, and
   supportability.

## Revalidation Cadence

Runtime choices are revalidated monthly per ADR-0008: confirm GA availability in selected
regions, validate control-evidence freshness and open-risk status, and create follow-up
issues for any drift.

## Consistency Confirmation

This matrix is the single source of truth for runtime mode by workload class. The
following documents are aligned to it and must not state a conflicting default:

1. [`docs/AI.md`](../AI.md) §Scope and Constraints — application-hosted default.
2. [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) §Decisions — runtime pattern decision.
3. [`docs/SD.md`](../SD.md) §Design Principles — runtime mode mapping.

## Traceability

| Requirement | Control | ADR | Register item |
| ----- | ----- | ----- | ----- |
| `NFR-AI-001`, `NFR-AI-004` | `CH-C10` | ADR-0008 | `RV-05` |
| `NFR-COMP-004` | `CH-C05` | ADR-0008 | `RV-05` |

## Change Control

Any change to the decision matrix or boundary contract register bumps this document's
version per `.github/copilot-instructions.md` §9 and must stay consistent with ADR-0008.
