# BVA + PO fan-out orchestration (Sprint 33 WS-C)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | (none — initial) |

WS-C implements the frozen **PO↔BVA hand-off**
([contracts §5](../superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md))
as a pure, advisory-only composer/router. The app orchestrator routes a question,
fans out onboarding/value-fit questions to **both** the BVA agent and the
Product Owner Agent, composes **one** fully-cited answer (**verdict first**, BVA
financials as supporting Class-C evidence), and writes the bundle back to the
Cosmos `Opportunity`. No LLM math, no cloud mutation.

## Module

[`data-platform/scripts/po-agent/runtime/bva_fanout.py`](../../data-platform/scripts/po-agent/runtime/bva_fanout.py)
is a sibling of the PO runtime
[`orchestrator.py`](../../data-platform/scripts/po-agent/runtime/orchestrator.py)
and reuses its advisory prefix, DE/EN transparency, prompt-injection defence, the
authorisation filter ([`authz.py`](../../data-platform/scripts/po-agent/runtime/authz.py)),
and audit logging ([`audit.py`](../../data-platform/scripts/po-agent/runtime/audit.py)).
It performs no network I/O; the `BvaSimulationResult` and the `poVerdict` are
injected by the caller.

| Function | Responsibility |
| -------- | -------------- |
| `classify_intent(question)` | Word-boundary keyword routing → `financial` (BVA alone), `strategic` (PO alone), or `onboarding` (fan out to both). Ambiguous input defaults to `onboarding` (safest: compose both). |
| `bva_chunks_from_result(bva_result)` | Extract the Class-C `GroundedChunk`s from a `BvaSimulationResult`. |
| `compose_onboarding_answer(question, bva_result, po_verdict, caller, …)` | Compose the frozen answer: PO verdict first (with its citations), then each BVA figure as a cited sentence; shared, de-duped citation layer (verdict citations first). |
| `build_opportunity_writeback(…)` | Build `record_ask(**kwargs)` for the Cosmos SoR (`bvaResult` + `poVerdict` + `history`); never advances `status` past the agent-safe default. |

## Routing (frozen, contracts §5)

* **pure-financial** ("ROI", "TCO", "payback", "NPV", "CHF", "cost") → **BVA alone**
* **pure-strategic** ("strategy", "fit", "priority", "competitor", "roadmap") → **PO alone**
* **onboarding / value-fit** ("onboard", "business case", "worth it", "go/no-go") → **fan out to both**

Routing keywords are word-boundary anchored so a strategic token such as `fit`
does not misfire on financial words like *bene**fit*** or *pro**fit***.

## Composition invariants (grounded-answer contract)

* **Verdict is an input, never invented.** The PO agent supplies the
  `go` / `no-go` / `conditional` verdict, rationale, and citations; the composer
  arranges and cites, and degrades to a transparent `partial` when the verdict is
  missing or invalid — it never fabricates a verdict.
* **Verdict first**, then BVA financials as supporting Class-C evidence.
* **No uncited substantive claim**: every rendered sentence carries a
  `[sourceRef]`; partner-tier callers (Class C dropped by `authz`) degrade to
  `partial`; prompt-injection questions degrade to `partial`.
* **Status** is the worst-of the used chunks (`verified` → `requires-validation`
  → `partial`); **confidence** is their mean.

## Opportunity write-back

`build_opportunity_writeback` returns kwargs for
[`opportunity_store.record_ask`](../../data-platform/bva/opportunity_store.py)
(WS-D). It writes `bvaResult`, `poVerdict`, and appends a `history` event via the
new optional `historyEvent` kwarg. It sets `status="new"`: agents capture the ask
and never auto-promote; humans advance the lifecycle past `qualified`. Re-asks
update the same hospital lineage (deterministic id) and append to `history`,
never forking a parallel record.

## Eval (WS-C Definition of Done)

[`evals/bva-agent/run_fanout_evals.py`](../../evals/bva-agent/run_fanout_evals.py)
replays [`fanout_questions.yaml`](../../evals/bva-agent/fanout_questions.yaml)
through the composer/router and gates **routing accuracy = 1.0**, **citation
coverage ≥ 0.95**, and **verdict-present** on every composed onboarding answer —
mirroring the PO harness
[`evals/product-owner-agent/run_evals.py`](../../evals/product-owner-agent/run_evals.py).
This satisfies the design §9.4 DoD ("orchestrator fan-out eval green").

## Traceability

* **FR-BVA-003** — PO↔BVA fan-out; verdict-first composition over Class-C evidence.
* **FR-BVA-005** — value/onboarding asks captured as `Opportunity` write-backs.
