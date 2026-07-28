# ADR-0053 Ratification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move ADR-0053 from `Proposed` to `Accepted` by extracting the trust-score weight profiles + grounding-readiness thresholds into a versioned JSON source of truth with a deterministic stdlib-only loader, and recording the single-owner ratification + revision path.

**Architecture:** A git-tracked `trustscore-weights.json` (keyed by `modelVersion: trustscore-v1`) holds the three decision-class weight profiles and per-class thresholds. A pure `weights_config.py` loader (stdlib `json` only, path resolved via `__file__`) exposes `load_profile()` / `load_thresholds()` that plug into the existing `trust_score()` function. ADR-0053 §3/§4 keep human-readable tables but name the JSON as source of truth; new subsections record the ratification, the revision path, and the RACI-via-DQA stance. `docs/AI.md` / `docs/COMPLIANCE.md` flip "ratification pending" to "ratified." The grounding-readiness *gate* is explicitly out of scope (separate slice).

**Tech Stack:** Python 3.12 (stdlib only), `pytest` (unit tests), Markdown (ADR + governance docs), GitHub Actions `quality-lane.yml` (existing CI gate).

---

## Prerequisites & sequencing

- **Base branch:** Create the implementation branch off `main` **after PR #483 merges** (PR #483 adds the `## Data Quality Trust Score...` section to `docs/AI.md` and the DQA control table to `docs/COMPLIANCE.md` with "ratification pending" wording that Task 6 edits). If #483 is not yet merged when execution starts, either merge it first or rebase this branch onto it. Verify with:

  ```bash
  git fetch origin main
  git log origin/main --oneline -5 | grep -i "AI.md + COMPLIANCE.md Sprint 31 DQA" || echo "WAIT: #483 not yet on main"
  ```

- **Branch name:** `sprint-31/adr-0053-ratification`.
- **Test command (whole lane):** `python -m pytest data-platform/quality/tests -q` (run from repo root; matches `quality-lane.yml`).
- **Single-file test command:** `python -m pytest data-platform/quality/tests/test_weights_config.py -q`.
- Imports resolve because `data-platform/` has no `__init__.py` while `data-platform/quality/` and `data-platform/quality/tests/` do, so pytest adds `data-platform/` to `sys.path` and `quality` is importable (same mechanism as the existing `from quality.trust_score import ...`).

## File structure

- Create: `data-platform/quality/trustscore-weights.json` — the versioned source of truth (weight profiles + thresholds).
- Create: `data-platform/quality/weights_config.py` — deterministic stdlib loader (`load_profile`, `load_thresholds`, `config_model_version`).
- Create: `data-platform/quality/tests/test_weights_config.py` — loader + config-validity unit tests.
- Modify: `docs/adr/0053-dqa-trust-score-model.md` — `Accepted` + concrete §3 numbers + source-of-truth references + Ratification / Revision path / Ownership subsections.
- Modify: `docs/AI.md` — flip "ratification pending" to "ratified"; SemVer bump.
- Modify: `docs/COMPLIANCE.md` — flip "ratification pending" to "ratified" (if present); SemVer bump.

## Canonical values (single source — copy exactly)

Weight profiles are stored as **relative** weights; `trust_score()` normalizes by dividing by their sum, so `default` all-`1.0` reproduces the module's equal-weight default. Dimension order is the frozen `DIMENSIONS` tuple: `completeness, timeliness, validity, uniqueness, consistency, lineage_integrity, provenance, ontology_mapping`.

| Profile | completeness | timeliness | validity | uniqueness | consistency | lineage_integrity | provenance | ontology_mapping |
|---------|---|---|---|---|---|---|---|---|
| `default` | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| `crisis` | 2.0 | 3.0 | 1.0 | 1.0 | 1.0 | 1.0 | 2.0 | 1.0 |
| `planning` | 2.0 | 1.0 | 1.0 | 1.0 | 2.0 | 1.0 | 1.0 | 2.0 |

