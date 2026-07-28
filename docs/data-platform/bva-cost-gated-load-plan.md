# BVA cost-basis gated live-load plan (Sprint 33 WS-A)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | (none — initial) |

**Plan-only.** This document describes the `approved-to-apply`-gated path that
publishes the Sprint 33 WS-A BVA cost-basis product to live Fabric. **Nothing in
this document is executed by the WS-A pull request.** Every step below is a
`deploy`-ceiling action gated by an explicit human `approved-to-apply` comment
per [AGENTS.md §4](../../AGENTS.md) and the confirmation rules in
[`.github/copilot-instructions.md` §4](../../.github/copilot-instructions.md).

Related artefacts:

- Gold schema + `sm_bva` measure catalog:
  [`bva-cost-gold-schema.md`](bva-cost-gold-schema.md).
- Pure transform: [`data-platform/bva/costbasis.py`](../../data-platform/bva/costbasis.py).
- Notebook wrapper:
  [`data-platform/notebooks/bva/build_gold_bva_costbasis.py`](../../data-platform/notebooks/bva/build_gold_bva_costbasis.py).
- Master data (golden source):
  [`data/master-data/bva/`](../../data/master-data/bva/).
- Plan: [`2026-07-28-sprint-33-bva-agent-ws-a-cost-data-product.md`](../superpowers/plans/2026-07-28-sprint-33-bva-agent-ws-a-cost-data-product.md).

## SIT + PROD parity method

The 7 CSVs under `data/master-data/bva/` are the **single golden source**, loaded
**identically** to SIT and PROD. Environment differs only by the Fabric workspace
and lakehouse coordinates in
[`data-platform/fabric/environments.yml`](../../data-platform/fabric/environments.yml)
(`SIT` → `ws-ihzhhpf-sit-data` / `lh_ihzhhpf_sit`, westus2; `PROD` →
`ws-ihzhhpf-prod-data` / `lh_ihzhhpf_prod`, switzerlandnorth). Those GUIDs are
deployment coordinates, not secrets. No per-environment CSV or transform drift is
permitted — parity is proven by loading the same files and asserting the same
`bva_baseline_kpi` reconciliation (one-time `1,300,000` CHF, annual run
`1,250,000` CHF, hospitals `3`) in each environment.

## Gate 0 — CI proof (already green in the WS-A PR, no approval needed)

These run in CI and require **no** `approved-to-apply`:

1. `python data/master-data/validate_master_data.py` — PK / FK / enum / no-PHI /
   ledger-sums-to-ROM gate on the 7 CSVs.
2. `python -m pytest data-platform/bva evals/bva-agent data/master-data/tests`
   — reconciliation + byte-stable transform tests.

## Gated live-load sequence (each step needs `approved-to-apply`)

> The agent posts a `what-if` / dry-run summary first, waits for a repo-writer
> human to reply `approved-to-apply` on the same thread, then executes exactly
> the approved step. The approver handle + timestamp are echoed in the follow-up
> comment. The agent refuses if the approver is a bot or lacks write access, or
> if the executed shape differs materially from the approved plan
> (AGENTS.md §4).

### Step 1 — Upload master data to OneLake (per environment)

```bash
python data-platform/scripts/upload_to_onelake.py \
  --workspace-id <env.workspace_id> --lakehouse-id <env.lakehouse_id> \
  --source-root data/master-data/bva --target master-data/bva
```

Lands the 7 CSVs under `Files/master-data/bva/`. IDs come from
`environments.yml` (never hard-coded, never a secret).

### Step 2 — Run the medallion notebook

Run [`build_gold_bva_costbasis.py`](../../data-platform/notebooks/bva/build_gold_bva_costbasis.py)
(via `run_notebooks.py`) to write the 5 Gold Delta tables: `gold.bva_bom_dim`,
`gold.bva_cost_fact`, `gold.bva_effort_fact`, `gold.bva_hospital_profile_dim`,
`gold.bva_baseline_kpi`. Post-run assertion: `gold.bva_baseline_kpi` matches the
ROM (one-time `1,300,000`, run `1,250,000`, hospitals `3`).

### Step 3 — Publish the `sm_bva` Direct Lake semantic model

Publish the `sm_bva` semantic model over the Gold tables with the measures in the
[measure catalog](bva-cost-gold-schema.md#sm_bva-measure-catalog). Verify each
measure equals its `bva_baseline_kpi` row.

### Step 4 — Ground the BVA agent / Fabric IQ Data Agent

Register `sm_bva` (and the Gold tables) as a read-only grounding surface for the
BVA agent per [ADR-0034](../adr/0034-fabric-iq-demo-scope-artefacts.md), so the
deterministic `bva.simulate` engine can later source its
[`archetypes.py`](../../data-platform/bva/archetypes.py) provisional constants
from `sm_bva` without changing the frozen `bva.simulate` contract.

### Step 5 — Data-quality contract-check

Run the [`data-quality-agent`](../../agents/data-quality-agent/AGENT.md)
Bronze/Silver/Gold contract-check on the landed `bva_*` tables (schema, PK/FK,
no-PHI, ledger reconciliation). Quarantine + alert on any drift.

## Rollback

Gold tables are `overwrite`-mode and rebuilt from the golden-source CSVs, so
rollback is re-running Step 2 from the last-good commit of
`data/master-data/bva/`. No destructive delete is required or permitted without a
separate `approved-to-apply` gate.

## Provenance & PHI

All data is synthetic / anonymized (Curavias demo; no PHI —
[ADR-0013](../adr/0013-temporary-us-region-demo-scope.md),
[ADR-0016](../adr/0016-no-phi-in-mvp-demo-scope.md)).
