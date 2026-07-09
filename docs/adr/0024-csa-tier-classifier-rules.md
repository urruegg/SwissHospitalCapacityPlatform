# ADR-0024 — CSA tier classifier rules (Swiss Lage doctrine)

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Deciders** | @urruegg |
| **Superseded by** | — |
| **Renumber note** | Renumbered from 0021 during Sprint 16 merge — 0021 was already occupied by [ADR-0021 readiness scoring rules](0021-readiness-scoring-rules.md) (Sprint 14) and [ADR-0021 whiteboard base](0021-whiteboard-base-react-flow-vs-tldraw-vs-custom.md) (Sprint 13). |

## Context

Sprint 16 introduces the CSA what-if system. Every simulation run must be
classified into a **Swiss Lage tier** so that the `csa-agent` can retrieve the
doctrine-aligned response levers and emit a defensible recommendation
([design spec §6](../superpowers/specs/2026-07-09-sprint-16-csa-design.md#6-tier-classifier-swiss-lage-doctrine)).

The Swiss operating-situation doctrine defines three tiers:

- **Normallage** (Tier 1) — normal operating capacity.
- **Besondere Lage** (Tier 2) — a special situation manageable by the ordinary
  responsible bodies with reinforced means (internal reallocation).
- **Ausserordentliche Lage** (Tier 3) — an extraordinary situation exceeding the
  ordinary means, governed by the VKSD (Verordnung über den Koordinierten
  Sanitätsdienst) Art. 2 severe-consequence / multi-canton criteria.

A tier classifier that is implicit in prompt text or notebook code is not
auditable and drifts silently. This ADR **codifies the classification rules** so
they are version-pinned and change only through a superseding ADR.

## Decision

The tier classifier is implemented as a pure, deterministic rules layer in
[`data-platform/scripts/csa/csa-tier-classifier.py`](../../data-platform/scripts/csa/csa-tier-classifier.py),
`RULES_VERSION = "1.0.0"`. It consumes a projected capacity state and returns a
tier with human-readable reasons.

### Rules (v1.0.0)

Evaluated top-down; the first matching tier wins.

1. **Tier 3 — Ausserordentliche Lage** if **any** of:
   - demand exceeds site capacity **even after internal levers**
     (`flags.capacityExceededAfterLevers`);
   - the event is **multi-canton** (`flags.multiCanton`);
   - the event is **severe-consequence** (`flags.severeConsequence`), per
     VKSD Art. 2;
   - a **special capability is overwhelmed** — utilization `> 1.0` or a positive
     shortfall on one of `burn-beds`, `ventilators`, `decontamination`,
     `isolation-beds`.
2. **Tier 2 — Besondere Lage** if any resource dimension utilization is
   `>= 0.90` (breaches threshold; internal reallocation required; single-site).
3. **Tier 1 — Normallage** otherwise.

### Thresholds

| Constant | Value | Meaning |
| -------- | ----- | ------- |
| `TIER2_UTILIZATION_THRESHOLD` | `0.90` | Threshold breach → Besondere Lage |
| `SPECIAL_CAPABILITIES` | `burn-beds, ventilators, decontamination, isolation-beds` | Exhaustion → Ausserordentliche Lage |

## Consequences

- **Auditable + version-pinned.** The rules live in code and this ADR; the
  classifier stamps `rulesVersion` onto every result and every
  `simulation-runs` document.
- **Change control.** Editing thresholds, special-capability membership, or the
  tier order **requires a superseding ADR** and a `RULES_VERSION` bump. The
  golden fixtures in
  [`data-platform/scripts/csa/tests/test_tier_classifier.py`](../../data-platform/scripts/csa/tests/test_tier_classifier.py)
  pin the doctrine transitions.
- **Scope.** The classifier is advisory input to the `csa-agent`; it never
  executes a response lever (design spec §5 refusal rules).

## Alternatives considered

- **LLM-only classification** — rejected: non-deterministic, not auditable, and
  cannot be pinned for regulated decision support.
- **Thresholds embedded in the notebook** — rejected: couples doctrine to Spark
  code and hides it from review.