Thresholds (verbatim from ADR-0053 §4):

| Profile | overall | gating dimensions |
|---------|---------|-------------------|
| `default` | 0.80 | completeness 0.80, provenance 0.80, ontology_mapping 0.80 |
| `crisis` | 0.85 | timeliness 0.90, completeness 0.85, provenance 0.85 |
| `planning` | 0.80 | completeness 0.85, consistency 0.80, ontology_mapping 0.80 |

---

### Task 1: Config JSON + `load_profile` loader

**Files:**
- Create: `data-platform/quality/trustscore-weights.json`
- Create: `data-platform/quality/weights_config.py`
- Test: `data-platform/quality/tests/test_weights_config.py`

- [ ] **Step 1: Write the failing test**

Create `data-platform/quality/tests/test_weights_config.py`:

```python
"""Sprint 31 DQA -- trust-score weights/thresholds config loader tests.

The loader is a PURE, stdlib-only reader of the git-tracked
``trustscore-weights.json`` source of truth (ADR-0053). No randomness, no
network, no clock -- same call always returns the same dict.
"""
from __future__ import annotations

import unittest

from quality.trust_score import DIMENSIONS, MODEL_VERSION, trust_score
from quality.weights_config import (
    config_model_version,
    load_profile,
    load_thresholds,
)


class TestLoadProfile(unittest.TestCase):
    def test_default_profile_covers_all_dimensions_and_is_positive(self):
        profile = load_profile("default")
        self.assertEqual(set(profile), set(DIMENSIONS))
        self.assertTrue(all(v > 0 for v in profile.values()))
        self.assertGreater(sum(profile.values()), 0.0)

    def test_default_profile_is_equal_weight(self):
        profile = load_profile("default")
        first = profile[DIMENSIONS[0]]
        for dim in DIMENSIONS:
            self.assertEqual(profile[dim], first)

    def test_none_and_unknown_class_fall_back_to_default(self):
        self.assertEqual(load_profile(None), load_profile("default"))
        self.assertEqual(load_profile("no-such-class"), load_profile("default"))

    def test_crisis_upweights_timeliness_completeness_provenance(self):
        profile = load_profile("crisis")
        self.assertEqual(set(profile), set(DIMENSIONS))
        for up in ("timeliness", "completeness", "provenance"):
            self.assertGreater(profile[up], profile["validity"])

    def test_planning_upweights_completeness_consistency_ontology(self):
        profile = load_profile("planning")
        for up in ("completeness", "consistency", "ontology_mapping"):
            self.assertGreater(profile[up], profile["validity"])

    def test_config_model_version_matches_module(self):
        self.assertEqual(config_model_version(), MODEL_VERSION)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest data-platform/quality/tests/test_weights_config.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'quality.weights_config'`.

- [ ] **Step 3: Create the config JSON**

Create `data-platform/quality/trustscore-weights.json`:

```json
{
  "modelVersion": "trustscore-v1",
  "profiles": {
    "default":  { "completeness": 1.0, "timeliness": 1.0, "validity": 1.0, "uniqueness": 1.0, "consistency": 1.0, "lineage_integrity": 1.0, "provenance": 1.0, "ontology_mapping": 1.0 },
    "crisis":   { "completeness": 2.0, "timeliness": 3.0, "validity": 1.0, "uniqueness": 1.0, "consistency": 1.0, "lineage_integrity": 1.0, "provenance": 2.0, "ontology_mapping": 1.0 },
    "planning": { "completeness": 2.0, "timeliness": 1.0, "validity": 1.0, "uniqueness": 1.0, "consistency": 2.0, "lineage_integrity": 1.0, "provenance": 1.0, "ontology_mapping": 2.0 }
  },
  "thresholds": {
    "default":  { "overall": 0.80, "gating": { "completeness": 0.80, "provenance": 0.80, "ontology_mapping": 0.80 } },
    "crisis":   { "overall": 0.85, "gating": { "timeliness": 0.90, "completeness": 0.85, "provenance": 0.85 } },
    "planning": { "overall": 0.80, "gating": { "completeness": 0.85, "consistency": 0.80, "ontology_mapping": 0.80 } }
  }
}
```

