# ADR-0014 — Fabric IQ Ontology as target semantic backbone (GA-gated)

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Supersedes** | [ADR-0002](0002-defer-fabric-iq-ontology-from-mvp.md) — full supersession. ADR-0002 is retained as an accepted-but-superseded record. |
| **Related** | [ADR-0001](0001-ga-only-mvp-critical-path.md) (GA-only critical path — **unchanged**), [ADR-0006](0006-preview-features-non-production-rule.md) (preview features non-production for regulated data — **unchanged**), [ADR-0003](0003-swiss-regional-inference-for-phi.md) and [ADR-0004](0004-block-global-and-data-zone-for-phi.md) (Swiss residency for PHI — **unchanged**), [ADR-0013](0013-temporary-us-region-demo-scope.md) (temporary US demo-scope carve-out — compatible; preview validation permitted in demo scope only) |
| **Realises** | [AMA HCC/North Star review §9.1 H-01](../reviews/2026-07-01-ama-hcc-northstar-review.md#91-high-priority-sprint-09-scope) — proposed as "ADR-0005 (superseding ADR-0002)". Renumbered to **ADR-0014** because `docs/adr/0005-*` is already assigned to *approve-react-channel-as-ga-safe*. |
| **Related requirements** | `FR-ONT-001…007`, `NFR-ONT-001`, `FR-GOV-ONT-001…003` (proposed families — see [AMA review §5.1](../reviews/2026-07-01-ama-hcc-northstar-review.md#51-ontology-requirements-new-family-fr-ont--nfr-ont)), existing `NFR-AI-002/003/004`, `NFR-MAINT-002/004` |

## Context

[ADR-0002](0002-defer-fabric-iq-ontology-from-mvp.md) (Accepted 2026-06-01) excluded Fabric IQ Ontology from MVP critical-path scope and moved it to a post-MVP feature wave, with a single review trigger: *"Re-evaluate when Microsoft publishes GA status and confirmed regional support for Switzerland deployment scope."*

The 2026-07-01 AMA HCC & North Star review ([docs/reviews/2026-07-01-ama-hcc-northstar-review.md](../reviews/2026-07-01-ama-hcc-northstar-review.md)) consolidated two companion analyses and produced a design outcome that materially changes what the ontology is *for*:

1. The platform's target scope widens from a three-use-case MVP (ED forecast + bed state + discharge) to an **integral Hospital Command Center (HCC)** covering beds, OR, staff, rooms and equipment — see [AMA review §1](../reviews/2026-07-01-ama-hcc-northstar-review.md#1-executive-summary) and [F-P-01](../reviews/2026-07-01-ama-hcc-northstar-review.md#31-product--business-findings).
2. Cross-resource consistency, forecast/simulation traceability and copilot grounding all require a **shared semantic backbone**, not just per-surface data contracts — see [F-A-02](../reviews/2026-07-01-ama-hcc-northstar-review.md#32-architecture--design-findings), [F-A-03](../reviews/2026-07-01-ama-hcc-northstar-review.md#32-architecture--design-findings), [F-AI-01](../reviews/2026-07-01-ama-hcc-northstar-review.md#34-ai--agent-findings).
3. Fabric IQ Ontology remains **preview**, with **no committed Switzerland-region GA date** at the time of writing ([R-01](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-key-risks-h--high-m--medium-l--low), [Open Question 1](../reviews/2026-07-01-ama-hcc-northstar-review.md#38-explicitly-open-questions-raised)). This is a hard blocker for putting Fabric IQ on the regulated MVP critical path under [ADR-0001](0001-ga-only-mvp-critical-path.md) and [ADR-0006](0006-preview-features-non-production-rule.md).
4. Under [ADR-0013](0013-temporary-us-region-demo-scope.md), preview services (including Fabric IQ Ontology) **may** be used in the `westus2` demo scope for **synthetic data only** — this provides a safe validation lane that does not require Swiss-region GA.

The design gap is therefore not *whether* to adopt Fabric IQ Ontology, but *how* to commit to it as the target backbone while (a) preserving all current guardrails and (b) de-risking against preview status and unknown GA timing.

ADR-0002's "defer indefinitely" posture no longer matches the design intent expressed in the AMA outcome. A superseding decision is required so that Sprint 09 can stand up the Minimum Viable Ontology (MVO) against a coherent target-state architecture rather than an implicitly-deferred one.

## Decision

**Adopt Fabric IQ Ontology as the target operational semantic backbone for the integral HCC tier, gated on Switzerland-region GA. Author the reference layer (BFO / OBO in OWL/RDF) in parallel and portably, so that operational realisation is de-risked against Fabric IQ preview status and Switzerland-region GA timing.**

The decision has five parts. All five must hold; violating any one requires a further superseding ADR.

### 1. Two-layer ontology, one intent

The ontology is realised in two layers, held in sync by a governed crosswalk:

- **Reference layer** — authored in **OWL/RDF**, imports [BFO (ISO/IEC 21838-2:2021)](https://basic-formal-ontology.org/), [OMRSE](https://obofoundry.org/ontology/omrse.html), [OGMS](https://obofoundry.org/ontology/ogms.html), [OOSTT](https://obofoundry.org/ontology/oostt.html) and the Goyer et al. healthcare-system classes; adds the platform-specific `CapacityUnit` abstraction and its subtypes (`Bed`, `ORSlot`, `Room`, `StaffShift`, `Device`). Portable, tool-neutral, versioned as a first-class asset under `docs/ontology/`.
- **Operational layer** — realised in **Fabric IQ Ontology**, auto-generated from the Sprint-09 Power BI semantic model per the [Fabric IQ lab pattern](../reviews/2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md), with static bindings (lakehouse) and time-series bindings (eventhouse). Live surfaces (dashboards, copilot, agents, simulation) read this layer.
- **Crosswalk** — `docs/ontology/crosswalk.md`: reference-layer class ↔ Fabric IQ entity type ↔ data contract. Versioned, reviewable, and enforced by a **CI conformance check** in the delivery pipeline.

### 2. Regulated critical path stays GA-only

[ADR-0001](0001-ga-only-mvp-critical-path.md) and [ADR-0006](0006-preview-features-non-production-rule.md) remain **fully in force**. In particular:

- The operational layer **may not** be used in `switzerlandnorth` PROD paths carrying PHI until (a) Fabric IQ Ontology is GA in `switzerlandnorth` **and** (b) Microsoft publishes DPA/data-residency equivalence with GA Fabric components.
- Until both conditions hold, the regulated MVP critical path uses GA Fabric assets + curated semantic model + data contracts, exactly as ADR-0002 originally prescribed. Ontology-driven surfaces in that scope are **advisory only**, sourced from the reference layer or curated views, never from a preview service.
- The `westus2` demo scope of [ADR-0013](0013-temporary-us-region-demo-scope.md) is the **sole permitted lane** for validating the operational layer against real preview Fabric IQ Ontology behaviour, with synthetic data only.

### 3. Sprint 09 delivers the Minimum Viable Ontology (MVO)

- **MVO entity types**: `Hospital`, `Specialty`, `HospitalService`, `Ward` (new), `Room` (new), `Bed` (new), `Encounter`, `Patient` role, `CareTeam`, `Equipment`, and **`ORSlot`** (new — the OR steering anchor).
- **First time-series binding**: bed-state changes (occupied / available / blocked / cleaning). OR-status and monitoring-device time series follow in Sprint 10/11.
- **Reference-layer skeleton**: authored in parallel under `docs/ontology/`. Publishes the `CapacityUnit` abstraction and the initial imports. Not required to be OBO-published in Sprint 09 — internal portability is sufficient.
- If Switzerland-region GA is not confirmed by the Sprint 09 mid-point, the operational layer may fall back to an equivalent property-graph representation on GA Fabric services for the regulated path; the demo-scope operational layer continues to run on Fabric IQ Ontology preview.

### 4. Governance model (OBO-inspired)

- **Named semantic / ontology owner** in the data-governance RACI (see [OPERATIONS.md](../OPERATIONS.md)) — realises `FR-GOV-ONT-001`.
- **Semantic change workflow** — proposal → domain-owner review → versioned release → downstream impact check → PR merge; mirrors the existing data-contract breaking-change control (`NFR-MAINT-002`). Realises `FR-GOV-ONT-002`.
- **Two-layer conformance CI check** — the reference↔operational crosswalk is auditable in every PR that touches either layer. Fails the build on missing or drifted mappings. Realises `FR-GOV-ONT-003` and `NFR-ONT-001`.
- **Principles**: realism (align to OBO Foundry), univocity (one term / one meaning), orthogonality / reuse (import; do not duplicate published ontologies).

### 5. Explicit go/no-go gates

Sprint 09 does not commit any of the following without an explicit gate:

| Gate | Trigger | Fallback if not met |
| --- | --- | --- |
| **G-A — MVO in demo scope** | Reference-layer skeleton authored + Fabric IQ operational layer generated in `westus2` demo scope, first time-series binding on bed state | No fallback — this is the Sprint 09 acceptance evidence per [AMA §11.3](../reviews/2026-07-01-ama-hcc-northstar-review.md#113-sprint-09-acceptance-evidence-proposed) |
| **G-B — Regulated preview use** | Formal ADR-0013-style time-limited exception in `policy/exceptions.json` for any regulated-path preview use | Regulated path stays on curated GA layer; ontology grounding is advisory-only via reference layer |
| **G-C — Fabric IQ Switzerland GA** | Microsoft publishes GA date + DPA equivalence for `switzerlandnorth` | Regulated operational layer stays on the property-graph fallback of §3, indefinitely |

## Consequences

**Positive:**

- Establishes an unambiguous target architecture for the integral HCC tier and Fabric IQ Ontology, replacing ADR-0002's implicit deferral with an explicit gated commitment.
- Preserves every existing guardrail: GA-only critical path ([ADR-0001](0001-ga-only-mvp-critical-path.md)), preview-non-production for regulated data ([ADR-0006](0006-preview-features-non-production-rule.md)), Swiss residency for PHI ([ADR-0003](0003-swiss-regional-inference-for-phi.md) / [ADR-0004](0004-block-global-and-data-zone-for-phi.md)) — none is amended or weakened by this ADR.
- Portable reference layer (OWL/RDF) makes the platform robust to Fabric IQ product-timeline slippage, vendor-strategy change, and multi-cloud provider requirements — realises `NFR-MAINT-002` and `NFR-MAINT-004`.
- Concept-level grounding for copilot and agents strengthens `NFR-AI-002/003/004` (grounded, traceable, region-pinned inference).
- Two-layer conformance CI turns "ontology drift" from a theoretical risk into a build-time failure, addressing risks [T-02](../reviews/2026-07-01-ama-hcc-northstar-review.md#61-technical-risks) and [D-17](../reviews/2026-07-01-ama-hcc-northstar-review.md#4-deviation-analysis--best-practice-vs-current-state).

**Negative / risks:**

- Two-layer maintenance overhead — requires a named semantic owner, CI check, and disciplined change workflow ([R-05](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-key-risks-h--high-m--medium-l--low), [R-08](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-key-risks-h--high-m--medium-l--low)).
- The `westus2` demo scope + `switzerlandnorth` target scope must remain semantically aligned for the reference layer to serve both — validates the [ADR-0013](0013-temporary-us-region-demo-scope.md) time-limited posture; sunset back to `switzerlandnorth` remains the target.
- If Fabric IQ Switzerland GA slips beyond the exception window in [ADR-0013](0013-temporary-us-region-demo-scope.md) (`EX-2026-07-02-westus2-demo`, expiry 2026-09-30), demo scope must either be renewed or the fallback of §3 becomes the long-term operational layer for the regulated path.
- Scope creep risk (adds MVO + ADR + PRD family + crosswalk + CI in one sprint) — bounded by the explicit gates in §5 and the MVO-first discipline in [AMA §11.2](../reviews/2026-07-01-ama-hcc-northstar-review.md#112-mvo-scope-for-sprint-09-proposed).

**Governance actions triggered by this ADR:**

- Update [ADR-0002](0002-defer-fabric-iq-ontology-from-mvp.md) status header to `Status: Superseded by ADR-0014`. Content otherwise unchanged (accepted-but-superseded record).
- Extend [PRD.md](../PRD.md) with `FR-ONT-*` (minimum) — realises AMA H-03 / RB-06.
- Nominate the semantic / ontology owner in [OPERATIONS.md](../OPERATIONS.md) — realises AMA H-04 / RB-07.
- Author `docs/ontology/` folder with the reference-layer skeleton and `docs/ontology/crosswalk.md` in Sprint 09 — realises AMA H-05 / RB-08 / RB-11.
- Register the "Fabric IQ Switzerland GA + DPA equivalence" go/no-go in [OPERATIONS.md](../OPERATIONS.md) risk register — realises AMA H-06 / RB-09.
- Add the CI conformance check to `.github/workflows/` (design in Sprint 09; enforcement may slip to Sprint 10 per AMA §11.1 H-05).
- Update [sprint-09 §0 RB-04](../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md#0--refresh-backlog-must-do-before-execution) to point to this ADR (was placeholder ADR-0005).

## Review triggers

Re-open this ADR when any of the following occurs:

1. Microsoft publishes a firm GA date for Fabric IQ Ontology in `switzerlandnorth` **and** DPA equivalence with GA Fabric components. Triggers the migration path in §3 for the regulated-path operational layer.
2. The [ADR-0013](0013-temporary-us-region-demo-scope.md) `westus2` demo exception (`EX-2026-07-02-westus2-demo`) is renewed, changed or allowed to lapse without regulated-path GA readiness.
3. A cantonal instruction imposes semantic-layer-specific controls that either enforce or forbid a specific ontology framework (see [R-07](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-key-risks-h--high-m--medium-l--low)).
4. The MVO delivered in Sprint 09 reveals that the target subtype set (`Bed`, `ORSlot`, `Room`, `StaffShift`, `Device`) or the first time-series binding (bed state) needs a structurally different modelling choice.
5. Microsoft changes Fabric IQ Ontology's preview scope, licensing, or data-residency posture in a way that materially affects any part of §1–§5.

## References

- Superseded ADR: [ADR-0002](0002-defer-fabric-iq-ontology-from-mvp.md)
- In-force guardrails: [ADR-0001](0001-ga-only-mvp-critical-path.md), [ADR-0003](0003-swiss-regional-inference-for-phi.md), [ADR-0004](0004-block-global-and-data-zone-for-phi.md), [ADR-0006](0006-preview-features-non-production-rule.md), [ADR-0013](0013-temporary-us-region-demo-scope.md)
- Design source: [AMA HCC & North Star Ontology review (2026-07-01)](../reviews/2026-07-01-ama-hcc-northstar-review.md) — [§1](../reviews/2026-07-01-ama-hcc-northstar-review.md#1-executive-summary), [§3.2](../reviews/2026-07-01-ama-hcc-northstar-review.md#32-architecture--design-findings), [§5.1](../reviews/2026-07-01-ama-hcc-northstar-review.md#51-ontology-requirements-new-family-fr-ont--nfr-ont), [§9.1 H-01](../reviews/2026-07-01-ama-hcc-northstar-review.md#91-high-priority-sprint-09-scope), [§11](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff)
- Companion analyses: [IKM/HCC vs Swiss Capacity Platform Analysis](../reviews/2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md), [HCC North Star Ontology Model Analysis](../reviews/2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md)
- Sprint slot: [sprint-09-master-data-simulation-and-capacity-dashboard.md](../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md) — §0 RB-04 (this ADR), RB-05 (MVO), RB-07 (owner), RB-08 (crosswalk + CI), RB-09 (GA tracker), RB-11 (OWL/RDF skeleton)
- Reference-ontology imports: BFO (ISO/IEC 21838-2:2021); OMRSE; OGMS; OOSTT; Goyer, Fabry, Barton & Ethier — *An ontology for healthcare systems* (ICBO 2022); OBO Foundry principles
- Fabric IQ: Microsoft Learn — *"Build an ontology from a semantic model"* (preview)
