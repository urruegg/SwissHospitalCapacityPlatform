# Data Quality Agent (DQA) Implementation Plan — Sprint 31

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Elevate `data-quality-agent` from ingestion gates to proactive assessment: a deterministic per-domain **Trust Score** + **gap detection with impact** + a frozen `DC-DQ-GAP-v1` "new-source-needed" seam, advisory + HITL + read-only.

**Architecture:** Two pure, deterministic Python modules under `data-platform/quality/` (mirroring `data-platform/decision/impact/compute_expected_impact.py` — no randomness, no LLM estimates), two `DC-*` JSON Schema contracts, an expanded `data-quality-agent` pack, and governance docs. The agent reads gold/serving metadata read-only and never edits source data.

**Tech Stack:** Python 3.11, pytest, JSON Schema (draft-07), the `dc-*-v1.schema.json` contract convention.

**Working dir for Python:** repo root; tests: `python -m pytest data-platform/quality/tests -q`.

**Scope:** Sprint 31 DQA MVP slice (closes #453; tracker #451). Design: [`docs/superpowers/specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md`](../specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md). SGA (Sprint 32) consumes the `DC-DQ-GAP-v1` seam this plan freezes.

---

## File structure

| File | Responsibility |
|------|----------------|
| `data/synthetic/schema/dc-dq-trustscore-v1.schema.json` *(create)* | Trust-score record contract. |
| `data/synthetic/schema/dc-dq-gap-v1.schema.json` *(create)* | Gap record contract (the SGA seam). |
| `data-platform/quality/__init__.py` *(create)* | Package marker. |
| `data-platform/quality/trust_score.py` *(create)* | Pure deterministic `trust_score()` + dimensions + model version. |
| `data-platform/quality/gap_assessment.py` *(create)* | Pure `assess_gaps()` → gap findings + `newSourceNeeded`. |
| `data-platform/quality/tests/test_trust_score.py` *(create)* | Trust-score unit tests. |
| `data-platform/quality/tests/test_gap_assessment.py` *(create)* | Gap-assessment unit tests. |
| `agents/data-quality-agent/AGENT.md` *(modify)* | Add proactive-assessment scope + trust score + gap→owner + grounding-readiness + seam. |
| `agents/data-quality-agent/manifest.yaml` *(modify)* | Reflect the expanded scope. |
| `agents/data-quality-agent/golden-tasks.md` *(modify)* | Add DQA fixtures. |
| `docs/adr/00NN-dqa-trust-score-model.md` *(create)* | Trust-score model + thresholds ADR. |
| `docs/DATA.md`, `docs/PRD.md` *(modify)* | Register contracts; `FR-DQA-*` + §7 traceability. |

---

## Task 1: `DC-DQ-TRUSTSCORE-v1` + `DC-DQ-GAP-v1` schema contracts

**Files:**
- Create: `data/synthetic/schema/dc-dq-trustscore-v1.schema.json`
- Create: `data/synthetic/schema/dc-dq-gap-v1.schema.json`

- [ ] **Step 1: Write `dc-dq-trustscore-v1.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://curavias/schema/dc-dq-trustscore-v1.schema.json",
  "title": "DC-DQ-TRUSTSCORE-v1",
  "type": "object",
  "required": ["contractId", "domain", "score", "dimensions", "modelVersion", "asOf"],
  "additionalProperties": true,
  "properties": {
    "contractId": { "const": "DC-DQ-TRUSTSCORE-v1" },
    "domain": { "type": "string" },
    "score": { "type": "number", "minimum": 0, "maximum": 1 },
    "dimensions": {
      "type": "object",
      "additionalProperties": { "type": "number", "minimum": 0, "maximum": 1 }
    },
    "decisionClass": { "type": "string" },
    "modelVersion": { "type": "string" },
    "asOf": { "type": "string", "format": "date-time" }
  }
}
```

- [ ] **Step 2: Write `dc-dq-gap-v1.schema.json`** (the frozen SGA seam)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://curavias/schema/dc-dq-gap-v1.schema.json",
  "title": "DC-DQ-GAP-v1",
  "type": "object",
  "required": ["contractId", "gapId", "domain", "dimension", "impactScore", "newSourceNeeded", "owner", "status"],
  "additionalProperties": true,
  "properties": {
    "contractId": { "const": "DC-DQ-GAP-v1" },
    "gapId": { "type": "string", "pattern": "^GAP-[0-9a-f]+$" },
    "domain": { "type": "string" },
    "detected": { "type": "string", "format": "date-time" },
    "dimension": { "type": "string" },
    "impactedKpi": { "type": "array", "items": { "type": "string" } },
    "impactedAgents": { "type": "array", "items": { "type": "string" } },
    "impactScore": { "type": "number", "minimum": 0, "maximum": 1 },
    "recommendedSource": { "type": "object" },
    "newSourceNeeded": { "type": "boolean" },
    "owner": { "type": "string" },
    "effort": { "type": "string", "enum": ["S", "M", "L"] },
    "status": { "type": "string", "enum": ["open", "routed", "closed"] }
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add data/synthetic/schema/dc-dq-trustscore-v1.schema.json data/synthetic/schema/dc-dq-gap-v1.schema.json
git commit -m "feat(dqa): DC-DQ-TRUSTSCORE-v1 + DC-DQ-GAP-v1 schema contracts"
```

---

## Task 2: Deterministic trust-score module

**Files:**
- Create: `data-platform/quality/__init__.py` (empty), `data-platform/quality/trust_score.py`
- Test: `data-platform/quality/tests/test_trust_score.py` (create `tests/__init__.py` too)

- [ ] **Step 1: Write the failing test**

```python
"""Sprint 31 DQA — deterministic trust-score tests."""
from __future__ import annotations

import pytest

from data_platform_quality.trust_score import trust_score, DIMENSIONS, MODEL_VERSION


def _full(v: float) -> dict:
    return {d: v for d in DIMENSIONS}


def test_perfect_score_is_one():
    out = trust_score("staffing.skills", _full(1.0))
    assert out["score"] == 1.0
    assert out["contractId"] == "DC-DQ-TRUSTSCORE-v1"
    assert out["modelVersion"] == MODEL_VERSION
    assert set(out["dimensions"]) == set(DIMENSIONS)


def test_equal_weights_average():
    dims = _full(0.5)
    dims["completeness"] = 1.0
    out = trust_score("staffing.skills", dims)
    # 7*0.5 + 1.0 = 4.5 over 8 dims = 0.5625
    assert out["score"] == pytest.approx(0.5625)


def test_missing_dimension_raises():
    dims = _full(1.0)
    del dims["provenance"]
    with pytest.raises(ValueError):
        trust_score("d", dims)


def test_out_of_range_raises():
    dims = _full(1.0)
    dims["validity"] = 1.5
    with pytest.raises(ValueError):
        trust_score("d", dims)
```

> **Note:** import path — add `pythonpath` for `data-platform/quality` in the test invocation, or place a `conftest.py` at `data-platform/quality/` that inserts its parent on `sys.path` as `data_platform_quality`. Simplest: create `data-platform/quality/conftest.py` with `import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))` and import as `from quality.trust_score import ...`. Match whichever import style the repo's other `data-platform` tests use; if none, use the `conftest.py` + `from quality.trust_score import ...` form and update the test import accordingly.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/quality/tests/test_trust_score.py -q`
Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

