# ADR-0043: Preview-tier services permitted in PROD Switzerland North for the Curavias demo (GA-only gate reserved for real go-live cut-over)

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-25 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Refines** | [ADR-0006](0006-preview-features-non-production-rule.md) (its written Preview exception) and [ADR-0042](0042-prod-switzerland-north-ga-target-standing-preview-exception.md) (generalises the named-feature exception into a standing demo-scope posture). |
| **Related** | [ADR-0013](0013-temporary-us-region-demo-scope.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md), [ADR-0037](0037-prod-region-switzerland-north-greenfield.md), [issue #255](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255) |
| **Consulted** | Product-owner decision from @urruegg on 2026-07-25; [docs/region-availability.yaml](../region-availability.yaml); ADR-0042 evidence matrix |

## Context

[ADR-0042](0042-prod-switzerland-north-ga-target-standing-preview-exception.md)
granted a **standing Preview exception** for PROD Switzerland North, but scoped
it to two **named** Preview features (`fabric-iq-ontology`, `fabric-data-agent`).
Subsequent demo work needs the same latitude for other Preview-tier capabilities
(and for target-state transports such as the skills-events Event Hub → Eventstream
rail), without opening a new named-feature exception each time.

The product goal remains: demonstrate the full Curavias stack end-to-end **in
Switzerland**, to show **what the technology stack makes possible today**. The
platform runs synthetic-only data with no PID/PHI ([ADR-0016](0016-no-phi-in-mvp-demo-scope.md)),
so the regulated-data rationale behind [ADR-0006](0006-preview-features-non-production-rule.md)
does not bind the current demo scope.

The **skills-events near-real-time lane** (WS-A4, [issue #255](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255))
was previously recorded with its `sourceMode=EventHub` transport "parked until
Fabric Swiss GA". That framing was over-conservative: **Eventstream is GA in
Switzerland North** ([docs/region-availability.yaml](../region-availability.yaml),
asOf 2026-07-09), Azure Event Hubs is GA there, PROD Fabric (`fabricihzhhpfprod`)
already runs in Switzerland North, and the PROD Event Hubs namespace
(`evh-ihzhhpf-prod-i62t`) already exists in-region. The only real blocker is an
out-of-band Fabric-managed connection, not a GA milestone.

## Decision

1. **Preview-tier Azure/Fabric services are permitted in PROD Switzerland North**
   strictly to demonstrate the Curavias stack under **synthetic / no-PHI** scope.
   This generalises ADR-0042 from two named features to a standing demo-scope
   posture, and satisfies ADR-0006's written-exception requirement for that scope.
2. The **GA-only gate applies solely to a real go-live (real-PHI) cut-over.**
   Proving value and the art of the possible in **Preview in Switzerland is
   sufficient** for the demo; work must not be re-parked behind a GA milestone
   unless it targets a real go-live cut-over.
3. **The skills-events `sourceMode=EventHub` flip is un-parked.** It is in fact
   **GA in Switzerland North** (Eventstream + Event Hubs), so it does not even
   consume this Preview exception; the "parked until Swiss GA" gate on it is
   lifted. Its only remaining prerequisite is the out-of-band Fabric-managed
   connection (`POST /v1/connections`).
4. **Environment isolation is preserved.** SIT (westus2 / eastus2, per enabled
   capacity) and PROD (Switzerland North) **do not share input services** —
   separate Event Hubs namespaces, resource groups, and regions
   (`evh-ihzhhpf-sit-y26y` vs `evh-ihzhhpf-prod-i62t`). New input services follow
   the per-environment, per-functional-domain pattern (a **dedicated skills-events
   Event Hub**, not shared with the capacity `events` rail).

## Exception record (ADR-0006 compliance)

| Field | Exception record |
|-------|------------------|
| Owner | @urruegg |
| Scope | PROD Switzerland North, synthetic/no-PHI Curavias demo only. |
| Risk | Preview-tier services carry no production SLA and may change or deprecate. |
| Compensating controls | Synthetic-only data and no PHI per ADR-0013/ADR-0016; GA-core PROD stays independent of any Preview capability so a Preview failure never degrades the GA stack; IaC-reproducible; per-environment input isolation. |
| Rollback path | Disable the Preview/target-state module flag (for the skills lane: keep `skillsEventstreamSourceMode='CustomEndpoint'`) and redeploy. GA-core is unaffected. |
| Expiry / revisit | Whichever comes first: the relevant capability reaches GA in Switzerland North; or real-Swiss-PHI onboarding, then re-evaluate under full ADR-0006 regulated-data rules and the GA-only cut-over gate. |

## Consequences

**Positive:**

* Removes the recurring need for a named-feature exception per Preview capability
  in the demo scope.
* Un-parks the skills-events Event Hub flip and any comparable target-state work
  in PROD Switzerland North.
* Keeps a hard GA-only gate exactly where it matters — real go-live cut-over.

**Negative / risks:**

* Preview-tier services may regress with no SLA; mitigated by synthetic/no-PHI
  scope and GA-core independence.
* Broader latitude requires discipline: each use must still stay within the
  synthetic/no-PHI demo scope recorded here.

## References

* [ADR-0006 — Preview features non-production rule](0006-preview-features-non-production-rule.md)
* [ADR-0042 — PROD Switzerland North GA target + standing Preview exception](0042-prod-switzerland-north-ga-target-standing-preview-exception.md)
* [ADR-0013 — Temporary US-region demo scope](0013-temporary-us-region-demo-scope.md)
* [ADR-0016 — No PHI in MVP demo scope](0016-no-phi-in-mvp-demo-scope.md)
* [ADR-0037 — PROD region pivot to Switzerland North](0037-prod-region-switzerland-north-greenfield.md)
* [docs/region-availability.yaml](../region-availability.yaml)
* [Issue #255 — Unified Curavias organisation spine + org/skills ontology](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255)
