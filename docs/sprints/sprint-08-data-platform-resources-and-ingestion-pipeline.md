# Sprint 08 - Data Platform Resources and Data Ingestion Pipeline (Superpowers Execution)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-14 |
| **Author** | GitHub Copilot |
| **Status** | Planned |
| **Previous Version** | - (initial sprint baseline) |

## Sprint Goal

Establish all data-platform resources and the end-to-end data ingestion
pipeline required to operate the patient capacity planning data product
delivered in Sprint 07.

The sprint stands up a SQL Server source (assumed KIS database) as the
ingestion entry point, lands and curates data through Microsoft Fabric and
OneLake, publishes the Data Product Semantic Model for Power BI consumption,
and provides a real-time capacity simulation service that emits continuous
new-demand records to exercise the streaming path end to end.

Execution follows the Superpowers Basic Workflow as the mandatory model,
consistent with Sprint 07.

## Source Baseline

1. [docs/PRD.md](../PRD.md)
2. [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
3. [docs/DATA.md](../DATA.md)
4. [docs/COMPLIANCE.md](../COMPLIANCE.md)
5. [docs/SECURITY.md](../SECURITY.md)
6. [docs/INFRASTRUCTURE.md](../INFRASTRUCTURE.md)
7. [docs/INTEGRATION.md](../INTEGRATION.md)
8. [docs/ALM_PLAN.md](../ALM_PLAN.md)
9. [docs/TEST.md](../TEST.md)
10. [docs/sprints/sprint-07-data-platform-and-data-products-superpowers.md](sprint-07-data-platform-and-data-products-superpowers.md)
11. [docs/sprints/sprint-07/brainstorming-ingestion-pipeline-slice.md](sprint-07/brainstorming-ingestion-pipeline-slice.md)
12. [docs/sprints/sprint-07/brainstorming-policy-evidence-slice.md](sprint-07/brainstorming-policy-evidence-slice.md)
13. [docs/superpowers/specs/2026-06-12-patient-capacity-data-product-design.md](../superpowers/specs/2026-06-12-patient-capacity-data-product-design.md)
14. [docs/adr/0003-swiss-regional-inference-for-phi.md](../adr/0003-swiss-regional-inference-for-phi.md)
15. [docs/adr/0004-block-global-and-data-zone-for-phi.md](../adr/0004-block-global-and-data-zone-for-phi.md)

## Sprint Scope

### In scope

1. Provision data-platform Azure resources (Fabric capacity, OneLake workspace
   and lakehouses, SQL Server source instance for KIS, supporting Key Vault,
   Storage, Log Analytics) as IaC under `infra/`.
2. Stand up the end-to-end ingestion pipeline from SQL Server (KIS) into
   Fabric / OneLake bronze, silver, and gold zones aligned to the Sprint 07
   data contracts.
3. Curate and publish the Data Product Semantic Model for Power BI consumption
   from the gold zone.
4. Implement and deploy a Real-Time Capacity Simulation service that emits
   continuous synthetic demand records into the streaming ingestion path,
   driven by an evidence-based situational profile.
5. Wire Fabric resources (Dataflows / Pipelines / Eventstream / Lakehouse /
   Semantic Model) to support the end-to-end process.
6. Enforce Superpowers stage-gates for design, planning, execution, review,
   and closure for every slice.
7. Capture weekly KPI evidence for throughput, quality, and reliability.

### Review-driven constraints (mandatory)

1. Hospital Operations abstraction is preserved: control unit is the
   Hospitalisation Episode, not the patient.
2. Minimal-Invasive Data Architecture is preserved: no PII in the planning
   platform; pseudonymised identifiers only across all zones and the Semantic
   Model.
3. KIS identity layer is kept separated from the planning metadata layer at
   the network, identity, and storage boundary.
4. Swiss data residency per [ADR-0003](../adr/0003-swiss-regional-inference-for-phi.md)
   and [ADR-0004](../adr/0004-block-global-and-data-zone-for-phi.md) applies
   to all provisioned resources, including Fabric capacity placement.
5. Data quality controls (validation rules and completeness thresholds) are
   enforced at ingestion and curation boundaries, not only at contract
   authoring time.
6. The Real-Time Capacity Simulation service must produce only metadata-only,
   pseudonymised records consistent with `DC-DEMAND-ENCOUNTER-v1` and the
   `purposeTags` / `residency` envelope.
7. Governance traceability is explicit (requirements, controls, evidence) for
   every scope slice.

### Out of scope

1. Removing approval gates or evidence contracts.
2. Reducing compliance controls for delivery speed.
3. Ingesting real KIS production data, real PHI, or any identifiable record.
4. Production deployment of Fabric workloads to customer tenants (this sprint
   targets SIT only).
5. Building consumer Power BI reports beyond the published Semantic Model;
   downstream reporting is a follow-up sprint.

## Superpowers Basic Workflow (Mandatory)

1. `brainstorming`
2. `using-git-worktrees`
3. `writing-plans`
4. `subagent-driven-development` or `executing-plans`
5. `test-driven-development`
6. `requesting-code-review`
7. `finishing-a-development-branch`

The same stage-runbook semantics established in Sprint 07 apply for Sprint 08
slices; concrete stage artifacts will be generated through the Stage 1
brainstorming outputs for this sprint.

## Planned Artifacts

1. `docs/sprints/sprint-08/README.md` (sprint pack index, created in Stage 1)
2. `docs/sprints/sprint-08/stage-runbook.md`
3. `docs/sprints/sprint-08/issue-body-templates.md`
4. `docs/sprints/sprint-08/checkpoint-matrix.md`
5. `docs/sprints/sprint-08/kpi-weekly-template.md`
6. `docs/sprints/sprint-08/brainstorming-fabric-onelake-foundation.md`
7. `docs/sprints/sprint-08/brainstorming-sql-kis-ingestion.md`
8. `docs/sprints/sprint-08/brainstorming-semantic-model-and-powerbi.md`
9. `docs/sprints/sprint-08/brainstorming-realtime-capacity-simulator.md`

## Definition of Done

1. Superpowers workflow is executed end-to-end for each in-scope delivery slice.
2. All data-platform resources are provisioned via IaC (Bicep modules under
   `infra/`) and pass `az bicep build` plus `what-if` in SIT.
3. End-to-end data ingestion pipeline runs successfully from the SQL Server
   (KIS) source through bronze, silver, and gold zones, validated against the
   Sprint 07 data contracts.
4. The Data Product Semantic Model is published in Fabric and consumable from
   Power BI with the metadata-only, pseudonymised contract envelope.
5. The Real-Time Capacity Simulation service can be kickstarted on demand,
   produces continuous capacity events conforming to the Sprint 07 contracts,
   and is consumed by the Fabric streaming path without breaking the gold
   contracts.
6. All Fabric resources required for the end-to-end process (capacity,
   workspaces, lakehouses, dataflows, pipelines, eventstream, semantic model)
   are established and configured with documented ownership.
7. Every merged PR includes requirement traceability and evidence contract
   fields per `.github/copilot-instructions.md` §6.
8. No deploy / delete action bypasses `approved-to-apply`.
9. Swiss data residency is verified for every provisioned resource and for the
   simulator's egress path.
10. Weekly KPI summary is produced from sprint execution data.