- [ ] **Step 4: Create the loader module**

Create `data-platform/quality/weights_config.py`:

```python
"""Sprint 31 DQA -- deterministic loader for the trust-score weights/thresholds.

This module is the read side of the versioned ``trustscore-weights.json`` source
of truth ratified by ``docs/adr/0053-dqa-trust-score-model.md``. It is PURE and
stdlib-only: it parses a git-tracked JSON file resolved relative to ``__file__``
(never the CWD), so the same call always returns the same dict regardless of
where the process runs. No randomness, no network, no clock, no LLM estimate --
mirroring the determinism guarantees of ``trust_score.py``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from quality.trust_score import DIMENSIONS

_CONFIG_PATH = Path(__file__).with_name("trustscore-weights.json")
_DEFAULT = "default"


def _load() -> dict:
    with _CONFIG_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def config_model_version() -> str:
    """Return the ``modelVersion`` recorded in the config (e.g. ``trustscore-v1``)."""
    return str(_load()["modelVersion"])


def load_profile(decision_class: Optional[str] = None) -> Dict[str, float]:
    """Return the weight vector for ``decision_class`` (falls back to ``default``).

    The returned dict covers every dimension in :data:`DIMENSIONS`; values are
    relative weights that :func:`quality.trust_score.trust_score` normalizes.
    """
    profiles = _load()["profiles"]
    raw = profiles.get(decision_class or _DEFAULT, profiles[_DEFAULT])
    profile = {dim: float(raw[dim]) for dim in DIMENSIONS}
    if any(v <= 0 for v in profile.values()):
        raise ValueError(f"profile {decision_class!r} has a non-positive weight")
    return profile


def load_thresholds(decision_class: Optional[str] = None) -> Dict[str, object]:
    """Return ``{"overall": float, "gating": {dim: float}}`` for ``decision_class``.

    Falls back to the ``default`` profile for an unknown or ``None`` class. Used
    by the (separate-slice) grounding-readiness gate; not wired into a gate here.
    """
    thresholds = _load()["thresholds"]
    raw = thresholds.get(decision_class or _DEFAULT, thresholds[_DEFAULT])
    return {
        "overall": float(raw["overall"]),
        "gating": {dim: float(val) for dim, val in raw["gating"].items()},
    }
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `python -m pytest data-platform/quality/tests/test_weights_config.py -q`
Expected: PASS (6 tests).

- [ ] **Step 6: Commit**

```bash
git add data-platform/quality/trustscore-weights.json data-platform/quality/weights_config.py data-platform/quality/tests/test_weights_config.py
git commit -m "feat(dqa): versioned trustscore-weights.json + stdlib loader (ADR-0053)

