# ADR-0015 — Skip SQL for MVP demo

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Supersedes (scoped)** | Sprint 08 SQL KIS ingestion assumption (Sprint 08 doc §Sprint Scope item 1–2) — **for MVP demo scope only; a future PROD Swiss deployment may reintroduce SQL if a customer KIS integration requires it.** |
| **Related** | [ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md), [ADR-0013](0013-temporary-us-region-demo-scope.md), [ADR-0001](0001-ga-only-mvp-critical-path.md), [ADR-0002](0002-defer-fabric-iq-ontology-from-mvp.md) (superseded by ADR-0014) |

## Context

Sprint 08 planned a SQL Server instance in Azure as the KIS-simulation source, with a Bronze → Silver → Gold notebook chain landing data into OneLake. Sprint 00 discovered MCAPS regional restrictions blocking Azure SQL in `westus2` (and 5 other regions). More importantly, the MVP demo is **not a KIS integration** — it's a showcase of the platform's shape. Introducing SQL adds a stateful DB tier that is (a) not needed for the demo narrative, (b) blocked by MCAPS in the demo region, and (c) misaligned with the "no PHI, synthetic-only" principle since a KIS-shaped SQL implies real hospital data flow.

## Decision

For the MVP demo scope, the platform ingests data via **two Fabric-native paths only**:

1. **Reference / master data** — direct-to-lakehouse file upload (CSV → `bronze/master-data/`), Fabric Spark notebook chain (`bronze → silver → gold/reference/`), and REST-based Fabric portal upload as a fallback when the CI pipeline is not available.
2. **Simulated operational data** — Event Hubs → Fabric Eventstream → Delta append into `bronze/eventstream/`, Spark notebook chain to `silver/eventstream/` and `gold/patient-flow/`.

No Azure SQL, no SQL Managed Instance, no Fabric Data Warehouse SKU. The `source-sql` Bicep module remains in the tree (Sprint 00 delivered it as ready-to-flip) but stays disabled behind `enableSourceSqlModule=false`.

## Consequences

**Positive:**

- Removes an entire service tier (SQL + PrivateLink + SQL MI-vs-Flex-vs-vCore choice + backup + failover) from Sprint 09 scope.
- Aligns cleanly with the demo-scope + no-PHI baseline (ADR-0016).
- Unblocks MCAPS-blocked regions.
- Preserves the Bronze → Silver → Gold discipline via Fabric Spark notebooks, so the pattern is intact.

**Negative:**

- No end-to-end KIS-integration demo. When a customer PROD deployment needs SQL (customer KIS), a new ADR must reverse this decision for that scope.

**Governance action:** Update `docs/INFRASTRUCTURE.md` to reflect SQL-optional posture; note in `sprint-08` retrospective that the SQL track is deferred.

## Review triggers

Re-open this ADR when any of the following occurs:

1. A customer PROD deployment starts and requires KIS integration.
2. MCAPS lifts the regional SQL block in `westus2`.
3. A follow-up sprint reintroduces SQL for a specific use case (e.g. Master Data Management, not KIS).