```python
"""Sprint 31 DQA — deterministic, versioned trust score (design §6).

NO randomness, NEVER an LLM estimate: same inputs always produce the same score.
Mirrors data-platform/decision/impact/compute_expected_impact.py.
"""
from __future__ import annotations

from typing import Dict, Optional

DIMENSIONS = (
    "completeness", "timeliness", "validity", "uniqueness",
    "consistency", "lineage_integrity", "provenance", "ontology_mapping",
)
MODEL_VERSION = "trustscore-v1"
_EQUAL_WEIGHT = 1.0 / len(DIMENSIONS)


def _validate(dimensions: Dict[str, float]) -> None:
    for d in DIMENSIONS:
        if d not in dimensions:
            raise ValueError(f"missing dimension {d!r}")
        v = dimensions[d]
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not (0.0 <= v <= 1.0):
            raise ValueError(f"dimension {d!r} must be a number in [0,1], got {v!r}")


def trust_score(
    domain: str,
    dimensions: Dict[str, float],
    weights: Optional[Dict[str, float]] = None,
    decision_class: Optional[str] = None,
) -> Dict[str, object]:
    """Return a DC-DQ-TRUSTSCORE-v1-shaped dict for one domain."""
    _validate(dimensions)
    w = weights or {d: _EQUAL_WEIGHT for d in DIMENSIONS}
    total_w = sum(w[d] for d in DIMENSIONS)
    score = sum(w[d] * dimensions[d] for d in DIMENSIONS) / total_w
    return {
        "contractId": "DC-DQ-TRUSTSCORE-v1",
        "domain": domain,
        "score": round(score, 4),
        "dimensions": {d: dimensions[d] for d in DIMENSIONS},
        "decisionClass": decision_class,
        "modelVersion": MODEL_VERSION,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest data-platform/quality/tests/test_trust_score.py -q`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add data-platform/quality/__init__.py data-platform/quality/trust_score.py data-platform/quality/tests/