Refs #453

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Copilot-Session: cfde1a64-d9e8-4c0f-ab4b-eaf06350bd6d"
```

---

### Task 2: `load_thresholds` behaviour + config-validity guards

**Files:**
- Test: `data-platform/quality/tests/test_weights_config.py` (append)

- [ ] **Step 1: Write the failing tests**

Append this class to `data-platform/quality/tests/test_weights_config.py`:

```python
class TestLoadThresholds(unittest.TestCase):
    def test_default_thresholds_shape_and_values(self):
        thr = load_thresholds("default")
        self.assertEqual(thr["overall"], 0.80)
        self.assertEqual(thr["gating"]["completeness"], 0.80)
        self.assertEqual(thr["gating"]["provenance"], 0.80)
        self.assertEqual(thr["gating"]["ontology_mapping"], 0.80)

    def test_crisis_thresholds_are_stricter_on_timeliness(self):
        thr = load_thresholds("crisis")
        self.assertEqual(thr["overall"], 0.85)
        self.assertEqual(thr["gating"]["timeliness"], 0.90)

    def test_planning_thresholds(self):
        thr = load_thresholds("planning")
        self.assertEqual(thr["overall"], 0.80)
        self.assertEqual(thr["gating"]["consistency"], 0.80)

    def test_none_and_unknown_class_fall_back_to_default(self):
        self.assertEqual(load_thresholds(None), load_thresholds("default"))
        self.assertEqual(load_thresholds("no-such-class"), load_thresholds("default"))

    def test_gating_dimensions_are_known_dimensions(self):
        for cls in ("default", "crisis", "planning"):
            for dim in load_thresholds(cls)["gating"]:
                self.assertIn(dim, DIMENSIONS)

    def test_thresholds_are_unit_interval(self):
        for cls in ("default", "crisis", "planning"):
            thr = load_thresholds(cls)
            self.assertTrue(0.0 <= thr["overall"] <= 1.0)
            self.assertTrue(all(0.0 <= v <= 1.0 for v in thr["gating"].values()))
```

- [ ] **Step 2: Run the tests to verify they fail... or pass**

Run: `python -m pytest data-platform/quality/tests/test_weights_config.py -q`
Expected: PASS — `load_thresholds` was implemented in Task 1, so these assertions confirm the JSON values are correct. If any FAIL, the JSON in Task 1 Step 3 has a wrong number; fix the JSON to match the canonical thresholds table, do not weaken the test.

- [ ] **Step 3: Commit**

```bash
git add data-platform/quality/tests/test_weights_config.py
git commit -m "test(dqa): assert trustscore thresholds match ADR-0053 §4

Refs #453

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Copilot-Session: cfde1a64-d9e8-4c0f-ab4b-eaf06350bd6d"
```

---

### Task 3: Integration — loaded profile drives `trust_score`

**Files:**
- Test: `data-platform/quality/tests/test_weights_config.py` (append)

- [ ] **Step 1: Write the failing test**

Append this class:

```python
class TestProfileDrivesTrustScore(unittest.TestCase):
    def test_default_profile_equals_module_default_score(self):
        dims = {d: 0.5 for d in DIMENSIONS}
        dims["completeness"] = 1.0
        with_config = trust_score("d", dims, weights=load_profile("default"))
        module_default = trust_score("d", dims)  # equal weights internally
        self.assertAlmostEqual(with_config["score"], module_default["score"], places=6)

    def test_crisis_profile_rewards_timeliness(self):
        # A domain strong on timeliness but weak elsewhere scores higher under
        # crisis weighting than under the equal-weight default.
        dims = {d: 0.2 for d in DIMENSIONS}
        dims["timeliness"] = 1.0
        crisis = trust_score("d", dims, weights=load_profile("crisis"))
        default = trust_score("d", dims, weights=load_profile("default"))
        self.assertGreater(crisis["score"], default["score"])

    def test_loaded_profile_is_accepted_by_trust_score_contract(self):
        out = trust_score("d", {x: 1.0 for x in DIMENSIONS}, weights=load_profile("planning"))
        self.assertEqual(out["contractId"], "DC-DQ-TRUSTSCORE-v1")
        self.assertEqual(out["score"], 1.0)
```

- [ ] **Step 2: Run the test to verify it passes**

Run: `python -m pytest data-platform/quality/tests/test_weights_config.py -q`
Expected: PASS. `test_default_profile_equals_module_default_score` proves the config `default` reproduces the built-in equal weighting; `test_crisis_profile_rewards_timeliness` proves the profile actually shifts the score.

- [ ] **Step 3: Run the whole quality lane to confirm no regression**

Run: `python -m pytest data-platform/quality/tests -q`
Expected: PASS — the pre-existing 18 trust-score/gap tests plus the new loader tests all green.

- [ ] **Step 4: Commit**

```bash
git add data-platform/quality/tests/test_weights_config.py
git commit -m "test(dqa): loaded weight profiles drive trust_score deterministically

