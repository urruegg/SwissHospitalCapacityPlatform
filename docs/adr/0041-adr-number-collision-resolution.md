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
  [ADR-0040](0050-curavias-landing-zone-and-skills-evidence-plugins.md)
  (subsequently renumbered ADR-0040 -> ADR-0050 on 2026-07-26; see the Update below).
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
* The next free ADR number after the original Sprint 19 work was ADR-0042
  (since consumed; the current next-free number is recorded in the Update below).

## References

* [ADR-0039 — PROD Network Parity](0039-prod-network-parity-vnet-private-endpoints.md)
* [ADR-0050 — Curavias Landing Zone + Skills-Evidence Plugin Architecture + Hybrid Transport](0050-curavias-landing-zone-and-skills-evidence-plugins.md)
* [ADR-0021 — Readiness Scoring Rules](0021-readiness-scoring-rules.md)
* [ADR-0051 — Whiteboard Base: React Flow vs tldraw vs Custom](0051-whiteboard-base-react-flow-vs-tldraw-vs-custom.md)

## Update - 2026-07-26 (#378): ADR-0040 and ADR-0021 collisions resolved

A later reconciliation (issue #378) found that the ADR-0040 number had become a
**real two-ADR collision** on `main`: the Curavias landing-zone ADR (renumbered
0039 -> 0040 above) and Sprint 26's
`0040-prescriptive-decision-ontology-and-runtime-store.md` both held 0040 after
concurrent merges. The pre-existing ADR-0021 collision was also still open, and a
further **ADR-0043** collision had since appeared.

Resolution in this pass (a safe, self-contained slice):

* **ADR-0040 is kept by**
  `0040-prescriptive-decision-ontology-and-runtime-store.md` (Sprint 26 decision
  layer; woven through FR-DEC/NFR-DEC traceability, `docs/AI.md`, `docs/DATA.md`,
  and evidence fixtures across merged PRs) - the lowest-churn ADR to keep fixed.
* **The Curavias ADR is renumbered** 0040 -> **0050**
  (`0050-curavias-landing-zone-and-skills-evidence-plugins.md`); it was already the
  "moving" ADR (0039 -> 0040 -> 0050).
* **The whiteboard ADR is renumbered** 0021 -> **0051**
  (`0051-whiteboard-base-react-flow-vs-tldraw-vs-custom.md`);
  `0021-readiness-scoring-rules.md` now solely owns ADR-0021.
* Inbound references repointed: `docs/PRD.md`, `docs/COMPLIANCE.md`,
  `docs/adr/0024-csa-tier-classifier-rules.md`, the `0039-curavias` redirect stub,
  `docs/sprints/superpowers-checkpoint-matrix.md`, and
  `apps/hcc-app-fluent/src/data/evidence/evidence-demo.json`.

**Reserved numbering:** 0050/0051 were chosen deliberately to leave **0045-0049**
free for the in-flight Sprint 23/28/29 ADRs, avoiding a renumbering race.

**Still open (deferred):** the **ADR-0043** collision
(`0043-preview-tier-permitted-in-prod-swn-for-demo.md` vs
`0043-product-owner-agent-foundry-iq-domain.md`) is **not** resolved here because
its inbound references touch `AGENTS.md` (governance-protected) and the live
Sprint 23 (#255) and Sprint 28 (#377, PR #395) branches. It remains tracked
in issue #378 for a focused follow-up hygiene PR once those sprints land.

**Next free ADR number:** ADR-0045 (0042 = preview-exception, 0043 = double-used
pending the deferred fix, 0044 = retire-public-website, 0050/0051 = this hygiene
renumber).
