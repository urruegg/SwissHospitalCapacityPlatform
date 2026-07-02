# CI Conformance Check — Two-Layer Ontology

| Field | Value |
| ----- | ----- |
| **Version** | 0.1.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Status** | Sprint 09 scaffold (WARN-only) — enforcement flip in Sprint 10 |
| **Realises** | [`FR-GOV-ONT-003`](../PRD.md#h-semantic-ontology), part of [`NFR-ONT-001`](../PRD.md#h-semantic-ontology-sprint-9), [AMA §11.1 H-05](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff), sprint-09 §0 RB-08 |
| **Depends on** | [ADR-0014 §4](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#4-governance-model-obo-inspired), [`reference-layer.ttl`](reference-layer.ttl), [`crosswalk.md`](crosswalk.md) |

## Purpose

Enforce (per FR-GOV-ONT-003) that every operational-layer entity in the Fabric IQ ontology has a corresponding reference-layer class in [`reference-layer.ttl`](reference-layer.ttl), via the [`crosswalk.md`](crosswalk.md) governed artefact.

Fails the build when the two layers drift. Prevents the two-layer risk called out in [ADR-0014 §T-02](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) and [AMA R-05](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-key-risks-h--high-m--medium-l--low).

## What the check does

Located at [`scripts/ontology/check_crosswalk_conformance.py`](../../scripts/ontology/check_crosswalk_conformance.py). Reads the two source files:

1. **Reference layer** — parses [`reference-layer.ttl`](reference-layer.ttl) for every `hcp:*` `owl:Class` declaration.
2. **Crosswalk** — parses [`crosswalk.md`](crosswalk.md) for every `hcp:*` class referenced in the MVO scope table.

Then runs two checks:

| # | Check | Severity | Message |
| --- | ----- | -------- | ------- |
| 1 | Reference class has no crosswalk row (except the abstract root `hcp:CapacityUnit` and `hcp:CapacityState`) | **WARN** | `reference class <cls> has no row in crosswalk.md MVO table` |
| 2 | Crosswalk row references a class not declared in the TTL | **FAIL** | `crosswalk row references undeclared reference class <cls>` |

Exit codes (default / WARN-only mode):

- `0` — check ran successfully; findings printed but do not fail the build.
- `2` — script error (file missing, unreadable, malformed).

Exit codes (`--strict` mode; Sprint 10):

- `0` — no findings.
- `1` — any WARN or FAIL finding.
- `2` — script error.

## When it runs

CI workflow: [`.github/workflows/ontology-conformance.yml`](../../.github/workflows/ontology-conformance.yml).

Triggers:

- `pull_request` — any PR that touches `docs/ontology/**`, `scripts/ontology/**`, or the workflow file itself.
- `workflow_dispatch` — manual trigger for ad-hoc runs.

## Sprint 09 semantics (WARN-only)

Sprint 09 delivers the scaffold. **The check never fails the build in Sprint 09** because:

- The reference layer is a skeleton (per [RB-11](../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md)); some subtypes (StaffShift, Device) are intentionally deferred to Sprint 10/11 and appear as "deferred" in the crosswalk.
- The operational layer (Fabric IQ) is not yet realised for Sprint 09 MVO delivery. The check today only compares reference ↔ crosswalk. When Fabric IQ is realised, a third source (operational-entity list) will be added.

Sprint 09 exit code is therefore always 0 unless the script itself errors (I/O, malformed input).

## Sprint 10 enforcement flip

To enable strict enforcement (per [AMA §11.1 H-05](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff)):

1. Add the operational-entity source to the script — either:
   - **Static list** in `docs/ontology/operational-entities.yaml` mirrored from the Fabric IQ generation output, refreshed via a manual runbook step; OR
   - **Live query** to Fabric IQ via the REST API (requires MI + `Fabric IQ Ontology.Read.All` scope on the workspace), scoped to `westus2` demo scope only per [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md) until GA in `switzerlandnorth`.
2. Uncomment the "STRICT preview" step in [`ontology-conformance.yml`](../../.github/workflows/ontology-conformance.yml).
3. Remove the WARN-only step above it.
4. Bump this doc's Version to **1.0.0** (MAJOR — semantics change from advisory to enforcing).
5. Update [ADR-0014 §5 gate G-A](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#5-explicit-go-no-go-gates) to reflect that the operational layer is now discoverable.

## Local invocation

```powershell
# From repo root
python scripts/ontology/check_crosswalk_conformance.py
python scripts/ontology/check_crosswalk_conformance.py --strict   # Sprint 10 preview
```

No third-party dependencies — the script uses only Python 3.10+ stdlib.

## Change log

- `0.1.0` (2026-07-02) — initial scaffold. WARN-only mode. Two source files (TTL + crosswalk).