git commit -m "feat(dqa): deterministic versioned trust-score module"
```

---

## Task 3: Gap-assessment module (+ the seam)

**Files:**
- Create: `data-platform/quality/gap_assessment.py`
- Test: `data-platform/quality/tests/test_gap_assessment.py`

- [ ] **Step 1: Write the failing test**

```python
"""Sprint 31 DQA — gap assessment + newSourceNeeded seam tests."""
from __future__ import annotations

from data_platform_quality.gap_assessment import assess_gaps


IMPACT_MAP = {
    "staffing.skills": {
        "impactedKpi": ["skills-based-assignment", "forecast-accuracy"],
        "impactedAgents": ["sba-agent"],
        "recommendedSource": {"kind": "certification-register", "example": "NAREG / FMH"},
        "newSourceNeeded": True,
    },
}
THRESHOLDS = {"completeness": 0.8, "timeliness": 0.8, "validity": 0.8}


def test_below_threshold_dimension_yields_a_gap():
    gaps = assess_gaps(
        "staffing.skills",
        metrics={"completeness": 0.4, "timeliness": 0.9, "validity": 0.95},
        thresholds=THRESHOLDS,
        impact_map=IMPACT_MAP,
    )
    assert len(gaps) == 1
    g = gaps[0]
    assert g["contractId"] == "DC-DQ-GAP-v1"
    assert g["dimension"] == "completeness"
    assert g["domain"] == "staffing.skills"
    assert g["newSourceNeeded"] is True
    assert "sba-agent" in g["impactedAgents"]
    assert 0.0 <= g["impactScore"] <= 1.0
    assert g["status"] == "open"
    assert g["gapId"].startswith("GAP-")


def test_all_above_threshold_yields_no_gap():
    gaps = assess_gaps(
        "staffing.skills",
        metrics={"completeness": 0.95, "timeliness": 0.9, "validity": 0.95},
        thresholds=THRESHOLDS,
        impact_map=IMPACT_MAP,
    )
    assert gaps == []


