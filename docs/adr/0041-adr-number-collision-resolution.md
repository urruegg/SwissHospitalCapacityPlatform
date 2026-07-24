# ADR-0041: ADR Number Collision Resolution

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-24 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |

## Context

ADR numbers are stable identifiers used by documentation, traceability rows, and
evidence surfaces. During Sprint 19 governance reconciliation, two files were
found using ADR-0039:

* `0039-prod-network-parity-vnet-private-endpoints.md`, dated 2026-07-22.
* `0039-curavias-landing-zone-and-skills-evidence-plugins.md`, dated
  2026-07-23, Status Proposed, Sprint 23 / issue #255.

A separate pre-existing ADR-0021 collision was also found:

* `0021-readiness-scoring-rules.md`.
* `0021-whiteboard-base-react-flow-vs-tldraw-vs-custom.md`.

The ADR-0021 prose references are ambiguous and the two ADRs belong to unrelated
Sprint 13 / Sprint 14 topics, so that collision requires a dedicated hygiene PR.

## Decision

Resolve only the ADR-0039 collision in this change:

* `0039-prod-network-parity-vnet-private-endpoints.md` retains ADR-0039 because
  it is the earlier ADR and is being promoted to Accepted during the Sprint 19
  PROD network-parity work.
* `0039-curavias-landing-zone-and-skills-evidence-plugins.md` is renumbered to
  [ADR-0040](0040-curavias-landing-zone-and-skills-evidence-plugins.md).
* A redirect stub remains at the old Curavias ADR path to preserve navigability
  while inbound links are retargeted.

Record the ADR-0021 collision as an open follow-up. The later hygiene PR should
renumber `0021-whiteboard-base-react-flow-vs-tldraw-vs-custom.md` to the next
free ADR number available at that time and update only confidently attributable
inbound references.

## Consequences

* One ADR now owns ADR-0039: the PROD network-parity ADR.
* The Curavias landing-zone and skills-evidence plugin decision is ADR-0040.
* The ADR-0021 collision remains intentionally unresolved in this change and is
  tracked for a focused follow-up because references are ambiguous.
* The repository convention is reaffirmed: one ADR equals one ADR number.
* The next free ADR number after this work is ADR-0042.

## References

* [ADR-0039 — PROD Network Parity](0039-prod-network-parity-vnet-private-endpoints.md)
* [ADR-0040 — Curavias Landing Zone + Skills-Evidence Plugin Architecture + Hybrid Transport](0040-curavias-landing-zone-and-skills-evidence-plugins.md)
* [ADR-0021 — Readiness Scoring Rules](0021-readiness-scoring-rules.md)
* [ADR-0021 — Whiteboard Base: React Flow vs tldraw vs Custom](0021-whiteboard-base-react-flow-vs-tldraw-vs-custom.md)
