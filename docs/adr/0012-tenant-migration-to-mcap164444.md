# ADR-0012 — Tenant migration to MCAP164444

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |

## Context

_To be filled during Task 19 (W4 execution) using actual migration evidence._

The Swiss Hospital Capacity Platform was originally deployed into the MCAP sandbox tenant `2dfb4d85-3ca7-474e-86eb-9ba3762d9474` (`MngEnvMCAP228255.onmicrosoft.com`). A new MCAP sandbox tenant `1337187a-4c41-4da9-8fca-731bba7a4329` (`MngEnvMCAP164444.onmicrosoft.com`) has been assigned to the solution and must become authoritative.

## Decision

_To be filled during Task 19._

Rebuild SIT and PROD in the new tenant end-to-end following the runbook at [docs/runbooks/tenant-migration-runbook.md](../runbooks/tenant-migration-runbook.md). The old tenant remains operational; teardown is deferred to a separate later decision.

## Consequences

_To be filled during Task 19 with actual execution evidence (dates, cost impact, remaining risks)._

## References

- Spec: [docs/superpowers/specs/2026-07-02-tenant-migration-design.md](../superpowers/specs/2026-07-02-tenant-migration-design.md) v1.1.0
- Plan: [docs/superpowers/plans/2026-07-02-tenant-migration-plan.md](../superpowers/plans/2026-07-02-tenant-migration-plan.md)
- Runbook: [docs/runbooks/tenant-migration-runbook.md](../runbooks/tenant-migration-runbook.md)
- Sprint report: [docs/sprints/sprint-00-new-tenantprovisioning.md](../sprints/sprint-00-new-tenantprovisioning.md)
- Prior ADR affecting region: [ADR-0003](0003-swiss-regional-inference-for-phi.md)
