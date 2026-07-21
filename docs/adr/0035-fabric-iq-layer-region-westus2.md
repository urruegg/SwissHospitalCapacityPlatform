# ADR-0035: PROD Fabric IQ Layer Stays in westus2 (eastus2 Fabric Quota = 0)

| Field | Value |
|-------|-------|
| **Status** | Accepted (scoped-superseded for PROD by [ADR-0037](0037-prod-region-switzerland-north-greenfield.md)) |
| **Date** | 2026-07-19 |
| **Decision-makers** | @urruegg |
| **Consulted** | Sprint 19 P6.1 deploy evidence; Fabric IQ readiness brainstorm |

> **2026-07-21 update:** PROD Fabric moves to `switzerlandnorth` per
> [ADR-0037](0037-prod-region-switzerland-north-greenfield.md) — live `az`
> confirmed swn Fabric quota is **0/512** (available), so PROD Fabric can
> co-locate with the rest of PROD and the westus2 cross-region placement this
> ADR describes is no longer needed for PROD. This ADR remains the record of the
> interim westus2 decision and the eastus2-quota-0 blocker behind it.

## Context

The [Fabric IQ to Foundry readiness design](../superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md)
records decision **D2 — "collocate the Fabric IQ layer in eastus2"** — whose
rationale is to remove the cross-region hop and two-region governance between
the Foundry control plane (eastus2, [ADR-0032](0032-foundry-control-plane-eastus2.md))
and the Fabric grounding surface.

Sprint 19 P6.1 attempted to create the PROD Fabric F2 capacity in eastus2 and
it **failed**:

> `BadRequest: The sum total of CapacityUnits of all Fabric capacities … must
> not exceed the regional quota … TotalCapacityUnits: 0, RegionalQuota: 0`

The `Microsoft.Fabric` usages API confirms the subscription
(`66a9953a-df37-4c51-856c-9971b9bf3e03`) has **0 CU** Fabric quota in eastus2
and **512 CU** in westus2. PROD Fabric (`fabricihzhhpfprod`, F2) was therefore
created in **westus2**, alongside the SIT Fabric capacity.

## Decision

The **PROD Fabric IQ layer (capacity, workspace, lakehouse, semantic model,
ontology, Data Agent, OneLake Data Product + Domain) runs in westus2** for the
demo / proof-of-technology scope. This **relaxes D2** of the readiness design:
collocation in eastus2 is not achievable without an eastus2 Fabric
quota-increase.

Consequences accepted:

- The **Foundry (eastus2) → Fabric (westus2) cross-region grounding hop
  remains** — identical to the current SIT topology and to the Sprint 18
  cross-region posture. Fabric is a region-flexible SaaS plane reachable over
  HTTPS; the seam config (`FABRIC_WORKSPACE_ID` + data-agent endpoint) is a
  variable-library value, so re-pointing to eastus2 later is a config change,
  not a rebuild.
- The readiness roadmap Phase 3 line "**sunset westus2 Fabric**" no longer
  applies to the PROD layer — westus2 *is* the PROD end-state. Only the SIT
  Fabric capacity remains a separate, environment-scoped resource.
- This is bounded by the demo scope of [ADR-0013](0013-temporary-us-region-demo-scope.md)
  (synthetic data only, US region, sunset to Swiss GA later) and does not touch
  the regulated Swiss critical path ([ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md),
  [ADR-0016](0016-no-phi-in-mvp-demo-scope.md)).

## Alternatives considered

- **File an eastus2 Fabric quota-increase and wait** — preserves D2 collocation
  but blocks the PROD Fabric IQ build on an approval of unknown latency.
  Rejected as the default; may be pursued later to converge on true eastus2
  collocation.
- **Move all Fabric (SIT + PROD) to a third region with headroom** — no benefit
  over westus2, which already has 512 CU, and adds churn.

## Revisit criteria

Revisit if the subscription obtains eastus2 Fabric quota, or when the platform
graduates to Swiss GA regions (`switzerlandnorth`) per ADR-0013 — at which point
the Fabric IQ layer re-points via variable library, not rebuild.
