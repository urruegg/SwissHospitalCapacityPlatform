# CSA Cosmos schemas + seed scripts

> **Version** 1.0.0 · **Date** 2026-07-09 · **Author** Urs Rüegg · **Status** Draft for review · **Previous Version** n/a (new — Sprint 16 T3)

Sprint 16 T3 — JSON Schemas and dependency-free seed/validation tooling for the
four CSA Cosmos DB containers (design spec §4). Provisioning lives in
[`infra/modules/cosmos/`](../../../infra/modules/cosmos/README.md).

## Schemas (`schema/`)

| File | Container | Partition key |
| ---- | --------- | ------------- |
| `scenarios.schema.json` | `scenarios` | `/scenarioId` |
| `agent-memory.schema.json` | `agent-memory` | `/threadId` |
| `response-levers.schema.json` | `response-levers` | `/leverId` |
| `simulation-runs.schema.json` | `simulation-runs` | `/runId` |

Schemas are draft-07. They are enforced by a small stdlib validator
([`_schema_util.py`](_schema_util.py)) so tests and the `csa-scenario-sync`
workflow run without `pip install jsonschema`.

## Scripts

| Script | Purpose |
| ------ | ------- |
| `csa-seed-response-levers.py` | Build + validate the ~80-item doctrine-aligned response-lever library; upsert into Cosmos when configured. |
| `csa-seed-scenarios.py` | Build + validate the 8 seeded scenarios (T6); upsert into Cosmos when configured. |
| `csa-tier-classifier.py` | Swiss Lage tier classifier (T5); ADR-gated rules. |

All seed scripts are **credential-optional**: without `CSA_COSMOS_ENDPOINT` set
they run a **dry run** (validate + summary, exit 0). With it set they upsert via
RBAC (`az login` / managed identity — no keys, per T1 `disableLocalAuth`).

```bash
# Dry run (no creds)
python3 data-platform/scripts/csa/csa-seed-response-levers.py --dry-run

# Live seed (RBAC)
export CSA_COSMOS_ENDPOINT="https://cosmos-csa-ihzhhpf-sit.documents.azure.com:443/"
python3 data-platform/scripts/csa/csa-seed-response-levers.py
```

## Tests

```bash
cd data-platform/scripts/csa
python3 -m unittest discover -s tests -v
```

The Cosmos smoke suite (`test_cosmos_smoke.py`) is **skipped** unless
`CSA_COSMOS_ENDPOINT` is set — CI stays green without live credentials.
