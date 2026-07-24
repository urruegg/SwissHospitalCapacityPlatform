# ADR-0042: PROD Switzerland North GA Target + Standing Preview Exception for Curavias Demo

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-24 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Refines** | [ADR-0006](0006-preview-features-non-production-rule.md) by providing its required written Preview exception; [ADR-0037](0037-prod-region-switzerland-north-greenfield.md) by formalizing its GA-core + Preview-IQ posture. |
| **Related** | [ADR-0013](0013-temporary-us-region-demo-scope.md) (Accepted), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) (Accepted), [ADR-0034](0034-fabric-iq-demo-scope-artefacts.md), [issue #270](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/270) |
| **Consulted** | Product-owner decision from @urruegg on 2026-07-24; [docs/region-availability.yaml](../region-availability.yaml); [ADR-0037](0037-prod-region-switzerland-north-greenfield.md) evidence matrix |

## Context

[ADR-0037](0037-prod-region-switzerland-north-greenfield.md) pivoted PROD to
Switzerland North as the greenfield rebuild target. [ADR-0006](0006-preview-features-non-production-rule.md)
makes Preview features non-production for regulated data unless a written
governance exception exists.

The Curavias platform currently runs synthetic-only data and no PID/PHI:
metadata/episode-driven per [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) / F2,
and US-SIT synthetic-only per [ADR-0013](0013-temporary-us-region-demo-scope.md) /
F3. Therefore, the regulated-data rationale behind ADR-0006 does not bind the
current demo scope.

The product goal is to demonstrate the full Curavias stack end-to-end **in
Switzerland**, which requires running two Preview-tier Fabric IQ capabilities
in-region.

## Decision

1. **GA is the target maturity** for PROD Switzerland North.
2. A **standing, governance-approved Preview exception** permits named Preview
   features in PROD Switzerland North strictly for demonstrating the Curavias
   stack under synthetic/no-PHI scope.
3. The covered Preview features are:
   * `fabric-iq-ontology`
   * `fabric-data-agent`
4. Both covered features are region-listed Preview in Switzerland North per
   [docs/region-availability.yaml](../region-availability.yaml) and
   [ADR-0037](0037-prod-region-switzerland-north-greenfield.md)'s evidence
   matrix. The ontology is additionally subject to the per-capacity
   `FeatureNotAvailable` gate tracked in [issue #270](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/270).
5. All other BOM items deploy at their GA maturity.

## Exception record (ADR-0006 compliance)

| Field | Exception record |
|-------|------------------|
| Owner | @urruegg |
| Risk | Preview features carry no production SLA, may change or deprecate, and the ontology may hit the #270 per-capacity availability gate. |
| Compensating controls | Synthetic-only data and no PHI per ADR-0013/ADR-0016; GA-core PROD remains independent of the Preview IQ layer so a Preview failure never degrades the GA stack; IaC-reproducible deployment; per-capacity gate handled gracefully. |
| Rollback path | Disable the Preview module flag — `enableFabricFoundationModule` / IQ wiring — and redeploy. GA-core is unaffected. |
| Expiry / revisit | Whichever comes first: Fabric IQ Ontology + Data Agent reach GA in Switzerland North, then retire the exception; or real-Swiss-PHI onboarding, then re-evaluate under full ADR-0006 regulated-data rules. |

## Consequences

**Positive:**

* Unblocks the full in-region Curavias demo.
* Formalizes the previously implicit ADR-0037 GA-core + Preview-IQ posture.
* Satisfies ADR-0006's written-exception requirement.

**Negative / risks:**

* The ontology may still be blocked by #270's per-capacity gate. This is an
  availability blocker, not a policy blocker; record PROD as availability-blocked
  if the gate is hit.
* Preview features may regress.

## Availability blocker summary

The pre-sprint parity review finding from
[ADR-0037](0037-prod-region-switzerland-north-greenfield.md)'s evidence matrix
and [docs/region-availability.yaml](../region-availability.yaml) is:

* In Switzerland North, **all** required BOM items are **GA** except the two
  Preview items named in this ADR.
* GA items: fabric-capacity, fabric-workspace, onelake, lakehouse, eventstream,
  eventhouse, semantic-model, powerbi-report, azure-openai, foundry-agent-service,
  container-apps, app-fluent, logic-apps, fhir, storage, key-vault,
  managed-identity, entra, log-analytics, purview, policy-as-code.
* Preview items covered by this exception: `fabric-iq-ontology` and
  `fabric-data-agent`.

Non-availability caveats:

* Foundry "Class-A" private-IP agent topology is not offered in Switzerland North.
* The three agent models (`gpt-5`, `gpt-5-mini`, `o3`) are deployable only via
  `GlobalStandard` cross-geo routing. Regional `Standard` residency is limited to
  `gpt-4.1` / `gpt-4o`.
* Neither caveat is binding under the current synthetic/no-PHI scope.

## References

* [ADR-0006 — Preview features non-production rule](0006-preview-features-non-production-rule.md)
* [ADR-0037 — PROD Region Pivot to Switzerland North](0037-prod-region-switzerland-north-greenfield.md)
* [ADR-0013 — Temporary US-region demo scope](0013-temporary-us-region-demo-scope.md)
* [ADR-0016 — No PHI in MVP demo scope](0016-no-phi-in-mvp-demo-scope.md)
* [ADR-0034 — Fabric IQ demo-scope artefacts](0034-fabric-iq-demo-scope-artefacts.md)
* [docs/region-availability.yaml](../region-availability.yaml)
* [Issue #270 — Fabric IQ Ontology per-capacity `FeatureNotAvailable` gate](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/270)
