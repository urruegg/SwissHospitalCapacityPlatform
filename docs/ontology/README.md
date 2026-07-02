# docs/ontology/ — Reference Ontology & Crosswalk

| Field | Value |
| ----- | ----- |
| **Version** | 0.1.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Status** | Draft — Sprint 09 skeleton (RB-11) |
| **Previous Version** | — (new folder) |
| **Owner** | Semantic / ontology owner *(nominated per [OPERATIONS.md v1.4.0](../OPERATIONS.md#roles-and-accountability-raci-baseline); incumbent TBD)* |

## Purpose

This folder is the **reference layer** of the two-layer ontology mandated by [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md). It is the portable, tool-neutral, versioned representation of the platform's semantic backbone — authored in OWL/RDF, importing established published ontologies (BFO, OMRSE, OGMS, OOSTT, Goyer et al. healthcare-system classes) and adding the platform-specific `CapacityUnit` abstraction and its subtypes.

The **operational layer** lives in Microsoft Fabric IQ (auto-generated from the Sprint-09 Power BI semantic model with static + time-series bindings) and is subject to the GA gates in [ADR-0014 §5](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#5-explicit-go-no-go-gates). The two layers are held in sync by the [crosswalk.md](crosswalk.md) artefact and a CI conformance check (see [RB-08 slice](#rb-08-ci-conformance-check-placeholder), delivered in a follow-up PR).

## Structure

| File | Purpose |
| ---- | ------- |
| [README.md](README.md) | This file. Purpose, structure, versioning, contribution workflow. |
| [reference-layer.ttl](reference-layer.ttl) | Turtle-format OWL skeleton: prefix declarations, `owl:imports`, and the `CapacityUnit` class family. |
| [crosswalk.md](crosswalk.md) | Governed crosswalk: reference-layer class ↔ Fabric IQ entity type ↔ data contract. Reviewable in every PR that touches either layer. |

## Requirement Anchors

- [`FR-ONT-001`](../PRD.md#h-semantic-ontology) — Reference ontology grounded in BFO + OMRSE + OGMS + OOSTT + Goyer et al.
- [`FR-ONT-003`](../PRD.md#h-semantic-ontology) — Capacity-unit subtypes (`Bed`, `ORSlot`, `Room`, `StaffShift`, `Device`).
- [`FR-ONT-007`](../PRD.md#h-semantic-ontology) — Provider extension pattern.
- [`FR-GOV-ONT-002`](../PRD.md#h-semantic-ontology) — Semantic change workflow.
- [`FR-GOV-ONT-003`](../PRD.md#h-semantic-ontology) — CI conformance check (RB-08 follow-up).
- [`NFR-ONT-001`](../PRD.md#h-semantic-ontology-sprint-9) — Versioning + governance discipline + CI check.

## Versioning

The ontology follows the same SemVer discipline as data contracts (`NFR-MAINT-002`):

- **MAJOR** — remove or rename a class, property or subtype relation used by an operational binding.
- **MINOR** — additive: new class, new property, new subtype relation, new import.
- **PATCH** — editorial: labels, comments, prefix cleanups, no axiomatic change.

Header `Version` in `README.md` and comment header in `reference-layer.ttl` must move together. Every PR that changes either file must include the semantic diff in the description (added / removed / renamed classes and properties).

## Contribution workflow (per [FR-GOV-ONT-002](../PRD.md#h-semantic-ontology))

1. **Proposal** — open an issue describing the semantic change and impact on operational bindings.
2. **Domain-owner review** — semantic / ontology owner + affected domain owners approve.
3. **Versioned release** — PR bumps SemVer per the rules above; updates [crosswalk.md](crosswalk.md) in the same PR if the change affects operational-layer mapping.
4. **Downstream impact check** — CI conformance check verifies every operational-layer entity still maps (RB-08 follow-up); reviewer must sign off on any deprecation window.
5. **Merge + release note** — no separate release notes; the PR description is the release note.

## Principles enforced (per [ADR-0014 §4](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#4-governance-model-obo-inspired))

- **Realism** — align to OBO Foundry semantics (entities exist independently of representation).
- **Univocity** — one term, one meaning across all layers.
- **Orthogonality / reuse** — import published ontologies (BFO, OMRSE, OGMS, OOSTT); do not duplicate them.

## RB-08 CI conformance check (placeholder)

The reference↔operational conformance CI check is scoped for a follow-up PR (RB-08). It will:

- Parse [reference-layer.ttl](reference-layer.ttl) to enumerate valid reference classes.
- Parse [crosswalk.md](crosswalk.md) to extract the reference ↔ operational mapping.
- Fail the build if:
  - A crosswalk row references an unknown reference class.
  - The operational-layer entity list (extracted from Fabric IQ, or from the Sprint-09 semantic model definition) contains an entity with no crosswalk row and no explicit `reference-layer-exempt` annotation.

Until then, the crosswalk is manually reviewed on every PR touching either layer.

## Scope discipline

This is a **skeleton** delivered under RB-11. It does not attempt OBO-publishable rigour. AMA §11.2 ("Reference-layer skeleton") explicitly bounds Sprint 09 scope to:

- Imports of the four published ontologies (declared but not exhaustively axiomatised).
- The `CapacityUnit` class + five subtypes.
- Enough class-level metadata to make [crosswalk.md](crosswalk.md) reviewable.

Full OBO-quality authoring — DL reasoning depth, exhaustive axioms, external publication — is a Phase 3 item ([AMA §9.3 L-06](../reviews/2026-07-01-ama-hcc-northstar-review.md#93-low-priority-post-sprint-12--strategic)).
