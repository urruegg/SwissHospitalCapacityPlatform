# Sprint 26 WS-A — Foresight Tier Implementation Plan

> **Status: ✅ COMPLETE — merged to `main` 2026-07-24** (PR #346 core; #351/#353 Fabric SIT evidence). Live SIT: `fact_occupancy_forecast` 73 · `fact_forecast_driver` 292 · `fact_signal` 4 (Trust-A). See [`docs/architecture/foresight-fabric-evidence.md`](../../architecture/foresight-fabric-evidence.md) and design spec §9. Semantic-model TMDL + verify-gate rebaseline deferred to the **WS-A2** stacked slice (Open decision Q1). Next slice: **WS-B** (`sprint-26/ws-b-levers`).
>
> **For agentic workers:** REQUIRED SUB-SKILL — implement task-by-task with `superpowers:test-driven-development` (tests first) and `superpowers:e2e-medallion-architecture` + `superpowers:spark-authoring` (bronze/silver/gold + notebook patterns). Steps use checkbox (`- [ ]`) syntax. No completion claim without fresh command evidence (`superpowers:verification-before-completion`).

**Issue:** #335 · **Branch:** `sprint-26/ws-a-foresight` (off `main`) · **Lane:** Data (+ AI grounding) · **Design source of truth:** [`docs/superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md`](../specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md) §3.2 / §4 WS-A / §5 Slice 1.

---

## Goal

Land **only the Foresight tier** (design WS-A) as one small, human-reviewed squash PR: a
**synthetic, deterministic** forecast + driver + signal generator in the medallion, three
Gold Delta tables, and the matching ontology extension — with a clean seam (design D2) to
swap in a real forecasting model later. **No LLM-guessed numbers.** The Decision +
Coordination (Cosmos) tiers (WS-B / WS-C) stay **out of this branch**.

## Scope — in / out

**In (this PR):**

1. Deterministic Foresight generator (Spark-free pure functions + Fabric `run()` wrapper), mirroring `data-platform/notebooks/external-signals/build_gold_*.py`.
2. Gold Delta tables: `gold.fact_occupancy_forecast`, `gold.fact_forecast_driver`, `gold.fact_signal`.
3. Ontology extension on `reference-layer.ttl` + `crosswalk.md`: `hcp:Forecast`, `hcp:Driver`, `hcp:Ward` (stub range target) + relations `hcp:forWard`, `hcp:explainedBy`, `hcp:evidencedBy` (evidence range = existing `hcp:ExternalSignal`).
4. Two new data contracts (JSON schema): `DC-OCCUPANCY-FORECAST-v1`, `DC-FORECAST-DRIVER-v1` (the STRICT ontology-conformance gate requires a schema for every crosswalk contract).
5. Unit + schema-conformance tests (TDD, `unittest`), doc updates + SemVer bumps.

**Out (later stacked slices / other work-streams):**

- Semantic-model TMDL tables/measures/RLS + `verify-semantic-model.yml` count rebaseline → **WS-A2** stacked PR (see Open decision Q1).
- Lever catalog, `compute_expected_impact`, barrier model → **WS-B**.
- Cosmos `proposed_actions` / `plans`, HITL recompute, golden-thread sync → **WS-C**.
- `DC-INSIGHT-v1` Data Agent contract, 6 Foundry agent upgrades, the big descriptive→prescriptive **ADR**, PRD FR/NFR rows → **WS-D** (see Open decision Q3).

## Architecture — mirror the proven external-signals pattern

- **Heavy Spark I/O in `run()` only** (`# pragma: no cover`); all transform logic is Spark-free pure functions unit-tested offline — exactly like `build_gold_signals.py` / `build_gold_forecast_adjustment.py`.
- **Empty-frame guard:** every writer uses an explicit `_empty_schema(name)` so an empty input still writes a well-typed Delta table (the repo's `if q_count` / `_empty_schema` convention).
- **Deterministic seam (D2):** occupancy forecast, driver decomposition and signal probability are pure functions of `(ward baseline, synthetic admission/discharge series, seed)` — no randomness that isn't seeded, no model. A `MODEL_RUN_ID = "foresight-synthetic-v0.1"` marks the swap-in point for a real model.
- **Signal reuse:** `gold.fact_signal` is a Foresight-scoped projection over the existing Sprint 21 `gold.ext_fact_signal` (Trust-A, `DC-EXT-SIGNAL-v1`) carrying `trust_tier` + a deterministic `probability`, linked to drivers via `evidencedBy`. We do **not** duplicate the Sprint 21 signal spine.

## Tech stack

Python 3 stdlib only (`python`, not `python3`) for pure functions + `unittest`; PySpark inside `run()` (Fabric runtime); JSON Schema (draft-07) for contracts; Markdown + Turtle for ontology/docs.

---

## Hard constraints (apply to every task)

- **Runtime `python`, not `python3`.**
- **Commit with hooks disabled** (Windows mojibake pre-commit false-fails): `git -c core.hooksPath=/dev/null commit -m "..."` — after verifying `python scripts/lint/check_mojibake.py` passes manually.
- **Synthetic / no-PHI only** (ADR-0013 / ADR-0016). Forecast/driver rows carry no patient identifiers; signal rows carry only public-authority hazard data.
- **Advisory-only, no writeback.** WS-A is read-only-producing Gold tables; no Cosmos, no source/EHR writeback.
- **Trunk-based:** one issue → short-lived branch → **one squash PR** linked to **#335**. **Human reviews + merges. Never self-merge.**
- **Every edited doc** bumps its SemVer header (§9) + updates `Previous Version`; run `markdownlint` + `python scripts/lint/check_mojibake.py`.
- **Ontology change discipline:** any `reference-layer.ttl` edit updates `crosswalk.md` in the same PR and bumps the TTL `owl:versionInfo` + crosswalk/README SemVer; `check_crosswalk_conformance.py --strict` must pass.

---

## File structure

### New — Foresight medallion notebooks (`data-platform/notebooks/foresight/`)

- `build_gold_forecast.py` — pure fns `build_occupancy_forecast(...)`, `build_forecast_drivers(...)`, `_empty_schema(name)`, `write_gold_tables(...)`, `run()`.
- `build_gold_signal.py` — pure fn `to_foresight_signal(ext_row, probability)` + `foresight_signals(ext_rows, drivers)` join; folded into `write_gold_tables` or a sibling `run()`.
- `run_foresight_medallion.ipynb` — thin orchestration notebook calling the two `run()`s (mirrors `run_ext_medallion.ipynb`).
- `README.md` — design + medallion chain + table names + offline test command (mirrors external-signals README).
- `tests/__init__.py`, `tests/test_forecast_pure.py`, `tests/test_signal_pure.py`, `tests/test_schema_conformance.py`.

### New — data contracts (`data/synthetic/schema/`)

- `dc-occupancy-forecast-v1.schema.json` — per ward × horizon 0..72h occupancy %/beds (envelope mirrors `dc-demand-forecast-v1`).
- `dc-forecast-driver-v1.schema.json` — decomposition rows (`factor` ∈ admissions/discharges/transfers/seasonality, `delta`, links to forecast point + optional signal).

### Modified — ontology + docs (SemVer bumps)

- `docs/ontology/reference-layer.ttl` — add `hcp:Forecast`, `hcp:Driver`, `hcp:Ward` + 3 relations; bump `owl:versionInfo` (MINOR, additive).
- `docs/ontology/crosswalk.md` — add MVO rows + relation rows + base-spec traceability; MINOR.
- `docs/ontology/README.md` — bump only if content changes (else untouched).
- `docs/DATA.md` — document the three Foresight Gold tables + two new contracts; MINOR.
- `docs/superpowers/specs/...-sprint-26-...design.md` — untouched (approved; no edit).

---

## Tasks (TDD order — tests before implementation) — ✅ all complete

- [x] **T1 — Contracts first.** Write `dc-occupancy-forecast-v1` + `dc-forecast-driver-v1` JSON schemas; add a `test_schema_conformance.py` asserting generator output validates (fails until T3).
- [x] **T2 — Pure-function tests.** `test_forecast_pure.py`: determinism (same seed ⇒ identical rows), driver decomposition sums reconcile to net forecast delta, empty input ⇒ empty typed frame. `test_signal_pure.py`: Trust-A filter, deterministic probability, `evidencedBy` linkage. (All red.)
- [x] **T3 — Implement pure functions** in `build_gold_forecast.py` + `build_gold_signal.py` until T1+T2 green.
- [x] **T4 — Spark wrappers** `run()` + `_empty_schema` + `write_gold_tables` (marked `# pragma: no cover`) + `run_foresight_medallion.ipynb`.
- [x] **T5 — Ontology extension** in `reference-layer.ttl` + `crosswalk.md`; run `python scripts/ontology/check_crosswalk_conformance.py --strict` → PASS.
- [x] **T6 — Docs** — `data-platform/notebooks/foresight/README.md`; update `docs/DATA.md`; SemVer bumps on every edited doc.
- [x] **T7 — Verify + evidence** — targeted tests + lint pasted in #346; **live Fabric SIT evidence** captured in #351/#353 → [`docs/architecture/foresight-fabric-evidence.md`](../../architecture/foresight-fabric-evidence.md).

## Test / verification strategy (the smallest targeted commands)

```bash
# Pure + schema-conformance unit tests for the new lane
cd data-platform/notebooks/foresight
python -m unittest discover -s tests -v

# STRICT ontology two-layer conformance (new classes must map + have schemas)
cd ../../..
python scripts/ontology/check_crosswalk_conformance.py --strict

# Synthetic-dataset schema validation (if the new contracts are wired into validate)
python data/synthetic/validate_datasets.py   # only if T1 registers the new schemas

# Doc gates
python scripts/lint/check_mojibake.py
npx --yes markdownlint-cli2 "docs/ontology/**/*.md" "docs/DATA.md" "data-platform/notebooks/foresight/README.md"
```

## Definition of done (this slice) — ✅ met (semantic-model deferred to WS-A2)

- [x] Three Gold tables produced by deterministic pure functions; empty-input guarded; unit tests green.
- [x] Two contracts added; generated rows validate against them.
- [x] Ontology `hcp:Forecast`/`hcp:Driver` + relations live (reuse `hcp:ExternalSignal` per Q2); `--strict` conformance PASS.
- [x] All edited docs SemVer-bumped; mojibake + markdownlint clean.
- [x] PR lists FR/NFR IDs, lane impact, test evidence, references #335. Not self-merged (merged by @urruegg).

---

## Open decisions — RESOLVED (@urruegg, 2026-07-23/24)

- **Q1 — Semantic model in-scope for THIS PR?** → **Deferred to WS-A2** stacked PR. This Foresight-generator PR stayed reviewable; the `verify-semantic-model.yml` count rebaseline lands with the measures when the app/agent slice needs them.
- **Q2 — `hcp:Signal` naming.** → **Reused `hcp:ExternalSignal`** (Sprint 21) as the `evidencedBy` range; added only `hcp:Forecast` + `hcp:Driver` (+ `hcp:Ward` stub). No duplicate concept.
- **Q3 — PRD FR/NFR + ADR timing.** → This PR referenced existing `FR-FC-001..006` + `FR-EXT-ONT-001`; new IDs + the descriptive→prescriptive ADR **deferred to WS-D**.
