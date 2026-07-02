# ADR-0002: Defer Fabric IQ Ontology from MVP

- Status: **Superseded by [ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md)** (2026-07-02) — the platform target has widened to an integral HCC tier where Fabric IQ Ontology is the target semantic backbone (GA-gated); the "deferred indefinitely" posture no longer matches design intent. The content below is preserved unchanged as the accepted-but-superseded record.
- Date: 2026-06-01
- Deciders: Architecture Working Group
- Related Decision ID: AR-D-002
- Related Requirements: FR-DATA-005, NFR-AI-002, NFR-MAINT-004

## Context

Fabric IQ Ontology is currently published as preview with no committed GA date
for Switzerland availability. The architecture must preserve predictable delivery
for regulated healthcare MVP scope.

## Decision

Fabric IQ Ontology is excluded from MVP critical-path scope and moved to a
post-MVP feature wave after GA and regional validation.

## Consequences

- MVP semantic layer is implemented using GA Fabric assets and semantic models.
- Ontology adoption remains a controlled roadmap item.
- Cross-domain semantic capabilities are delayed but delivery certainty improves.

## Review Trigger

Re-evaluate when Microsoft publishes GA status and confirmed regional support
for Switzerland deployment scope.
