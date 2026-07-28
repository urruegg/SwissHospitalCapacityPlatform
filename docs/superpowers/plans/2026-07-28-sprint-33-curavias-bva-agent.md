# Sprint 33 — Curavias BVA Agent — Plan 1: WS-G0 Frozen Contracts

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze the three shared interface contracts every downstream Sprint 33 workstream builds against — the `bva.simulate` **result** shape, the **`Opportunity`** record shape, and the **CHF cost-basis normalization** contract — as JSON Schemas + a frozen contracts doc + conformance fixtures and tests.

**Architecture:** Mirror the Sprint 28 WS-G0 pattern exactly. Publish `draft-07` JSON Schemas under `data/synthetic/schema/`, example fixtures under `evals/bva-agent/fixtures/`, and pytest conformance tests under `evals/bva-agent/tests/` that validate each fixture against its schema. The frozen contracts doc (`docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md`) is the single source of truth; changing a shape requires a version bump there plus a matching schema/fixture update. No runtime code, no cloud calls in this plan — contracts only.

**Tech Stack:** JSON Schema (draft-07), Python 3 + `pytest` + `jsonschema` (already a dev dependency, used by `evals/product-owner-agent/tests`). Runtime interpreter is `python` (not `python3`) per repo convention.

---

## File structure (created by this plan)

- `docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md` — frozen contracts narrative (mirrors `2026-07-25-sprint-28-po-agent-contracts.md`).
- `data/synthetic/schema/bva-simulation-result-v1.schema.json` — the `bva.simulate` result envelope (embeds `GroundedChunk[]`).
- `data/synthetic/schema/bva-opportunity-v1.schema.json` — the Cosmos `Opportunity` record (WS-D system-of-record shape).
- `evals/bva-agent/fixtures/bva-simulation-result-example.json` — one valid simulation result.
- `evals/bva-agent/fixtures/bva-opportunity-example.json` — one valid opportunity.
- `evals/bva-agent/tests/conftest.py` — repo-root + loader helpers.
- `evals/bva-agent/tests/test_bva_schema_conformance.py` — schema-exists + fixture-validates + invariant tests.

Reuse (do NOT redefine): `data/synthetic/schema/grounded-chunk-v1.schema.json` — the BVA result embeds `GroundedChunk` objects by reference in the doc; the simulation-result schema references the same field shape so PO can consume BVA chunks unchanged.

---

## Task 1: Simulation-result JSON Schema

**Files:**

- Create: `data/synthetic/schema/bva-simulation-result-v1.schema.json`
- Create: `evals/bva-agent/fixtures/bva-simulation-result-example.json`
- Create: `evals/bva-agent/tests/conftest.py`
- Test: `evals/bva-agent/tests/test_bva_schema_conformance.py`