def test_unknown_domain_defaults_to_no_source_needed():
    gaps = assess_gaps(
        "unmapped.domain",
        metrics={"completeness": 0.1},
        thresholds={"completeness": 0.8},
        impact_map=IMPACT_MAP,
    )
    assert len(gaps) == 1
    assert gaps[0]["newSourceNeeded"] is False
    assert gaps[0]["impactedAgents"] == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/quality/tests/test_gap_assessment.py -q`
Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

```python
"""Sprint 31 DQA — deterministic gap assessment (design §6, §8).

Emits DC-DQ-GAP-v1 findings for each below-threshold dimension. The
``newSourceNeeded`` flag on a mapped domain is the frozen seam Sprint 32 SGA
consumes. NO randomness, NEVER an LLM estimate.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional


def _gap_id(domain: str, dimension: str) -> str:
    return "GAP-" + hashlib.sha256(f"{domain}:{dimension}".encode()).hexdigest()[:16]


def assess_gaps(
    domain: str,
    metrics: Dict[str, float],
    thresholds: Dict[str, float],
    impact_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Return DC-DQ-GAP-v1 findings for dimensions below their threshold."""
    impact_map = impact_map or {}
    dom = impact_map.get(domain, {})
    gaps: List[Dict[str, Any]] = []
    for dimension, threshold in sorted(thresholds.items()):
        value = metrics.get(dimension)
        if value is None or value >= threshold:
            continue
        # impact = normalised shortfall vs threshold (deterministic, in [0,1])
        impact = round((threshold - value) / threshold, 4) if threshold else 1.0
        gaps.append({
            "contractId": "DC-DQ-GAP-v1",
            "gapId": _gap_id(domain, dimension),
            "domain": domain,
            "dimension": dimension,
            "impactedKpi": list(dom.get("impactedKpi", [])),
            "impactedAgents": list(dom.get("impactedAgents", [])),
            "impactScore": impact,
            "recommendedSource": dom.get("recommendedSource", {}),
            "newSourceNeeded": bool(dom.get("newSourceNeeded", False)),
            "owner": dom.get("owner", f"data-owner:{domain.split('.')[0]}"),
            "effort": dom.get("effort", "M"),
            "status": "open",
        })
    return gaps
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest data-platform/quality/tests/test_gap_assessment.py -q`
Expected: PASS (3 passed). Then run the whole quality suite: `python -m pytest data-platform/quality/tests -q`.

- [ ] **Step 5: Commit**

```bash
git add data-platform/quality/gap_assessment.py data-platform/quality/tests/test_gap_assessment.py
git commit -m "feat(dqa): gap assessment + DC-DQ-GAP-v1 new-source-needed seam"
```

---

## Task 4: Expand the `data-quality-agent` pack

**Files:**
- Modify: `agents/data-quality-agent/AGENT.md`, `agents/data-quality-agent/manifest.yaml`

- [ ] **Step 1: Extend the AGENT.md scope** — under `## 2. Scope` → `### In scope`, add:

```markdown
- **Proactive quality assessment (beyond gates).** Score gold/serving domains on the
  eight trust dimensions (completeness, timeliness, validity, uniqueness, consistency,
  lineage-integrity, provenance, ontology-mapping) via the deterministic
  `data-platform/quality/trust_score.py`; publish a `DC-DQ-TRUSTSCORE-v1` record.
- **Gap detection + impact + owner routing.** Emit `DC-DQ-GAP-v1` findings via
  `data-platform/quality/gap_assessment.py`; route each to the accountable data owner
  (advisory / HITL); set `newSourceNeeded` to hand off to the Signal Agent (SGA).
- **Grounding-readiness certification (GA-gated).** Certify a domain grounding-ready only
  when trust score + completeness + provenance + ontology-mapping are all above the
  ADR-ratified threshold; otherwise advise degraded-mode, never silently serve.
```

- [ ] **Step 2: Add to `### Out of scope`:**

```markdown
- Editing / writing source data (DQA is read-only; owners remediate).
- Self-certifying a domain grounding-ready without owner remediation of open gaps.
```

- [ ] **Step 3: Bump the AGENT.md version header** (MINOR — additive scope). Update `Version`, `Date`, `Previous Version` per copilot-instructions §9.

