# ADR-0034: Fabric IQ (Preview) demo-scope artefacts in westus2

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-07-18 |
| **Author** | Urs Rüegg |
| **Related** | [ADR-0013 (temporary US-region demo scope)](0013-temporary-us-region-demo-scope.md), [ADR-0014 (Fabric IQ ontology backbone)](0014-fabric-iq-ontology-target-backbone-ga-gated.md), [ADR-0016 (no PHI in demo)](0016-no-phi-in-mvp-demo-scope.md), [ADR-0033 (Fabric Data Agent as Foundry grounding tool)](0033-fabric-data-agent-as-foundry-grounding-tool.md), [GitHub issue #251](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/251) |
| **Design source** | [Fabric IQ (Preview) demo showcase design](../superpowers/specs/2026-07-18-fabric-iq-preview-demo-showcase-design.md) |

## Context

The Fabric → Foundry grounding seam from Slice 0 is proven live in SIT by
[ADR-0033](0033-fabric-data-agent-as-foundry-grounding-tool.md), but it still
runs synthetically: no live Fabric IQ artefacts exist. A repeatable Tier-3 demo
requires the operational Fabric IQ ontology, a OneLake Data Product, a
"Hospital Capacity" Domain, and a Fabric Data Agent. Both the Foundry `ooa`
agent, through its native Fabric connection, and the Container Apps agent-host
adapter consume those artefacts live.

Fabric IQ and the Fabric Data Agent are Preview capabilities. This ADR therefore
records only the demo-scope artefact decision; it does not place Fabric IQ on the
regulated critical path.

## Decision

Adopt the Fabric IQ demo-scope artefacts in the existing `westus2` Fabric
workspace `f3af9733-9503-4e92-98f9-a901d96f1c87`:

* Operational Fabric IQ ontology built from the `capacity-dashboard` semantic
  model, with the first bed-state time-series binding.
* OneLake Data Product containing the gold lakehouse tables, Direct Lake
  semantic model, and operational ontology.
* OneLake "Hospital Capacity" Domain that makes the data product discoverable.
* Fabric Data Agent over the semantic model, lakehouse, and ontology, returning
  concept-level `hcp:*` citations and propagating the ADR-0016 refusal.
* Foundry `ooa` native Fabric connection and agent-host live adapter consumption
  of the published Data Agent.

The adoption is synthetic-only, contains no PHI, is read-only grounding, and live
registration remains approval-gated by AGENTS.md §4. This supplements
[ADR-0033](0033-fabric-data-agent-as-foundry-grounding-tool.md) and is bounded
by:

* [ADR-0013](0013-temporary-us-region-demo-scope.md): `westus2` is the sole
  permitted preview and synthetic lane under exception
  `EX-2026-07-02-westus2-demo`, expiring 2026-09-30.
* [ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md): this delivers
  gate G-A in demo scope only, namely the operational Fabric IQ layer and first
  bed-state time-series binding; it is not the regulated GA path.
* [ADR-0016](0016-no-phi-in-mvp-demo-scope.md): no PHI, no direct identifiers,
  and no re-identification output are allowed.

Alternatives considered:

* Keep the seam synthetic-only. Rejected because it does not prove Fabric IQ, the
  OneLake Data Product, or the Data Agent live path.
* Build the demo artefacts in `eastus2` beside the Foundry control plane.
  Rejected for now because the Fabric workspace and gold data are already live
  in `westus2`, ADR-0013 scopes the demo lane there, and the region move is a
  Sprint 19 responsibility.

## Consequences

* **Positive:** creates a repeatable Tier-3 demo, exercises the real Fabric to
  Foundry seam end-to-end, advances `FR-ONT-008` from synthetic to live demo
  grounding, and satisfies ADR-0014 gate G-A in the bounded demo scope.
* **Negative / risks:** depends on Preview API stability, tenant-admin Fabric
  Copilot toggles, and cross-geo processing for Copilot. The demo must sunset
  back to `switzerlandnorth` when target services reach Swiss GA, and these
  artefacts remain demo-grade rather than certified production governance
  assets.

## Review triggers

* Fabric IQ, Fabric Data Agent, or Foundry native Fabric connection Preview
  contracts change materially.
* The ADR-0013 exception `EX-2026-07-02-westus2-demo` is renewed, expires, or is
  superseded by a Switzerland-region GA decision.
* A proposal attempts to reuse the demo artefacts for regulated or PHI-bearing
  scope.
* Sprint 19 changes the target region topology for Fabric and Foundry.
