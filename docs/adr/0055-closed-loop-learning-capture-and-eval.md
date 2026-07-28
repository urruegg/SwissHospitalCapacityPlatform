# ADR-0055: Closed-loop learning — capture contract, retention class, and online-eval sampling

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Related** | [Sprint 30 closed-loop-learning design](../superpowers/specs/2026-07-27-sprint-30-closed-loop-learning-foundation-design.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) (no-PHI), [ADR-0013](0013-temporary-us-region-demo-scope.md) (demo region), [ADR-0007](0007-mvp-agent-runtime-and-hitl-release-gates.md) (HITL release gates), [ADR-0006](0006-preview-features-non-production-rule.md)/[ADR-0042](0042-prod-switzerland-north-ga-target-standing-preview-exception.md) (GA gate), [`docs/AI.md`](../AI.md) §Evaluation, [`docs/DATA.md`](../DATA.md), [`docs/COMPLIANCE.md`](../COMPLIANCE.md), [issue #443](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/443) |

## Context

Sprint 30 builds the platform's **closed learning loop**: capture every agent turn
as a PHI-free record, evaluate captured interactions (online + offline), curate
high-signal traces into versioned datasets, and — human-gated — improve the lead
agent from that curated data. Milestones M0–M5 shipped the capture contract, the
observability wiring, the evaluator library + offline gate, the online continuous
evaluator, and the curator + advisory backlog.

Three cross-cutting decisions underpin all of those milestones and every future
agent that joins the loop, so they are fixed here rather than left implicit in
code and PR prose:

1. **What is captured** — the shape and PHI posture of the interaction record.
2. **How long it is kept and where** — the retention class and residency of the
   capture store and the datasets derived from it.
3. **How much production traffic is scored online** — the sampling policy that
   trades evaluation cost against coverage.

The design spec (§12) explicitly requires "a new ADR [to] ratify the capture
contract, retention class, and the online-eval sampling approach." This ADR
discharges that requirement and closes the related open questions in §13. The
demo remains a synthetic-only, no-PHI showcase in the demo region (ADR-0013,
ADR-0016); Swiss-region residency is the GA target under the standing
Preview-exception path (ADR-0006/0042).

## Decision

1. **Capture contract — `DC-AGENT-INTERACTION-v1` (ratified).** One versioned
   record per agent turn, following the platform `DC-*` data-contract convention
   ([`docs/DATA.md`](../DATA.md)) and validated by
   `data/synthetic/schema/agent-interaction-v1.schema.json`. The record is
   **PHI-free by construction**: `promptRedacted` / `answerRedacted` pass through
   the deterministic redaction gate — the single persistence choke point — before
   storage, and `promptHash` (`sha256:…`) enables dedup / regression matching
   without retaining raw content. `userEvents` (thumbs / chip / insight-select /
   HITL) are appended in place; the `eval` block is filled asynchronously off the
   hot path. The record is model-agnostic (identical for the deterministic mock or
   a live Foundry model), so it is valid before and during hybrid testing.

2. **Retention class — R3, Swiss-residency at GA.** The `agent_interactions`
   capture store and the versioned golden datasets curated from it are classified
   **R3 "AI trace and model evidence" (24 months)** per the
   [`docs/DATA.md`](../DATA.md) retention table — they are agent decision-trace and
   grounding evidence, not raw operational buffers (R1) or compliance/security
   evidence (R4). The store follows platform residency: the **demo region** for the
   synthetic showcase, **Switzerland North** at GA, never crossing region without
   an approved runbook. Legal ratification of the concrete duration precedes go-live
   (standing DATA.md caveat); R3 is the policy class, not a legal sign-off.

3. **Online-eval sampling — 10–20%, default 15%, deterministic.** The scheduled
   online evaluator (M4) samples recent interactions at a configurable rate in the
   **10–20% band, defaulting to 15%**, via a **seeded** Bernoulli draw so a re-run
   of the same window yields the same sample (reproducible cost + auditable
   coverage). The offline regression gate (M3) always scores the **full** versioned
   golden dataset; sampling applies only to the online continuous evaluator over
   production traffic. The same evaluator library scores both, so online and
   offline verdicts never diverge on definition.

4. **Advisory-only loop with full lineage.** The loop is **advisory-only**: the
   curator (M5) emits dataset candidates and GitHub-issue backlog drafts; it never
   writes a dataset file, opens an issue, or mutates a prompt / knowledge source /
   guardrail / model. No change is promoted without the **offline regression suite
   passing and a human `approved-to-apply`** comment (AGENTS.md §4; no bot
   self-approval). Every improvement keeps the lineage chain
   **interaction → dataset → eval → change**, satisfying the AI-and-decision-trace
   governance domain.

5. **Requirement ratification.** This sprint's requirement family
   `FR-LEARN-001..005` and `NFR-LEARN-001..004` is ratified into
   [`docs/PRD.md`](../PRD.md) §Functional / §Non-Functional Requirements and the
   Traceability Matrix, replacing the "proposed" status they held in the design
   spec §14.

## Consequences

- **Positive.** The capture shape, retention posture, and sampling policy are now
  fixed contracts that every future agent (Sprint 31 breadth) inherits by
  configuration, not redesign. No-PHI is enforced at one choke point and gated by a
  PHI-leak evaluator; retention and residency are classified and auditable; online
  cost is bounded and reproducible; the human stays on the promotion gate; and the
  `FR-LEARN-*` / `NFR-LEARN-*` IDs that M1–M5 PRs already referenced now resolve in
  the PRD.
- **Negative / trade-offs.** A fixed 10–20% online sample under-covers rare failure
  modes early, when real-trace volume is thin — mitigated by the always-full
  offline gate plus curator random sampling, and revisited as traffic grows.
  Freezing the capture contract means a genuinely new field requires a
  `DC-AGENT-INTERACTION-v2` bump, which is deliberate friction against silent drift.
- **Residual open questions** (from design §13, now narrowed): concrete legal
  retention duration within R3; reviewer ownership of the curation gate; and the
  quality-dashboard surface (App Insights workbook vs Fabric report). These are
  operational choices that do not change the contracts fixed here.

## Alternatives considered

- **Leave the decisions implicit in code + PR prose.** Rejected: capture shape,
  retention, and sampling are cross-cutting and consumed by future agents and
  auditors; they must be a ratified contract, not a code comment.
- **Store raw prompts/answers for richer offline analysis.** Rejected: violates
  ADR-0016 no-PHI and the redaction-gate design; `promptHash` + redacted text give
  enough signal for dedup and regression without the PHI risk.
- **Score 100% of production traffic online.** Rejected: unnecessary cost for a
  foundation sprint; the full offline gate already covers the golden dataset, and a
  seeded 10–20% online sample gives representative continuous signal.
- **Autonomous promotion of high-confidence improvements.** Rejected: conflicts
  with the advisory-only / HITL posture (ADR-0007) and the platform's no-bot-
  self-approval rule; every promotion stays human-gated.