- [ ] **Step 4: Update `manifest.yaml`** — reflect the expanded scope in its description/capabilities field (match the manifest's existing schema; do not invent new keys).

- [ ] **Step 5: Commit**

```bash
git add agents/data-quality-agent/AGENT.md agents/data-quality-agent/manifest.yaml
git commit -m "feat(dqa): expand data-quality-agent to proactive assessment + trust score + gap seam"
```

---

## Task 5: Golden-task fixtures

**Files:**
- Modify: `agents/data-quality-agent/golden-tasks.md`

- [ ] **Step 1: Add four fixtures** (match the existing golden-task structure in the file): (a) happy-path publish a `DC-DQ-TRUSTSCORE-v1` for one gold domain; (b) a below-threshold dimension → `DC-DQ-GAP-v1` routed to a named owner; (c) below-threshold domain → grounding-readiness **withheld** (degraded-mode advised, not served); (d) failure-mode refusal — asked to edit source data or self-certify → refuse (read-only + no self-cert). Each fixture references the `FR-DQA-*` IDs it verifies via the front-matter `requirement:` key.

- [ ] **Step 2: Bump the golden-tasks version header + front-matter `version` / `last-reviewed`.**

- [ ] **Step 3: Commit**

```bash
git add agents/data-quality-agent/golden-tasks.md
git commit -m "test(dqa): golden-task fixtures for trust score + gap + degraded-mode + refusal"
```

---

## Task 6: Governance ADR + PRD + DATA docs

**Files:**
- Create: `docs/adr/00NN-dqa-trust-score-model.md` (next free ADR number)
- Modify: `docs/PRD.md`, `docs/DATA.md`

- [ ] **Step 1: Write the ADR** — trust-score model (the eight dimensions + weighting), thresholds per decision class, the read-only/advisory/HITL posture, and the `DC-DQ-GAP-v1` seam. Status `Proposed`. Use the next free ADR number (check `docs/adr/` for the highest; resolve any collision per ADR-0041).

- [ ] **Step 2: Add `FR-DQA-*` / `NFR-DQA-*` rows to `docs/PRD.md` §7** (headline IDs from design §13) and bump the PRD version (MINOR).

- [ ] **Step 3: Register both contracts in `docs/DATA.md`** — add rows to the "Suggested Contract Groups" table for `DC-DQ-TRUSTSCORE-v1` and `DC-DQ-GAP-v1`; bump the DATA version (MINOR).

- [ ] **Step 4: Run doc gates** (repo root): `python scripts/lint/check_mojibake.py docs/adr/00NN-dqa-trust-score-model.md docs/PRD.md docs/DATA.md` then `npx --yes markdownlint-cli2 "docs/adr/00NN-dqa-trust-score-model.md" "docs/PRD.md" "docs/DATA.md"`. Expected: clean.

- [ ] **Step 5: Commit**

```bash
git add docs/adr/00NN-dqa-trust-score-model.md docs/PRD.md docs/DATA.md
git commit -m "docs(dqa): trust-score ADR + FR-DQA-* PRD rows + contract registration"
```

---

## Final verification

- [ ] `python -m pytest data-platform/quality/tests -q` — all green.
- [ ] Trust score is deterministic (same inputs → same score) and explainable (dimensions echoed).
- [ ] `DC-DQ-GAP-v1` `newSourceNeeded` is set for a mapped domain — the frozen seam for Sprint 32 SGA.
- [ ] Doc gates green on all edited docs; no PHI in any artefact.

---

## Self-review checklist (run before opening the PR)

- Spec coverage: D0=T1, D1=T2, D2=T3, D3=T4, D4=T5, D5=T6 — all design §11 Sprint-31 milestones mapped.
- No placeholders except the two flagged `Note`s (import-path style + ADR number), which are genuine environment lookups the implementer resolves.
- Type consistency: `trust_score()` / `assess_gaps()` signatures match their tests; contract keys match the JSON Schemas.
