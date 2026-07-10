# CSA simulation notebook (`csa-simulate`)

> **Version** 1.1.0 · **Date** 2026-07-10 · **Author** Urs Rüegg · **Status** Reviewed · **Previous Version** 1.0.0 (added §Verify — captured `csa-verify-mvp.ipynb` v6 after Sprint 16 SIT go-live)

Sprint 16 T5 — the Fabric Spark notebook that runs a what-if scenario against
**synthetic Gold capacity data** (ADR-0016, no PHI) and writes a
`DC-SIM-RESULT` row back to Fabric plus a `simulation-runs` document to Cosmos.

## Design

The heavy Spark I/O lives in `run()`; the decision logic is Spark-free and
unit-testable:

| Module | Role |
| ------ | ---- |
| `shock_model.py` | Pure shock model — projects baseline capacity forward under a scenario's shock vector; computes utilization, shortfall, KPIs. |
| `csa-simulate.py` | `simulate()` = shock → tier classification (ADR-0024) → KPIs → `simulation-runs` document. `run()` is the Fabric entrypoint. |

Tier classification is delegated to
[`data-platform/scripts/csa/csa-tier-classifier.py`](../../scripts/csa/csa-tier-classifier.py)
so the doctrine rules stay version-pinned (ADR-0024).

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

## Verify (`csa-verify-mvp.ipynb`)

Sprint 16 T5 SIT go-live also captured a minimal end-to-end verification
notebook, `csa-verify-mvp.ipynb`. It is **not** the production
`csa-simulate.py` — it is the artefact used to prove the Concept-1 network +
auth + persistence stack works end-to-end after the Cosmos private endpoint,
Fabric MPE, and env-csa environment landed.

Cells:

1. **Auth + MPE routing** — acquires a Fabric-brokered Entra token via
   `notebookutils.credentials.getToken('https://cosmos.azure.com/.default')`
   (Managed / Default / CLI credentials are not usable inside Fabric Spark
   notebooks), constructs a `CosmosClient`, lists the 4 containers.
2. **Shock model + tier classifier** — inline copies of the pure functions
   so the notebook does not depend on `csa-simulate.py` module import.
3. **Seed** — upserts 3 response-levers + 1 RSV scenario into Cosmos through
   the private endpoint. Every document carries an `id` field (Cosmos NoSQL
   requirement, independent of partition key).
4. **Run** — invokes the canonical RSV shock, asserts `tier == 2`.
5. **Persist to Cosmos** — writes the run document to `simulation-runs`.
6. **Persist to Delta (BI parity)** — writes to
   `abfss://<workspaceId>@onelake.dfs.fabric.microsoft.com/<lakehouseId>/Tables/csa_simulation_runs`
   using an explicit ABFSS URI. This is session-context-independent — it
   works even if the notebook's default lakehouse binding is not honoured by
   the current Spark session. Sprint 17 backlog covers moving this table under
   a proper schema (e.g. `gold.csa_simulation_runs`) once the lakehouse
   schema layout is finalised.

Rerun cadence: **on demand**. This is a diagnostic notebook, not a scheduled
job. Rerun after any change to `csa.bicep` (Cosmos schema), the MPE, or
`env-csa` (library set). Successful run = 8/8 Spark jobs green + a new row in
`Tables/csa_simulation_runs`.
