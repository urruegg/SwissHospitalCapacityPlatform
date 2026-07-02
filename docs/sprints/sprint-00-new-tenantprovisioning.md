# Sprint 00 — New Tenant Provisioning

| Field | Value |
| ----- | ----- |
| **Version** | 0.1.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Status** | In progress |
| **Previous Version** | N/A |

## Goal

Rebuild SIT and PROD end-to-end in the new Entra tenant `1337187a-4c41-4da9-8fca-731bba7a4329` (`MngEnvMCAP164444.onmicrosoft.com`) with solution short name `ihzhhpf`, without disturbing the current tenant.

**Scope carve-out (D9 / [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md)):** deployment region is `westus2` for this sprint — demonstration / proof-of-technology scope only, synthetic sample data only, no PHI. Single subscription `66a9953a-df37-4c51-856c-9971b9bf3e03` hosts both SIT and PROD RGs. Sunset back to `switzerlandnorth` when target services reach Swiss GA or exception `EX-2026-07-02-westus2-demo` expires (2026-09-30).

## Scope

- W0 — Repo prep (rename `chhealthpf` → `ihzhhpf` in live/authoritative files)
- W1 — Tenant plane setup (developer trust, OIDC federation, subscription RBAC, GitHub env config, Fabric prereq)
- W2 — SIT deploy + smoke test
- W3 — PROD deploy + smoke test
- W4 — Cutover documentation (ADR-0012, OPERATIONS, AGENTS)
- W5 — This retrospective

Spec: [docs/superpowers/specs/2026-07-02-tenant-migration-design.md](../superpowers/specs/2026-07-02-tenant-migration-design.md) v1.1.0.
Plan: [docs/superpowers/plans/2026-07-02-tenant-migration-plan.md](../superpowers/plans/2026-07-02-tenant-migration-plan.md).

## Workstream evidence

_Populated during Task 20 (W5 execution)._

| Workstream | Start | End | Evidence links |
| ---------- | ----- | --- | -------------- |
| W0 | | | |
| W1 | | | |
| W2 | | | |
| W3 | | | |
| W4 | | | |

## Retrospective

_Populated during Task 20._

### What went well

### What didn't

### What to change next time

## References

- Runbook: [docs/runbooks/tenant-migration-runbook.md](../runbooks/tenant-migration-runbook.md)
- ADR-0012: [docs/adr/0012-tenant-migration-to-mcap164444.md](../adr/0012-tenant-migration-to-mcap164444.md)
