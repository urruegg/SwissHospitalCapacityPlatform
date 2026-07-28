# Master Data — Golden Source (single source of truth)

This tree is the **canonical, git-owned** master data for the platform. Both SIT
and PROD load it **identically** (no per-environment drift). CSVs here are
uploaded verbatim to each lakehouse `Files/master-data/<domain>/` by
`data-platform/scripts/upload_to_onelake.py`, then ingested by the medallion
notebooks.

## Domains

| Folder | Domain | Load into |
| ------ | ------ | --------- |
| `capacity/` | Operational capacity master data (9 CSVs). | `Files/master-data/capacity/` |
| `curavias-org-skills/` | Curavias organisation + skills master data (added in P1b). | `Files/master-data/curavias-org-skills/` |
| `bva/` | BVA cost/BOM master data product (7 CSVs). | `Files/master-data/bva/` |

## Load order (capacity)

Dimensions before facts/bridges: `dim_hospital`, `dim_disease`, `dim_specialty`,
`dim_hospital_service`, `dim_treatment`, `dim_drg`, `dim_ward_capacityunit`, then
`fact_capacity_baseline`, then `map_disease_treatment_specialty_service`.

## BVA cost/BOM data

The `bva/` domain contains synthetic, PHI-free master data for the Sprint 33 BVA
cost data product: the authoritative ROM ledger, hospital profiles, Azure BOM,
weekly Azure cost evidence, Copilot usage, team effort, and FX rates. The ROM
ledger in `bva_cost_element.csv` reconciles to CHF 1,300,000 one-time and CHF
1,250,000 annual run cost.

## Contract gate

`validate_master_data.py` (dependency-free) enforces file presence, PK
uniqueness, foreign-key integrity, and the no-PHI contract. CI:
`.github/workflows/master-data.yml`.

## Provenance & PHI

All data is **synthetic / anonymized** (Curavias demo; no PHI — ADR-0013,
ADR-0016). The `capacity/` CSVs originate from the 2026-06-29 AMA capacity
metadata review.