Refs #453

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Copilot-Session: cfde1a64-d9e8-4c0f-ab4b-eaf06350bd6d"
```

---

### Task 4: Ratify ADR-0053 (accept + subsections + concrete §3 numbers)

**Files:**
- Modify: `docs/adr/0053-dqa-trust-score-model.md`

- [ ] **Step 1: Flip the status**

In the header table, change:

```markdown
| **Status** | Proposed |
```

to:

```markdown
| **Status** | Accepted |
```

- [ ] **Step 2: Make the §3 weight table concrete and name the source of truth**

Replace the §3 weighting table + the sentence after it. Find:

```markdown
   | Decision class | Weighting profile |
   |----------------|-------------------|
   | `default` | Equal weight across all eight dimensions. |
   | `crisis` / real-time steering | Up-weight `timeliness`, `completeness`, `provenance` (freshness and source-trust dominate under time pressure). |
   | `planning` / forecast grounding | Up-weight `completeness`, `consistency`, `ontology_mapping` (coverage and semantic alignment dominate). |

   Concrete weight vectors live with the model in code and are changed only by a
   `modelVersion` bump plus an update to this ADR.
```

Replace with:

```markdown
   | Decision class | completeness | timeliness | validity | uniqueness | consistency | lineage_integrity | provenance | ontology_mapping |
   |----------------|---|---|---|---|---|---|---|---|
   | `default` | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
   | `crisis` | 2.0 | 3.0 | 1.0 | 1.0 | 1.0 | 1.0 | 2.0 | 1.0 |
   | `planning` | 2.0 | 1.0 | 1.0 | 1.0 | 2.0 | 1.0 | 1.0 | 2.0 |

   Values are **relative** weights normalized by the model (so `default`
   reproduces equal weighting). The **source of truth** is
   `data-platform/quality/trustscore-weights.json` (`modelVersion: trustscore-v1`);
   this table is the human-readable mirror. Values change only by a
   `modelVersion` bump plus a config PR under the sign-off in the Ratification
   subsection below.
```

- [ ] **Step 3: Name the source of truth under the §4 thresholds table**

Immediately after the §4 grounding-readiness thresholds table (the block that ends with the `planning | ≥ 0.80 | ...` row), add a new paragraph:

```markdown
The **source of truth** for these thresholds is
`data-platform/quality/trustscore-weights.json` (`modelVersion: trustscore-v1`);
the table above is the human-readable mirror. The grounding-readiness *gate*
that enforces them (compare a domain's score/dimensions, then advise
degraded-mode or withhold) is a separate implementation slice.
```

- [ ] **Step 4: Add the Ratification / Revision path / Ownership subsections**

Immediately before the `## Consequences` heading, insert:

```markdown
## Ratification

The eight-dimension model, the three decision-class weight profiles (§3), and the
grounding-readiness thresholds (§4) are **ratified as an expert-set baseline** by
the single accountable owner **@urruegg** (platform / data-governance), consistent
with the repository's single-owner ADR acceptance practice. This is a deliberate,
signed baseline — not yet backtested against observed forecast/grounding impact
(see Revision path). Acceptance is recorded here rather than gated on a board
sign-off.

## Revision path

The weights and thresholds are expected to change as evidence accrues:

1. A **backtest-driven revision** is scheduled once the Sprint 30 evaluation
   harness has enough scored traces to compare the expert-set thresholds against
   observed impact.
2. A revision is a **config PR** to `trustscore-weights.json` + **single-owner
   sign-off** + a `modelVersion` bump (`trustscore-v{N}`), with this ADR's mirror
   tables updated in the same PR.
3. A **new superseding ADR** is required only when the **dimension set or the
   aggregation method** changes — not for tuning existing values.

## Ownership (RACI)

Every gold domain should have a named accountable owner. An **unowned** gold
domain is not an acceptance blocker: it surfaces as a `DC-DQ-GAP-v1` finding that
the DQA raises and routes, so the agent's own mechanism closes the RACI gap over
time.
```