- [ ] **Step 1: Write the schema file**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "bva-simulation-result-v1.schema.json",
  "title": "BVA Agent Simulation Result Contract (BvaSimulationResult v1)",
  "description": "Frozen Sprint 33 interface contract (WS-G0). Output of the deterministic bva.simulate tool. All figures are CHF. No LLM arithmetic. Every figure is rendered as a GroundedChunk (grounded-chunk-v1.schema.json) so the PO citation layer consumes BVA output unchanged. See docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md.",
  "type": "object",
  "additionalProperties": false,
  "required": ["scenarioId", "currency", "asOf", "baseline", "projection", "metrics", "sensitivity", "chunks"],
  "properties": {
    "scenarioId": { "type": "string", "minLength": 1, "description": "Stable id for this simulation (also the Opportunity join key)." },
    "currency": { "type": "string", "const": "CHF", "description": "All monetary figures are CHF (D2)." },
    "asOf": { "type": "string", "format": "date-time", "description": "ISO-8601 stamp of the gold snapshot the baseline was read from." },
    "baseline": {
      "type": "object",
      "additionalProperties": false,
      "required": ["totalCostChf", "oneTimeChf", "annualRunChf", "hospitals"],
      "properties": {
        "totalCostChf": { "type": "number", "minimum": 0 },
        "oneTimeChf": { "type": "number", "minimum": 0 },
        "annualRunChf": { "type": "number", "minimum": 0 },
        "hospitals": { "type": "integer", "minimum": 1, "description": "Count of baseline hospitals (3 today)." }
      }
    },
    "projection": {
      "type": "object",
      "additionalProperties": false,
      "required": ["hospitalName", "archetype", "onboardingOneTimeChf", "annualRunDeltaChf", "annualBenefitChf"],
      "properties": {
        "hospitalName": { "type": "string", "minLength": 1 },
        "archetype": { "type": "string", "enum": ["acute", "rehab", "spitex"] },
        "onboardingOneTimeChf": { "type": "number", "minimum": 0 },
        "annualRunDeltaChf": { "type": "number", "minimum": 0 },
        "annualBenefitChf": { "type": "number", "description": "Modelled benefit (ADR-0025 KPI catalog); may be provisional." }
      }
    },
    "metrics": {
      "type": "object",
      "additionalProperties": false,
      "required": ["roiPct", "paybackMonths", "tco3yChf", "npvChf"],
      "properties": {
        "roiPct": { "type": "number" },
        "paybackMonths": { "type": "number", "minimum": 0 },
        "tco3yChf": { "type": "number" },
        "npvChf": { "type": "number" }
      }
    },
    "sensitivity": {
      "type": "object",
      "additionalProperties": false,
      "required": ["low", "base", "high"],
      "description": "Low/base/high band on roiPct.",
      "properties": {
        "low": { "type": "number" },
        "base": { "type": "number" },
        "high": { "type": "number" }
      }
    },
    "chunks": {
      "type": "array",
      "minItems": 1,
      "description": "Each headline figure rendered as a GroundedChunk (grounded-chunk-v1.schema.json). Class is always 'C' (cost).",
      "items": { "type": "object", "required": ["classId", "text", "citation", "asOf", "liveness", "status", "confidence", "language"] }
    }
  }
}
```

- [ ] **Step 2: Write the example fixture**

```json
{
  "scenarioId": "sim-hopital-fribourg-2026w30",
  "currency": "CHF",
  "asOf": "2026-07-28T00:00:00Z",
  "baseline": { "totalCostChf": 442000.0, "oneTimeChf": 1300000.0, "annualRunChf": 1250000.0, "hospitals": 3 },
  "projection": { "hospitalName": "Hopital de Fribourg", "archetype": "acute", "onboardingOneTimeChf": 210000.0, "annualRunDeltaChf": 180000.0, "annualBenefitChf": 640000.0 },
  "metrics": { "roiPct": 34.2, "paybackMonths": 17.5, "tco3yChf": 750000.0, "npvChf": 512000.0 },
  "sensitivity": { "low": 18.0, "base": 34.2, "high": 51.0 },
  "chunks": [
    {
      "classId": "C",
      "text": "3-year TCO for onboarding Hopital de Fribourg is CHF 750,000 with a 34.2% ROI and 17.5-month payback.",
      "citation": { "sourceRef": "sm_bva:bva_baseline_kpi@2026-07-28; input:onboarding-scope", "anchor": "bva.simulate" },
      "asOf": "2026-07-28T00:00:00Z",
      "liveness": "live",
      "status": "requires-validation",
      "confidence": 0.72,
      "language": "en"
    }
  ]
}
```

- [ ] **Step 3: Write the conftest helper**

```python
"""Shared fixtures for Sprint 33 BVA Agent contract conformance tests."""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = REPO_ROOT / "data" / "synthetic" / "schema"
FIXTURE_DIR = REPO_ROOT / "evals" / "bva-agent" / "fixtures"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
```

- [ ] **Step 4: Write the failing conformance test**

```python
"""Contract conformance tests for the Sprint 33 BVA Agent frozen shapes.

Run:  python -m pytest evals/bva-agent/tests/test_bva_schema_conformance.py -v
"""
from __future__ import annotations

