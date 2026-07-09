# CSA simulation notebook (`csa-simulate`)

> **Version** 1.0.0 · **Date** 2026-07-09 · **Author** Urs Rüegg · **Status** Draft for review · **Previous Version** n/a (new — Sprint 16 T5)

Sprint 16 T5 — the Fabric Spark notebook that runs a what-if scenario against
**synthetic Gold capacity data** (ADR-0016, no PHI) and writes a
`DC-SIM-RESULT` row back to Fabric plus a `simulation-runs` document to Cosmos.

## Design

The heavy Spark I/O lives in `run()`; the decision logic is Spark-free and
unit-testable:

| Module | Role |
| ------ | ---- |
| `shock_model.py` | Pure shock model — projects baseline capacity forward under a scenario's shock vector; computes utilization, shortfall, KPIs. |
| `csa-simulate.py` | `simulate()` = shock → tier classification (ADR-0021) → KPIs → `simulation-runs` document. `run()` is the Fabric entrypoint. |

Tier classification is delegated to
[`data-platform/scripts/csa/csa-tier-classifier.py`](../../scripts/csa/csa-tier-classifier.py)
so the doctrine rules stay version-pinned (ADR-0021).

## Golden test

For the canonical **RSV surge** input (pediatric-beds 40 cap / 30 occ, +50 %
demand) the simulation returns **Tier 2** with a modest pediatric bed shortfall
(KPI band 3–8 beds, one dimension over threshold). The **cyber-attack** capacity
loss escalates to **Tier 3**. See `tests/test_csa_simulate_pure.py`.

```bash
cd data-platform/notebooks/csa
python3 -m unittest discover -s tests -v
```

## Publish (gated)

Publishing the notebook to `ws-ihzhhpf-sit-data` is a `deploy`-ceiling action.
Post the plan as a PR comment and wait for `@urruegg` to reply
`approved-to-apply` (AGENTS.md §4) before running
[`data-platform/scripts/csa/deploy-notebook.py`](../../scripts/csa/deploy-notebook.py).