- [ ] **Step 5: Update the Consequences → Status bullet**

Find:

```markdown
- **Status.** `Proposed` until the trust-score module + thresholds are exercised
  on ≥1 gold domain and the sprint is accepted, at which point this ADR moves to
  `Accepted`.
```

Replace with:

```markdown
- **Status.** `Accepted`. The trust-score module + thresholds are exercised on a
  gold domain (18 unit tests) and ratified as an expert-set baseline; the values
  now live in the versioned `trustscore-weights.json` source of truth.
```

- [ ] **Step 6: Add the config to the References list**

In `## References`, under the `Modules:` line, add the config path. Find:

```markdown
- Modules: `data-platform/quality/trust_score.py`, `data-platform/quality/gap_assessment.py`
```

Replace with:

```markdown
- Modules: `data-platform/quality/trust_score.py`, `data-platform/quality/gap_assessment.py`, `data-platform/quality/weights_config.py`
- Config (source of truth): `data-platform/quality/trustscore-weights.json` (`trustscore-v1`)
```

- [ ] **Step 7: Run the doc gates**

Run: `python scripts/lint/check_mojibake.py docs/adr/0053-dqa-trust-score-model.md`
Expected: `OK: no mojibake ...` (exit 0). Note: the ADR author line contains a legitimate `ü`; only new lines you added must stay clean — do not touch existing punctuation lines.

Run: `npx --yes markdownlint-cli2 "docs/adr/0053-dqa-trust-score-model.md"`
Expected: `Summary: 0 error(s)`.

- [ ] **Step 8: Commit**

```bash
git add docs/adr/0053-dqa-trust-score-model.md
git commit -m "docs(dqa): ratify ADR-0053 (Accepted) with versioned config source of truth

Refs #453

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Copilot-Session: cfde1a64-d9e8-4c0f-ab4b-eaf06350bd6d"
```

Note: the pre-commit hook regenerates `data/synthetic/.../evidence-demo.json` because an ADR changed. Let the hook `git add` it; include it in this commit if the hook stages it (verify with `git status` after the commit — if the working tree is dirty with the fixture, `git add` it and `git commit --amend --no-edit`).

---

### Task 5: Flip "ratification pending" → "ratified" in AI.md

**Files:**
- Modify: `docs/AI.md`

- [ ] **Step 1: Update the wording**

Find (in the `## Data Quality Trust Score and Grounding Readiness (Sprint 31)` section):

```markdown
   The dimension weights and per-decision-class thresholds are ADR-ratified in
   [ADR-0053](adr/0053-dqa-trust-score-model.md) (ratification pending).
```

Replace with:

```markdown
   The dimension weights and per-decision-class thresholds are ADR-ratified in
   [ADR-0053](adr/0053-dqa-trust-score-model.md) (Accepted), with the values held
   in the versioned `data-platform/quality/trustscore-weights.json`
   (`trustscore-v1`) source of truth.
```

- [ ] **Step 2: Bump the SemVer header (PATCH)**

Find:

```markdown
| **Version** | 0.13.0 |
```

Replace with:

```markdown
| **Version** | 0.13.1 |
```

Find:

```markdown
| **Previous Version** | 0.12.0 (added the Sprint 30 M5 Evaluation Curation + Advisory Backlog: selection policy over scored traces, versioned-dataset rows, advisory GitHub-issue drafts) |
```

Replace with:

```markdown
| **Previous Version** | 0.13.0 (added the Sprint 31 DQA trust-score/grounding section) |
```

- [ ] **Step 3: Run the doc gates**

Run: `python scripts/lint/check_mojibake.py docs/AI.md`
Expected: `OK` (exit 0).

Run: `npx --yes markdownlint-cli2 "docs/AI.md"`
Expected: `Summary: 0 error(s)`.

- [ ] **Step 4: Commit**

