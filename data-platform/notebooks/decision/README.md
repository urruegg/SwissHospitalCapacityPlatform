# Decision medallion notebook (`decision`)

> **Version** 1.0.0 · **Date** 2026-07-27 · **Author** Urs Rüegg · **Status** Draft · **Previous Version** — (new — Sprint 26 WS-B, issue #335)

Sprint 26 WS-B — the deterministic **Decision-tier** Gold materialization that
turns a flat discharge-blocked candidate feed into a ranked list of **systemic
barriers** (design spec §3.3 item 3 / beat 3): the DCA "N candidates collapse
into M barriers" pattern.

**Synthetic + deterministic only** (ADR-0013 / ADR-0016). No PHI — candidates
carry only an opaque `candidate_key` and ontology ward IDs, so the Gold rows
carry only aggregate counts + ward IDs. **No LLM-guessed numbers** (design
D2/D4): the collapse/rank logic is the pure
[`derive_barriers`](../../decision/barriers/derive_barriers.py) builder, reused
verbatim (not duplicated), with a clean seam (`build_gold_barrier.run(candidates=…)`
/ `DEFAULT_CANDIDATES`) to swap in a real discharge-candidate feed later without
changing the Gold contract or the ontology binding.

## Design

The materialization module lives with the pure builder in the decision lane
([`data-platform/decision/barriers/build_gold_barrier.py`](../../decision/barriers/build_gold_barrier.py))
so it can reuse `derive_barriers` directly. The heavy Spark I/O lives in that
module's `run()` / `_write` (`# pragma: no cover`); the transform is Spark-free
and unit-tested offline
([`data-platform/decision/barriers/tests/test_gold_barrier.py`](../../decision/barriers/tests/test_gold_barrier.py)),
following the WS-A `foresight` pattern. Empty inputs still write a well-typed
Delta table via an explicit `_empty_schema`.

| Module | Role |
| ------ | ---- |
| `barriers/build_gold_barrier.py` | `build_discharge_barriers(candidates, produced_at)` → `gold.fact_discharge_barrier` rows (ranked, camelCase, contract-shaped); `discharge_barrier_envelope` wraps rows into the `DC-DISCHARGE-BARRIER-v1` contract for validation; `run()` is the Fabric entrypoint. Reuses `derive_barriers` verbatim. |
| `run_decision_medallion.ipynb` | Fabric orchestration: adds the decision root to `sys.path`, calls `build_gold_barrier.run()`, verifies the count (5 barriers from the 8-candidate default feed) + displays the ranked barrier board. |

## Medallion chain + table names

| Layer | Table | Contents |
| ----- | ----- | -------- |
| Gold | `gold.fact_discharge_barrier` | One row per systemic discharge barrier: `barrierType`, `ownerRole`, `rank`, `candidateCount`, `bedImpact`, `agedH`, `clearsAt`, spanning `wards`. Contract `DC-DISCHARGE-BARRIER-v1`; grounds `hcp:Barrier`. Deterministic collapse of a discharge-blocked candidate feed, ranked by bed impact then age. |

**Input:** a flat discharge-blocked candidate feed (opaque `candidate_key`,
ontology `ward`, `barrier_type`, optional `aged_h` / `clears_at` / `bed_impact`).
`DEFAULT_CANDIDATES` is the deterministic synthetic default (the design "8 → 5"
fixture, scoped to `H_USZ`); a real feed swaps in via the `run(candidates=…)` seam.

## Ontology binding

`hcp:Barrier` + relation `barrierForWard` are declared in
[`docs/ontology/reference-layer.ttl`](../../../docs/ontology/reference-layer.ttl)
(v0.5.0) and mapped in
[`docs/ontology/crosswalk.md`](../../../docs/ontology/crosswalk.md) (v0.6.0),
enforced by the STRICT two-layer conformance gate.

## Offline test

```bash
# from repo root — the barrier gold builder + pure builder tests
python -m unittest discover -s data-platform/decision -p "test_*.py" -v

# STRICT ontology two-layer conformance
python scripts/ontology/check_crosswalk_conformance.py --strict
```
