# ADR-0053: DQA trust-score model, dimensions, and grounding-readiness thresholds

| Field | Value |
|-------|-------|
| **Status** | Proposed |
| **Date** | 2026-07-27 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Related** | [Sprint 31–32 SGA+DQA design](../superpowers/specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md), [Sprint 31 plan](../superpowers/plans/2026-07-27-sprint-31-data-quality-agent.md), [ADR-0007](0007-mvp-agent-runtime-and-hitl-release-gates.md) (HITL gates), [ADR-0008](0008-agent-runtime-pattern-scope-and-selection.md) (runtime), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) (no-PHI), [ADR-0006](0006-preview-features-non-production-rule.md)/[ADR-0042](0042-prod-switzerland-north-ga-target-standing-preview-exception.md) (GA gate), [issue #451](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/451), [#453](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/453) |

## Context

The COO showcase review's central finding is that **data quality — not the
technology — is the single point of failure**: a golden-source decision layer
whose trust is *assumed* rather than *measured* cannot safely ground Fabric IQ /
Foundry IQ. Sprint 31 elevates the existing `data-quality-agent` from
ingestion-time gates to **proactive** assessment, which requires a per-domain
**Trust Score** and a **gap** contract.

For that score to be governance-grade it must be **deterministic, versioned, and
explainable** — never an LLM estimate — so it is reproducible and auditable, and
so a domain cannot be gamed into a false "trusted" state. The score's dimensions,
weighting, and the thresholds that gate grounding-readiness are cross-cutting
decisions that other artefacts (the agent pack, the contracts, downstream
consumers) depend on, so they are fixed here rather than in code comments.

The demo remains a westus2, synthetic-data showcase with no PHI (ADR-0013,
ADR-0016); grounding-readiness certification respects the GA gate (ADR-0006/0042,
Fabric IQ first).

## Decision

1. **Eight-dimension trust model.** A domain's Trust Score is a weighted aggregate
   of eight dimensions, each scored in `[0,1]`:
   `completeness`, `timeliness`, `validity`, `uniqueness`, `consistency`,
   `lineage_integrity`, `provenance`, `ontology_mapping`. These are frozen as the
   canonical `DIMENSIONS` tuple in `data-platform/quality/trust_score.py`.

2. **Deterministic, versioned aggregation.** `TrustScore(domain) =
   Σ(wᵢ · dimensionᵢ) / Σ(wᵢ)`. The score is a pure function of its inputs — no
   randomness, no clock, no LLM estimate — and carries a `modelVersion`
   (`trustscore-v1`) that bumps whenever the dimensions or weighting change. The
   default weighting is **equal per dimension**; a decision class may supply its
   own weighting (below).

3. **Weighting per decision class.** Weights are ratified here and may differ per
   decision class. For Sprint 31 the ratified profiles are:

   | Decision class | Weighting profile |
   |----------------|-------------------|
   | `default` | Equal weight across all eight dimensions. |
   | `crisis` / real-time steering | Up-weight `timeliness`, `completeness`, `provenance` (freshness and source-trust dominate under time pressure). |
   | `planning` / forecast grounding | Up-weight `completeness`, `consistency`, `ontology_mapping` (coverage and semantic alignment dominate). |

   Concrete weight vectors live with the model in code and are changed only by a
   `modelVersion` bump plus an update to this ADR.

4. **Grounding-readiness thresholds.** A domain is certified `grounding-ready`
   only when **all** of the following clear the threshold for its decision class;
   otherwise the agent advises **degraded-mode** and never silently serves:

   | Decision class | Overall score | Gating dimensions (each must clear) |
   |----------------|---------------|-------------------------------------|
   | `default` | ≥ 0.80 | `completeness` ≥ 0.80, `provenance` ≥ 0.80, `ontology_mapping` ≥ 0.80 |
   | `crisis` | ≥ 0.85 | `timeliness` ≥ 0.90, `completeness` ≥ 0.85, `provenance` ≥ 0.85 |
   | `planning` | ≥ 0.80 | `completeness` ≥ 0.85, `consistency` ≥ 0.80, `ontology_mapping` ≥ 0.80 |

5. **Read-only, advisory, HITL posture.** DQA never edits source data. Each
   below-threshold dimension is emitted as a `DC-DQ-GAP-v1` finding routed to the
   accountable data owner; the owner remediates. The agent cannot self-certify a
   domain grounding-ready while it has open, unremediated gaps.

6. **The `DC-DQ-GAP-v1` seam (frozen).** A gap with `newSourceNeeded: true` is the
   single, frozen integration point handed to the Sprint 32 Signal Agent (SGA);
   its shape is fixed by the design (§8) and the contract schema.

## Consequences

- **Positive.** Trust becomes *measured and reproducible*; a below-threshold
  domain is withheld rather than silently served; gaps are owner-routed and
  auditable; SGA gets a stable, demand-driven trigger; no PHI is involved
  (aggregate metadata only).
- **Negative / trade-offs.** The initial weights and thresholds are expert-set,
  not yet backtested against real forecast impact (that backtest converges with
  the Sprint 30 evaluation harness — an open question in the design §12). Changing
  the model requires a coordinated `modelVersion` bump + ADR update, which is
  deliberate friction to prevent silent drift.
- **Status.** `Proposed` until the trust-score module + thresholds are exercised
  on ≥1 gold domain and the sprint is accepted, at which point this ADR moves to
  `Accepted`.

## Alternatives considered

- **LLM-estimated trust.** Rejected: not reproducible, not auditable, and gameable
  — it would reintroduce the very "assumed trust" the COO finding calls out.
- **Single scalar quality flag (pass/fail).** Rejected: loses the dimension
  breakdown that makes a score explainable and a gap actionable.
- **Per-domain bespoke thresholds only.** Rejected as the default: decision-class
  profiles keep the model consistent and reviewable; a domain may still be tuned
  by overriding weights, recorded here.

## References

- Design: [`docs/superpowers/specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md`](../superpowers/specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md) (§6 DQA, §8 seam, §10 governance)
- Modules: `data-platform/quality/trust_score.py`, `data-platform/quality/gap_assessment.py`
- Contracts: `data/synthetic/schema/dc-dq-trustscore-v1.schema.json`, `data/synthetic/schema/dc-dq-gap-v1.schema.json`
- Agent pack: [`agents/data-quality-agent/AGENT.md`](../../agents/data-quality-agent/AGENT.md)
- Requirements: `docs/PRD.md` §S (FR-DQA-*) + §O (NFR-DQA-*)
