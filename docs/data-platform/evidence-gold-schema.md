# Evidence Gold Star Schema

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | — (initial) |

Gold star schema for the Sprint 14 Showcase Evidence data product, produced by
the medallion notebooks under
[`data-platform/notebooks/evidence/`](../../data-platform/notebooks/evidence/).
Naming: snake_case tables with a `gold.` schema prefix (per PR #153
reconciliation).

## Dimensions

| Table | Grain | Key columns |
| --- | --- | --- |
| `gold.dim_resource` | one BOM item | `resource_key` (= `bom-*` id), `name`, `type`, `category`, `sku` |
| `gold.dim_region` | one region | `region_key` (`Switzerland North`, `West Europe`) |
| `gold.dim_track` | one delivery track | `track_key` (`T-SHOW`, `T-PROD`) |
| `gold.dim_maturity_status` | one maturity | `maturity_key` (`GA`, `Preview`, `NotAvailable`) |
| `gold.dim_requirement` | one FR/NFR | `requirement_key`, `family`, `kind`, `title`, `mvp` |
| `gold.dim_adr` | one ADR | `adr_key`, `title`, `status`, `decisionSummary` |
| `gold.dim_environment` | one environment | `environment_key` (`dev`, `sit`, `prod`) |
| `gold.dim_date` | one as-of date | `date_key` (ISO date) |

## Facts

| Table | Grain | Measures / attributes |
| --- | --- | --- |
| `gold.fact_availability_evidence` | resource × region | `maturity_key`, `date_key`, `verifiedBy`, `sourceUrl` |
| `gold.fact_bom_deployment` | infra resource | `resourceType`, `modulePath` (stub — ARG deferred, design spec §2.2) |
| `gold.fact_readiness_snapshot` | resource × track | `status` (`Ready`/`Blocked`), `showcaseOnly`, `blockingReason`, `region` |
| `gold.fact_readiness_summary` | track | `readyCount`, `total`, `readyPct` + GA-parity gap |

## Bridges

| Table | Relates |
| --- | --- |
| `gold.bridge_resource_dependency` | resource → depends-on resource (`edge_type`) |
| `gold.bridge_requirement_resource` | requirement ↔ realising resource |
| `gold.bridge_requirement_adr` | requirement ↔ governing ADR (`relationship`) |

## Provenance

Every dimension carries `sourcePath` + `sourceCommit`; availability facts
additionally carry `verifiedBy` + as-of `date_key`. This is the contract that
lets every presenter-whiteboard card render provenance (design spec §5, §10).
