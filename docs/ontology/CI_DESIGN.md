# CI Conformance Check — Two-Layer Ontology

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-03 |
| **Author** | Urs Rüegg |
| **Status** | Sprint 09 strict (enforcing) |
| **Previous Version** | 0.1.0 (Sprint 09 scaffold — WARN-only) |
| **Realises** | [`FR-GOV-ONT-003`](../PRD.md#h-semantic-ontology), part of [`NFR-ONT-001`](../PRD.md#h-semantic-ontology-sprint-9), [AMA §11.1 H-05](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff), sprint-09 §0 RB-08 |
| **Depends on** | [ADR-0014 §4](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#4-governance-model-obo-inspired), [`reference-layer.ttl`](reference-layer.ttl), [`crosswalk.md`](crosswalk.md), [`data/synthetic/schema/`](../../data/synthetic/schema/) |

## Purpose

Enforce (per FR-GOV-ONT-003) that every operational-layer entity in the Fabric IQ ontology has a corresponding reference-layer class in [`reference-layer.ttl`](reference-layer.ttl) AND every data-contract ID referenced from [`crosswalk.md`](crosswalk.md) has a matching JSON Schema on disk.

Fails the build when the two layers drift or when a crosswalk row references a contract that has no schema. Prevents the two-layer risk called out in [ADR-0014 §T-02](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) and [AMA R-05](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-key-risks-h--high-m--medium-l--low), and closes the enforcement gap flagged in [AMA §11.1 H-05](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff).

## What the check does

Located at [`scripts/ontology/check_crosswalk_conformance.py`](../../scripts/ontology/check_crosswalk_conformance.py). Reads three sources:

1. **Reference layer** — parses [`reference-layer.ttl`](reference-layer.ttl) for every `hcp:*` `owl:Class` declaration.
2. **Crosswalk** — parses [`crosswalk.md`](crosswalk.md) for every `hcp:*` class referenced in the MVO scope table AND for every backticked `` `DC-*-vN` `` data-contract ID.
3. **Contracts on disk** — enumerates `*.schema.json` under [`data/synthetic/schema/`](../../data/synthetic/schema/).

Then runs three checks:

| # | Check | Severity | Message |
| --- | ----- | -------- | ------- |
| 1 | Reference class has no crosswalk row (except the abstract roots `hcp:CapacityUnit`, `hcp:CapacityState`, `hcp:InformationContent`) | **WARN** | `reference class <cls> has no row in crosswalk.md MVO table` |
| 2 | Crosswalk row references a class not declared in the TTL | **FAIL** | `crosswalk row references undeclared reference class <cls>` |
| 3 | Crosswalk backticks a data-contract ID (`` `DC-*-vN` ``) with no matching `.schema.json` under `data/synthetic/schema/` | **FAIL** | `crosswalk contract <id>-vN has no schema under data/synthetic/schema/` |

Exit codes (`--strict` mode — what CI runs):

- `0` — no findings.
- `1` — any WARN or FAIL finding.
- `2` — script error (file missing, unreadable, malformed).

Exit codes (default — local dev convenience only):

- `0` — check ran successfully; findings printed but do not fail the build.
- `2` — script error.

**Convention.** Crosswalk rows that reference concrete, materialised contracts backtick-quote the ID (`` `DC-FOO-v1` ``). Rows that mention future or deferred contract IDs write them as plain text (`DC-FOO-v1`) so the check does not flag them until the schema lands.

## When it runs

CI workflow: [`.github/workflows/ontology-conformance.yml`](../../.github/workflows/ontology-conformance.yml).

Triggers:

- `pull_request` — any PR that touches `docs/ontology/**`, `scripts/ontology/**`, `data/synthetic/schema/**`, or the workflow file itself.
- `workflow_dispatch` — manual trigger for ad-hoc runs.

The single CI step invokes the check with `--strict`, so any WARN or FAIL fails the build.

## Sprint 09 v2.0.0 semantics (STRICT — enforcing)

The Sprint 09 v2.0.0 refinement flips the check from advisory to enforcing (per plan T1.6 / design spec §3.5):

- The reference layer includes all Sprint 09 MVO classes plus 4 Information Content Entity classes (Encounter, DischargeReadinessScore, DischargeRecommendation, ForecastOutput) added under T1.3 / T1.4.
- All 3 new data contracts added under T1.5 (`DC-DISCHARGE-SCORE-v1`, `DC-DISCHARGE-RECOMMENDATION-v1`, `DC-DEMAND-FORECAST-v1`) exist under `data/synthetic/schema/` so the contract-existence gate (check 3) passes cleanly.
- Any future PR that adds a crosswalk row referencing a new class MUST also add the class to `reference-layer.ttl` — check 2 blocks otherwise.
- Any future PR that backticks a new `` `DC-*-vN` `` in the crosswalk MUST also add the `.schema.json` under `data/synthetic/schema/` in the same PR — check 3 blocks otherwise. Deferred contracts must be written as plain text without backticks.

Sprint 10 remaining work: extend the check with a third source (operational-entity list generated from the Fabric IQ semantic model) so it can also detect operational-layer drift. Recorded as a follow-up in the Sprint 10 backlog; not gating the Sprint 09 v2.0.0 strict-mode flip.

## Local invocation

```powershell
# From repo root
python scripts/ontology/check_crosswalk_conformance.py            # WARN-only (local convenience)
python scripts/ontology/check_crosswalk_conformance.py --strict   # what CI runs
python -m pytest scripts/ontology/tests/ -v                       # unit tests
```

No third-party dependencies — the script uses only Python 3.10+ stdlib.

## Change log

- `1.0.0` (2026-07-03) — strict-mode flip landed. Added contract-existence check (check 3) that cross-references crosswalk backticks against `data/synthetic/schema/*.schema.json`. Workflow flipped from WARN-only to STRICT single step. MAJOR bump per §9 Document Versioning (semantics change from advisory to enforcing). Test: [`scripts/ontology/tests/test_contract_existence.py`](../../scripts/ontology/tests/test_contract_existence.py). Design spec §3.5, plan T1.6.
- `0.1.0` (2026-07-02) — initial scaffold. WARN-only mode. Two source files (TTL + crosswalk).