```bash
git add docs/AI.md
git commit -m "docs(dqa): mark ADR-0053 ratified in AI.md (0.13.0 -> 0.13.1)

Refs #453

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Copilot-Session: cfde1a64-d9e8-4c0f-ab4b-eaf06350bd6d"
```

---

### Task 6: Flip "ratification pending" → "ratified" in COMPLIANCE.md

**Files:**
- Modify: `docs/COMPLIANCE.md`

- [ ] **Step 1: Check whether the phrase is present**

Run: `python -c "import pathlib,sys; t=pathlib.Path('docs/COMPLIANCE.md').read_text(encoding='utf-8'); sys.exit(0 if 'ADR-0053' in t else 1)"`

The Sprint 31 DQA control section (added in PR #483) references ADR-0053 but does **not** contain the literal words "ratification pending" (only AI.md did). Confirm by inspection:

Run: `python -c "import pathlib; t=pathlib.Path('docs/COMPLIANCE.md').read_text(encoding='utf-8'); print('pending' in t.lower())"`

- If it prints `False` (expected): make no body change; only add a one-line note that the model is now ratified, to keep the doc current. In the Sprint 31 DQA control section, find the intro sentence ending `... impact (`DC-DQ-GAP-v1`).` and append a sentence:

  ```markdown
  The trust-score weights and thresholds are ratified in
  [ADR-0053](adr/0053-dqa-trust-score-model.md) (Accepted), held in the versioned
  `trustscore-weights.json` (`trustscore-v1`) source of truth.
  ```

- If it prints `True`: replace the "pending"-bearing sentence with the ratified wording analogous to Task 5 Step 1.

- [ ] **Step 2: Bump the SemVer header (PATCH)**

Find:

```markdown
| **Version** | 0.12.0 |
```

Replace with:

```markdown
| **Version** | 0.12.1 |
```

Find:

```markdown
| **Previous Version** | 0.11.1 (repointed the Curavias ADR link ADR-0040 -> ADR-0050 (#378)); this bump adds the Sprint 31 Data Quality Agent proactive-assessment control section |
```

Replace with:

```markdown
| **Previous Version** | 0.12.0 (added the Sprint 31 Data Quality Agent proactive-assessment control section); this bump records ADR-0053 as ratified |
```

- [ ] **Step 3: Run the doc gates**

Run: `python scripts/lint/check_mojibake.py docs/COMPLIANCE.md`
Expected: `OK` (exit 0). Note: COMPLIANCE.md has a pre-existing BOM on line 1 — leave it; do not rewrite the whole file.

Run: `npx --yes markdownlint-cli2 "docs/COMPLIANCE.md"`
Expected: `Summary: 0 error(s)`.

- [ ] **Step 4: Commit**

```bash
git add docs/COMPLIANCE.md
git commit -m "docs(dqa): record ADR-0053 ratified in COMPLIANCE.md (0.12.0 -> 0.12.1)

Refs #453

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Copilot-Session: cfde1a64-d9e8-4c0f-ab4b-eaf06350bd6d"
```

---

### Task 7: Final verification + open the PR

**Files:** none (verification only)

- [ ] **Step 1: Run the full quality lane one last time**

Run: `python -m pytest data-platform/quality/tests -q`
Expected: PASS (18 pre-existing + ~15 new loader tests).

- [ ] **Step 2: Run doc gates across every changed doc**

Run: `python scripts/lint/check_mojibake.py docs/adr/0053-dqa-trust-score-model.md docs/AI.md docs/COMPLIANCE.md`
Expected: `OK: no mojibake in 3 listed text file(s).`

Run: `npx --yes markdownlint-cli2 "docs/adr/0053-dqa-trust-score-model.md" "docs/AI.md" "docs/COMPLIANCE.md"`
Expected: `Summary: 0 error(s)`.

- [ ] **Step 3: Push and open the PR**

```bash
git push -u origin sprint-31/adr-0053-ratification
gh pr create --base main --head sprint-31/adr-0053-ratification \
  --title "docs(dqa): ratify ADR-0053 + versioned trustscore-weights.json source of truth" \
  --body-file - <<'BODY'
## What changed
- `docs/adr/0053-dqa-trust-score-model.md`: Status Proposed -> **Accepted**; concrete §3 weight numbers; §3/§4 name `trustscore-weights.json` as source of truth; new Ratification / Revision path / Ownership subsections.
- `data-platform/quality/trustscore-weights.json`: versioned (`trustscore-v1`) weight profiles + thresholds — the source of truth.
- `data-platform/quality/weights_config.py`: deterministic, stdlib-only loader (`load_profile`, `load_thresholds`, `config_model_version`).
- `data-platform/quality/tests/test_weights_config.py`: loader + config-validity + integration tests.
- `docs/AI.md` (0.13.0 -> 0.13.1) and `docs/COMPLIANCE.md` (0.12.0 -> 0.12.1): mark ADR-0053 ratified.

## Why
Closes the last Sprint 31 acceptance gap: ADR-0053 was `Proposed`; the DoD requires ADR-ratified weights/thresholds with a signed sign-off. Design: `docs/superpowers/specs/2026-07-28-adr-0053-ratification-design.md`. Refs #453.

## Requirements implemented
FR-DQA-003 (deterministic Trust Score — weights/thresholds ratified + versioned); FR-DQA-006 / FR-DQA-012 (thresholds ratified; gate wiring deferred to a separate slice); NFR-DQA-001 / NFR-DQA-002 (auditable, read-only).

## Test evidence
- `python -m pytest data-platform/quality/tests -q` -> PASS
- `python scripts/lint/check_mojibake.py ...` -> OK
- `npx markdownlint-cli2 ...` -> 0 error(s)

## Lane impact
Governance / AI / Compliance + data (quality lane). No infra, no security, no PHI.

## Impact statements
- Infra impact: none
- MCP allow-list impact: none
- Security impact: none (read-only; no new deps — stdlib JSON only)
- Eval impact: none (no prompt/golden-task change)
- Compliance impact: additive — records the ratified, auditable trust-score baseline

## Versioning contract
ADR uses Status field (no SemVer header); AI.md + COMPLIANCE.md PATCH-bumped per §9.
BODY
```

- [ ] **Step 4: Post-merge follow-up (record, do not execute here)**

After a human merges this PR, ADR-0053 is `Accepted`. No deploy is required (docs + pure Python; the app evidence fixture regenerates via the hook and rides the normal `evidence-publish` path). The grounding-readiness **gate** remains open as a separate future slice.

---

## Self-review

**Spec coverage** (against `docs/superpowers/specs/2026-07-28-adr-0053-ratification-design.md`):
- §4.1 ADR becomes ratification artefact → Task 4 (all subsections + status + source-of-truth refs). ✓
- §4.2 versioned JSON config → Task 1 Step 3. ✓
- §4.3 deterministic loader → Task 1 Step 4 (`load_profile`, `load_thresholds`, `config_model_version`). ✓
- §4.4 backtest recorded as future work → Task 4 Step 4 "Revision path". ✓
- §4.5 doc touch-up → Tasks 5 + 6. ✓
- §6 testing (loader coverage, default==equal, thresholds intact, 18 existing green) → Tasks 1–3, 7. ✓
- §7 non-goals (gate wiring, backtest itself) → explicitly deferred in Task 4 Step 3 + Task 7 Step 4. ✓

**Placeholder scan:** no TBD/TODO; every code + doc step shows exact content. ✓

**Type consistency:** `load_profile`, `load_thresholds`, `config_model_version`, `DIMENSIONS`, `trust_score`, `MODEL_VERSION` used identically across Tasks 1–3; JSON keys (`modelVersion`, `profiles`, `thresholds`, `overall`, `gating`) match between Task 1 Step 3 and the loader in Step 4. ✓
