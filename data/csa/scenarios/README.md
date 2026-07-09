# CSA seeded scenarios

Sprint 16 T6 — eight canonical what-if crisis scenarios for the Crisis / Scenario
Agent (CSA), one per scenario family (F1–F8) from the anchor idea
(`docs/superpowers/ideas/CSA-WhatIf-Scenario-Research-and-Catalogue.md`) and the
design spec (`docs/superpowers/specs/2026-07-09-sprint-16-csa-design.md` §7).

Each YAML validates against
[`data-platform/scripts/csa/schema/scenarios.schema.json`](../../../data-platform/scripts/csa/schema/scenarios.schema.json).

| File | Family | Default tier | MVP |
| ---- | ------ | ------------ | --- |
| `helipad-elevator-failure.yaml` | F1 | 2 | no |
| `ward-specialists-at-congress.yaml` | F2 | 2 | no |
| `crans-montana-burns-mci.yaml` | F3 | 3 | no |
| `cyberattack-hospital-services.yaml` | F4 | 3 | **yes** |
| `ventilator-supply-shortage.yaml` | F5 | 3 | no |
| `pediatric-virus-surge-rsv.yaml` | F6 | 2 | **yes** |
| `terror-attack-second-hit-risk.yaml` | F7 | 3 | no |
| `summer-heatwave-demand-surge.yaml` | F8 | 2 | **yes** |

The three `mvpRequired: true` scenarios are the ones run end-to-end in T9.

## Seeding

```bash
# validate only (no creds needed)
python3 data-platform/scripts/csa/csa-seed-scenarios.py --dry-run

# upsert into Cosmos (requires CSA_COSMOS_ENDPOINT + managed identity / creds)
python3 data-platform/scripts/csa/csa-seed-scenarios.py
```

The first upsert is manual; `csa-scenario-sync.yml` (T8) validates and upserts on
merge thereafter. Every `responseLevers` entry must reference a `leverId` seeded
by `csa-seed-response-levers.py`; the cross-reference is enforced by
`data-platform/scripts/csa/tests/test_scenarios.py`.
