# Sprint 33 — Curavias BVA Agent — Plan 5: WS-C Orchestration + PO linkage

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |
| **Sprint** | Sprint 33 — Curavias BVA Agent |
| **Issue** | [#489](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/489) (tracker); [#527](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/527) (WS-C) |

> **For agentic workers:** REQUIRED SUB-SKILL — `superpowers:subagent-driven-development`
> (fresh subagent + spec review + quality review per task) with
> `superpowers:test-driven-development`. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Implement the frozen **PO↔BVA hand-off** (contracts §5) as the final
Sprint 33 workstream. The app orchestrator routes a question, fans out
onboarding/value-fit questions to **both** BVA (deterministic `bva.simulate` →
Class-C `GroundedChunk`s) and the **Product Owner Agent** (go/no-go/conditional
**verdict**), composes **one** advisory, fully-cited answer (**verdict first**,
BVA financials as supporting Class-C evidence, shared citation layer), and writes
the bundle back to the Cosmos `Opportunity` (`bvaResult`, `poVerdict`, `history`).

**Routing (frozen, contracts §5):**

- pure-financial ("ROI", "TCO", "payback", "CHF") → **BVA alone**
- pure-strategic ("strategy", "fit", "priority", "competitor") → **PO alone**
- onboarding / value-fit ("should we onboard", "business case", "worth it",
  "go/no-go") → **fan out to both** → composed answer

**Architecture (mirror existing patterns):**

- **Composer/router** — a pure module `data-platform/scripts/po-agent/runtime/bva_fanout.py`,
  sibling of [`orchestrator.py`](../../../data-platform/scripts/po-agent/runtime/orchestrator.py).
  Reuses the advisory prefix, DE/EN transparency, injection defence, and
  citation discipline of the PO runtime. No network I/O; tools/verdict injected.
- **Verdict is an input, not invented.** The composer consumes a `poVerdict`
  (go/no-go/conditional + rationale + citations) provided by the PO agent at
  runtime and a `BvaSimulationResult` provided by BVA. The composer arranges and
  cites; it never derives the verdict or any financial figure (no LLM math).
- **Write-back** — `build_opportunity_writeback` returns the `record_ask` kwargs
  consumed by [`data-platform/bva/opportunity_store.py`](../../../data-platform/bva/opportunity_store.py)
  (`bvaResult` snapshot + `poVerdict` + `history` append; never advances `status`
  past `qualified`; re-asks update the same lineage, never fork).
- **Eval** — `evals/bva-agent/run_fanout_evals.py`, mirroring
  [`evals/product-owner-agent/run_evals.py`](../../../evals/product-owner-agent/run_evals.py):
  runs the composer/router over `fanout_questions.yaml` and scores citation
  coverage + verdict-present gate + routing correctness (WS-C DoD, design §9.4).

**Frozen inputs (do NOT redefine):**

- `BvaSimulationResult` + embedded Class-C `GroundedChunk`
  ([contracts §2](../specs/2026-07-28-sprint-33-bva-agent-contracts.md)).
- PO↔BVA hand-off ([contracts §5](../specs/2026-07-28-sprint-33-bva-agent-contracts.md)).
- `grounded-chunk-v1.schema.json`; `bva-opportunity-v1.schema.json`.

**Out of scope (governance / other plans):** `AGENTS.md`, `.github/copilot/mcp.json`,
`docs/adr/*`, and `docs/PRD.md` edits (shared refusal rule; per-agent `AGENT.md`
prompt edits ARE in scope, backed by #527). The pre-existing PRD gap
(NFR-BVA-001..004 body rows) remains a separate governance follow-up.

## Tasks (subagent-driven, TDD-first)

- [ ] **C1 — pure fan-out composer + router** (`bva_fanout.py` + tests):
  `classify_intent`, `compose_onboarding_answer` (verdict first, every BVA figure
  cited, union citations, advisory prefix, DE/EN, partial when verdict
  missing/chunks uncited, injection defence), `build_opportunity_writeback`.
- [ ] **C2 — fan-out golden eval + fixtures**: `evals/bva-agent/fanout_questions.yaml`,
  `run_fanout_evals.py`, `tests/test_fanout_harness.py`. Citation coverage +
  verdict-present + routing gates green.
- [ ] **C3 — agent-pack prompt updates**: `agents/bva-agent/` +
  `agents/product-owner-agent/` (AGENT.md + golden-tasks.md) declare the
  fan-out/routing/hand-off + verdict emission + BVA Class-C consumption.
  New golden tasks carry `requirement:` front-matter (FR-BVA-003).
- [ ] **C4 — integration doc + this plan**: `docs/data-platform/bva-po-fanout.md`.
  Mojibake + markdownlint clean.
- [ ] **C5 — final review + PR**: full pytest + eval + doc gates; scope check;
  rebase on `origin/main`; squash PR → #527 / #489. Human merges.

## Definition of Done (design §9.4)

- Orchestrator fan-out eval (onboarding question composes BVA + PO) green.
- Routing correctness for financial / strategic / onboarding intents.
- Opportunity write-back stores `bvaResult` + `poVerdict` + appends `history`,
  never advancing `status` past `qualified`.
- Traceability: **FR-BVA-003** (PO↔BVA fan-out), FR-BVA-005 (opportunity write).

## Status — WS-C

- [ ] C1 fan-out composer + router
- [ ] C2 fan-out golden eval
- [ ] C3 agent-pack prompt updates
- [ ] C4 integration doc
- [ ] C5 final review + PR
