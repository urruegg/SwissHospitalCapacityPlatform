# ADR-0053 Ratification — DQA trust-score weights + grounding-readiness thresholds (Design)

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rueegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (new document) |
| **Sprint** | 31 — Data Quality Agent (DQA) follow-up |
| **Skill** | Authored via the Superpowers `brainstorming` skill |
| **Source** | [ADR-0053](../../adr/0053-dqa-trust-score-model.md) (Proposed) + [Sprint 31-32 DQA/SGA design](2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md) §12 open questions |

> **Purpose**: Close the last Sprint 31 acceptance gap. ADR-0053 is still
> `Proposed`; the sprint Definition of Done and design §12 require the
> trust-score weights + per-decision-class thresholds to be **ADR-ratified**,
> with the open question *"who signs."* This design fixes the ratification
> approach so ADR-0053 can move to `Accepted`.

---

## 1. Problem and goal

Sprint 31 shipped a deterministic, versioned, explainable trust score
(`data-platform/quality/trust_score.py`, 18 unit tests) plus the `DC-DQ-*`
contracts, agent pack, golden tasks, PRD requirements, and CI. Everything is
merged and live at SIT + PROD parity. **One gap remains:**
[ADR-0053](../../adr/0053-dqa-trust-score-model.md) is `Proposed`, so the
model's **weights** (three decision-class profiles) and **grounding-readiness
thresholds** are not yet an accepted, signed decision. Design §12 lists three
open questions:

1. The values are **expert-set, not backtested** against real forecast impact.
2. **Who signs** the weights/thresholds.
3. **RACI completeness** — is every gold domain owned?

**Goal:** ratify ADR-0053 with a governance approach that fits how this repo
already works, so acceptance is unblocked *now* without inventing new process,
while keeping an honest, auditable path to backtest-driven revision.

## 2. Decisions (user-approved during brainstorming)

| # | Question | Decision |
|---|----------|----------|
| Q1 | Sign-off authority | **Single accountable owner** (`@urruegg`, platform/data-governance) signs the ADR — consistent with every other accepted ADR in the repo. No RACI board. |
| Q2 | Ratification vehicle | **Accept now** with expert-set values as a **versioned baseline**; schedule a backtest-driven revision once the Sprint 30 eval harness has enough scored traces. |
| Q3 | Future revision governance | Values live in a **versioned config file** (`trustscore-weights.json`, keyed by `trustscore-v1`) that is the source of truth; the ADR references it; changes go via **PR + single-owner sign-off + `modelVersion` bump**. |
| Q4 | RACI completeness | **Accept now**; an unowned gold domain is a `DC-DQ-GAP-v1` finding the DQA raises and routes — the agent's own mechanism closes the RACI gap. Not an acceptance blocker. |
| Scope | Gate implementation | Ratification is **docs + config + loader only**. The grounding-readiness threshold *gate* wiring is a **separate slice**, keeping ratification tight and acceptance fast. |

## 3. Approach (selected: A — accept-now with versioned config baseline)

Two alternatives were considered and set aside:

- **B — Provisional-accept with hard expiry.** Same as A but thresholds carry a
  hard review-by date that force-flips the ADR back to review. Rejected as the
  default: it adds calendar-driven process the repo does not otherwise use and
  risks an artificial "expired" state during demo scope. The scheduled-revision
  trigger in A gives the same rigor without the forcing calendar.
- **C — Gate-on-backtest.** Keep the ADR `Proposed` until a backtest validates
  the values. Rejected: it blocks the Sprint 31 DoD indefinitely (Q2).

Approach **A** matches all four decisions: accept the expert-set values as a
signed baseline, move the concrete values into a versioned config that is the
single source of truth, and record an explicit, low-friction revision path.

## 4. What changes

### 4.1 ADR-0053 becomes the ratification artefact

- `Status: Proposed -> Accepted`; `Decision-makers: @urruegg`.
- New **"Ratification"** subsection recording *what* was signed (the eight-dimension
  model, the `default`/`crisis`/`planning` weight profiles, the grounding-readiness
  threshold tables), *by whom* (`@urruegg`, single accountable owner), and *on what
  basis* (expert-set baseline; backtest pending — see §4.4).
- §3 (weight profiles) and §4 (thresholds): keep the tables as the human-readable
  record, but add a line naming
  `data-platform/quality/trustscore-weights.json` (`trustscore-v1`) as the
  **source of truth**, replacing the current "concrete weight vectors live with
  the model in code" wording (which is not yet true — see §5).
- New **"Revision path"** subsection: values are expert-set now; a
  backtest-driven revision is scheduled once the Sprint 30 eval harness has
  enough scored traces; a revision is a **config PR + single-owner sign-off +
  `modelVersion` bump**. A *new superseding ADR* is required only when the
  **dimension set or aggregation method** changes — not for value tuning.