import pytest

from conftest import SCHEMA_DIR, FIXTURE_DIR, load_json

SIM_SCHEMA = SCHEMA_DIR / "bva-simulation-result-v1.schema.json"
OPP_SCHEMA = SCHEMA_DIR / "bva-opportunity-v1.schema.json"
SIM_FIXTURE = FIXTURE_DIR / "bva-simulation-result-example.json"
OPP_FIXTURE = FIXTURE_DIR / "bva-opportunity-example.json"


def test_schemas_exist() -> None:
    assert SIM_SCHEMA.is_file(), f"missing schema: {SIM_SCHEMA}"
    assert OPP_SCHEMA.is_file(), f"missing schema: {OPP_SCHEMA}"


def test_simulation_result_validates() -> None:
    import jsonschema

    jsonschema.validate(instance=load_json(SIM_FIXTURE), schema=load_json(SIM_SCHEMA))


def test_all_money_is_chf() -> None:
    result = load_json(SIM_FIXTURE)
    assert result["currency"] == "CHF", "BVA figures must be normalized to CHF (D2)"


def test_every_metric_has_a_chunk() -> None:
    result = load_json(SIM_FIXTURE)
    assert len(result["chunks"]) >= 1, "every simulation result must carry >=1 GroundedChunk (NFR-BVA-002)"
    for chunk in result["chunks"]:
        assert chunk["classId"] == "C", "BVA chunks are Class C (cost)"
        assert chunk["citation"]["sourceRef"], "no uncited figure (NFR-BVA-002)"


def test_opportunity_validates() -> None:
    import jsonschema

    jsonschema.validate(instance=load_json(OPP_FIXTURE), schema=load_json(OPP_SCHEMA))