- New **"Ownership / RACI"** note: an unowned gold domain is a `DC-DQ-GAP-v1`
  finding the DQA raises and routes to the accountable owner; the agent's own
  mechanism closes the RACI gap, so full ownership is **not** an acceptance
  blocker.
- The `Consequences -> Status` bullet is updated to reflect acceptance.

### 4.2 Versioned config as source of truth

Create `data-platform/quality/trustscore-weights.json` (JSON, not YAML, to
preserve the module's stdlib-only, zero-new-dependency property — the
`quality-lane` CI installs only `pytest`, and the loader parses it with the
stdlib `json` module):

- `modelVersion: trustscore-v1`.
- `profiles:` the three decision-class weight vectors (`default` equal-weight;
  `crisis` up-weighting `timeliness`/`completeness`/`provenance`; `planning`
  up-weighting `completeness`/`consistency`/`ontology_mapping`) over the frozen
  eight-dimension `DIMENSIONS` order.
- `thresholds:` the per-decision-class overall score + gating-dimension minimums
  exactly as ADR-0053 §4.

The concrete numeric vectors are lifted verbatim from the ADR tables so the ADR
and config agree by construction at ratification time.

### 4.3 Deterministic loader

Add a small pure loader beside the model (e.g.
`data-platform/quality/weights_config.py`):

- `load_profile(decision_class) -> Dict[str, float]` — returns the weight vector
  for a class (falls back to `default`), covering every dimension in `DIMENSIONS`
  and summing > 0, so it plugs straight into `trust_score(..., weights=...)`.
- `load_thresholds(decision_class) -> {overall, gating}` — returned for the
  future gate slice; not yet wired into a runtime gate here.
- No I/O beyond reading the git-tracked JSON; no randomness, no clock — the
  loader is deterministic and unit-tested, mirroring the module's existing
  determinism guarantees.

`trust_score.py` itself is **unchanged** in signature; it already accepts
`weights`. This design only supplies a governed, versioned way to obtain them.

### 4.4 Backtest convergence (recorded as future work, not implemented here)

Trust scores are an input signal to the Sprint 30 evaluation-dataset curation.
The scheduled backtest compares the expert-set thresholds against observed
forecast/grounding impact and proposes revised values through the config-PR
path. No code or acceptance dependency here — it is the named follow-up that the
"Revision path" subsection points to.

### 4.5 Doc touch-up

The `## Data Quality Trust Score and Grounding Readiness` section added to
`docs/AI.md` and the DQA control table in `docs/COMPLIANCE.md` (PR #483) say
"ratification pending." Once ADR-0053 is `Accepted`, update those to "ratified
(ADR-0053, `trustscore-v1`)" with the appropriate SemVer PATCH/MINOR bump per
governance §9.

## 5. Notes on current state (verified)

- `trust_score.py` today does **not** hard-code the per-class profiles or the
  thresholds; it takes `weights` as a parameter and echoes `decision_class`. The
  concrete values referenced by ADR-0053 §3/§4 currently live **only in the ADR
  prose**. Extracting them into `trustscore-weights.json` therefore *creates* the
  single source of truth the ADR claims exists, rather than duplicating code.
- The grounding-readiness threshold **gate** (compare a domain's score/dimensions
  against `load_thresholds`, emit degraded-mode / withhold) is intentionally
  **out of scope** here and tracked as a separate slice.

## 6. Testing

- Unit tests for the loader: every profile covers all eight dimensions, sums
  > 0, `default` fallback for an unknown class, thresholds returned intact,
  and the loaded `default` profile equals the module's equal-weight default.
- A parity test asserting the config values match the ADR-0053 §3/§4 tables
  (guards against silent drift between doc and config).
- Existing 18 trust-score tests stay green (signature unchanged).
- Doc gates: mojibake + markdownlint on every edited doc; SemVer headers bumped.

## 7. Scope, guardrails, non-goals

- **In scope:** ADR-0053 edits (accept + ratification/revision/RACI subsections),
  `trustscore-weights.json`, deterministic loader + tests, AI/COMPLIANCE doc
  touch-up, traceability.
- **Guardrails:** read-only / advisory / HITL; no PHI; synthetic only; no infra
  apply; single-owner sign-off recorded in the ADR; every doc SemVer-bumped;
  gates green; a human merges.
- **Non-goals:** the grounding-readiness gate wiring; the backtest itself;
  runtime wiring of the trust-score/gap modules; any RACI board.

## 8. Requirement traceability

- `FR-DQA-003` (per-domain deterministic Trust Score) — weights/thresholds now
  ratified + versioned.
- `FR-DQA-006` / `FR-DQA-012` (degraded-mode / grounding-readiness) — thresholds
  ratified; gate wiring deferred to a separate slice.
- `NFR-DQA-001` (auditable) / `NFR-DQA-002` (read-only) — preserved; config
  changes are auditable PRs under single-owner sign-off.
- Governance §9 (doc versioning); ADR uses `Status` field (no SemVer header).