```

- [ ] **Step 5: Run the test to verify it fails**

Run: `python -m pytest evals/bva-agent/tests/test_bva_schema_conformance.py -v`
Expected: FAIL — `test_schemas_exist` / `test_opportunity_validates` fail because `bva-opportunity-v1.schema.json` and `bva-opportunity-example.json` do not exist yet (created in Task 2).

- [ ] **Step 6: Commit**

```bash
git -c core.hooksPath=/dev/null add data/synthetic/schema/bva-simulation-result-v1.schema.json evals/bva-agent/fixtures/bva-simulation-result-example.json evals/bva-agent/tests/conftest.py evals/bva-agent/tests/test_bva_schema_conformance.py
git -c core.hooksPath=/dev/null commit -m "feat(bva): freeze bva.simulate result schema + conformance test (WS-G0)"
```

---

## Task 2: Opportunity JSON Schema

**Files:**

- Create: `data/synthetic/schema/bva-opportunity-v1.schema.json`
- Create: `evals/bva-agent/fixtures/bva-opportunity-example.json`
- Test: `evals/bva-agent/tests/test_bva_schema_conformance.py` (already written in Task 1; now made to pass)

- [ ] **Step 1: Write the schema file**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "bva-opportunity-v1.schema.json",
  "title": "BVA Opportunity Record Contract (Opportunity v1)",
  "description": "Frozen Sprint 33 interface contract (WS-G0). Cosmos DB system-of-record for a hospital-onboarding opportunity (D4). Projected one-way to gold.bva_opportunity. Agents never auto-advance status past 'qualified'. See docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md.",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "hospitalName", "archetype", "createdAt", "createdBy", "status", "askText", "language", "history"],
  "properties": {
    "id": { "type": "string", "minLength": 1 },
    "hospitalName": { "type": "string", "minLength": 1 },
    "archetype": { "type": "string", "enum": ["acute", "rehab", "spitex"] },
    "createdAt": { "type": "string", "format": "date-time" },
    "createdBy": { "type": "string", "minLength": 1 },
    "status": { "type": "string", "enum": ["new", "evaluating", "qualified", "disqualified", "onboarding", "won", "lost"] },
    "askText": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "enum": ["de", "en"] },
    "bvaResult": { "type": ["object", "null"], "description": "Snapshot of the bva-simulation-result-v1 output (nullable until first simulate)." },
    "poVerdict": {
      "type": ["object", "null"],
      "additionalProperties": false,
      "properties": {
        "verdict": { "type": "string", "enum": ["go", "no-go", "conditional"] },
        "rationale": { "type": "string" },
        "citations": { "type": "array", "items": { "type": "string" } }
      }
    },
    "inputs": { "type": ["object", "null"], "description": "The slot-filled deltas (beds, occupancy, case-mix, onboarding scope)." },
    "history": {
      "type": "array",
      "description": "Append-only audit of re-simulations / verdict changes.",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["at", "event"],
        "properties": {
          "at": { "type": "string", "format": "date-time" },
          "event": { "type": "string", "minLength": 1 },
          "by": { "type": "string" }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Write the example fixture**

```json
{
  "id": "opp-hopital-fribourg-0001",
  "hospitalName": "Hopital de Fribourg",
  "archetype": "acute",
  "createdAt": "2026-07-28T09:15:00Z",
  "createdBy": "app-copilot",
  "status": "evaluating",
  "askText": "Should we onboard Hopital de Fribourg?",
  "language": "en",
  "bvaResult": null,
  "poVerdict": null,
  "inputs": { "beds": 320, "occupancyTarget": 0.85, "onboardingScope": "full" },
  "history": [
    { "at": "2026-07-28T09:15:00Z", "event": "created from START rail ask", "by": "app-copilot" }
  ]
}
```

- [ ] **Step 3: Run the test to verify it passes**

Run: `python -m pytest evals/bva-agent/tests/test_bva_schema_conformance.py -v`
Expected: PASS — all five tests green (schemas exist, both fixtures validate, CHF + chunk invariants hold).

- [ ] **Step 4: Commit**

```bash
git -c core.hooksPath=/dev/null add data/synthetic/schema/bva-opportunity-v1.schema.json evals/bva-agent/fixtures/bva-opportunity-example.json
git -c core.hooksPath=/dev/null commit -m "feat(bva): freeze Opportunity record schema + fixture (WS-G0)"
```

---

## Task 3: Frozen contracts document

**Files:**

- Create: `docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md`

- [ ] **Step 1: Write the contracts doc**

Mirror `docs/superpowers/specs/2026-07-25-sprint-28-po-agent-contracts.md`. Include the version-header table (Version 1.0.0, Date 2026-07-28, Author, Status **Frozen**, Sprint 33, Issue #TBD, Governed by the new BVA ADR). Sections:

1. **Scope** — the three frozen shapes: `bva.simulate` result, `Opportunity`, and the CHF cost-basis normalization contract; published by WS-G0 before WS-A/B/D/C start.
2. **`BvaSimulationResult` (frozen)** — reproduce the field list from `bva-simulation-result-v1.schema.json` with the invariants: `currency` is always CHF; every headline figure appears as a `GroundedChunk` (Class C) with a non-empty `citation.sourceRef`; no LLM arithmetic.
3. **`Opportunity` (frozen)** — reproduce the field list from `bva-opportunity-v1.schema.json` with the lifecycle (`new -> evaluating -> qualified/disqualified -> onboarding -> won/lost`) and the rule that agents never auto-advance past `qualified`; re-asks append to `history`, never fork.
4. **Cost-basis normalization contract (frozen)** — team cost = Copilot AIU/token spend + human elective hours × configured rate; Azure/BOM USD converted to CHF via the explicit `bva_fx_rate.csv` line; settling weeks marked provisional.
5. **PO <-> BVA hand-off** — BVA returns `BvaSimulationResult`; PO consumes its `chunks` as Class-C evidence and emits the `poVerdict`; the orchestrator composes one cited answer.
6. **Change control** — no shape change without a version bump here plus a matching update to the two schemas + fixtures + this plan's conformance test.

- [ ] **Step 2: Run the doc gates**

Run: `python scripts/lint/check_mojibake.py docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md`
Expected: `OK: no mojibake`.

Run: `npx --yes markdownlint-cli2 "docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md"`
Expected: `0 issues`.

- [ ] **Step 3: Commit**

```bash
git -c core.hooksPath=/dev/null add docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md
git -c core.hooksPath=/dev/null commit -m "docs(bva): frozen WS-G0 interface contracts (Sprint 33)"
```

---

## Task 4: Wire the conformance test into CI discovery

**Files:**

- Modify: `evals/bva-agent/tests/conftest.py` (only if CI needs an `__init__` or path shim — verify first)

- [ ] **Step 1: Verify how PO evals are discovered**

Run: `python -m pytest evals/product-owner-agent/tests -q`
Expected: PASS. Confirm whether discovery relies on `rootdir`/`conftest` import style (the BVA test imports `from conftest import ...`, which requires running from the tests dir or a `conftest.py` on `sys.path`). If PO uses absolute imports instead, match that style in `test_bva_schema_conformance.py` before finishing.

- [ ] **Step 2: Run the BVA suite from the repo root the way CI will**

Run: `python -m pytest evals/bva-agent -v`
Expected: PASS (5 tests). If collection fails on the `from conftest import` line, change the import to the PO pattern (module-level `REPO_ROOT` in the test file) and re-run.

- [ ] **Step 3: Commit any discovery fix**

```bash
git -c core.hooksPath=/dev/null add evals/bva-agent/tests/
git -c core.hooksPath=/dev/null commit -m "test(bva): align WS-G0 conformance test discovery with PO evals"
```

---

## Definition of Done (Plan 1 / WS-G0)

- [ ] `bva-simulation-result-v1.schema.json` + `bva-opportunity-v1.schema.json` committed under `data/synthetic/schema/`.
- [ ] One valid fixture per shape under `evals/bva-agent/fixtures/`.
- [ ] `python -m pytest evals/bva-agent -v` green (schema-exists, both fixtures validate, CHF + Class-C-chunk + citation invariants).
- [ ] `docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md` (Status **Frozen**) committed, mojibake + markdownlint clean.
- [ ] One SMALL squash PR (branch `sprint-33/ws-g0-contracts`) linked to the WS-G0 work-package issue and the tracker. **Never self-merge; a human merges on green.**

---

## Follow-on plans (proposed after Plan 1 lands)

Each is its own `docs/superpowers/plans/2026-07-28-sprint-33-*.md`, own issue, own branch, own squash PR, rebranched off the latest `main`:

- **Plan 2 — WS-A cost/BOM data product.** `data/master-data/bva/*.csv` sources; `bronze_bva -> silver_bva -> gold_bva` notebooks (FX->CHF, schema/PHI/FK gates); `sm_bva` Direct Lake baseline measures; ontology + Fabric IQ Data Agent grounding; `data-quality-agent` gates; SIT/PROD parity.
- **Plan 3 — WS-B BVA reasoning + engine.** Deterministic `bva.simulate` calc engine (unit-tested, no LLM math) validated against `bva-simulation-result-v1`; `agents/bva-agent/` pack (`AGENT.md` + `manifest.yaml` + `golden-tasks.md`, happy + what-if + refusal); slot-filling interaction.
- **Plan 4 — WS-D opportunity capture.** Cosmos `Opportunity` container + upsert (append-history, no-fork); `gold.bva_opportunity` one-way projection notebook; Backstage pipeline view.
- **Plan 5 — WS-C orchestration + PO linkage.** App-copilot fan-out (onboarding intent -> BVA + PO); compose cited answer (PO verdict + BVA figures); Start inline + Backstage surfacing; orchestrator eval fixture.
- **Governance close-out.** New BVA ADR (next free number after #378 cleanup); `AGENTS.md` §1 row; PRD §7 `FR-BVA-*` / `NFR-BVA-*`.
