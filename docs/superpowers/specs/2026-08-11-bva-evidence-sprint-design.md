---
Version: 1.1.0
Date: 2026-08-11
Author: Copilot coding agent (autopilot, delegated)
Status: Code-complete, deployed to SIT and PROD, live-verified
Previous Version: 1.0.0 (added §10 documenting both §8 follow-ups completed same-day)
---

# BVA Evidence Sprint — Master Data, PO Agent Competency, Backstage Card — Design

> Produced via the Superpowers `brainstorming` skill. The user delegated this
> work with: *"Please check the new `master-data\bva` we've and use superpower
> brainstorming to a) establish the master data in Fabric b) use the BVA Agent
> to consume and expose it in the curavias app via the Product Owner Agent as
> additional competency BVA of him c) review the BVA in the curavias backstage
> bva section and update it with the real value based on the master data. add
> as well the cost of the mvp we build as a card"*. Two rounds of clarifying
> questions were attempted via `vscode_askQuestions`; the user was unavailable
> both times and replied *"work autonomously and make good decisions."* This
> document is the audit trail the brainstorming skill calls for, written
> after the fact for asynchronous review rather than before implementation.

## 1. Context / problem statement

An uncommitted, incomplete CSV migration sat in the working tree: seven
existing `bva_*.csv` files staged as **deleted**, with ten new `dim_*.csv`/
`fact_*.csv` files added but never wired to any consumer, validator, or test.
A parallel uncommitted draft of `docs/BVA.md` (v2.0.0, "evidence-refined")
had replaced the committed v1.1.1 without preserving its branding header. No
Fabric artefact, PO Agent behaviour, or Backstage UI referenced any of this
new data. The user's three-part ask required turning this inert data drop
into (a) a validated, Fabric-bound master-data domain, (b) a live PO Agent
competency, and (c) a real UI card — while not lying about evidence strength
anywhere along the way (the repo's evidence-status vocabulary exists
specifically to prevent that).

## 2. Research findings (what already existed)

- **Fabric**: `sm_bva` semantic model already published live in the SIT
  workspace (`f3af9733-…`, item `1ab34928-…`), confirmed via a direct Fabric
  REST call. Lakehouse `lh_ihzhhpf_sit` is schema-enabled.
- **`data-platform/bva/costbasis.py`**: a *different*, already-productionised
  BVA data product (hospital-onboarding simulation baseline: BOM, effort,
  weekly Azure/Copilot cost, FX). The old `bva_*.csv` files the incomplete
  migration deleted are its inputs — deleting them would have silently
  broken the archetype simulation engine.
- **`po-agent-service`** (`data-platform/scripts/po-agent/`): a dedicated
  FastAPI Container App, already deployed to SIT, implementing the frozen
  `POST /answer` contract over four knowledge classes (A corpus, B
  live-proof, C cost, D ontology). Class C (`cost/reconcile_bva.py`) already
  reconciles a live Azure/Copilot run-rate against a ROM band parsed out of
  `docs/BVA.md`.
- **`bva_fanout.py`** (`runtime/bva_fanout.py`): a separate, already-tested
  "PO + BVA peer" answer composer (`compose_onboarding_answer`) that cites a
  PO verdict alongside BVA financial chunks. **Not wired into the live
  `/answer` endpoint** — no caller in `app.py` constructs the `bva_result`/
  `po_verdict` inputs it needs. This is a larger, separate integration
  surface than the current ask; see §8.
- **`data-platform/bva/simulate.py`**: the deterministic `bva.simulate`
  calc engine ADR-0056 describes (no-LLM-arithmetic ROI/TCO), already
  implemented, feeding `bva_fanout.py`'s tests via fixtures.
- **ADR-0056**: BVA Agent and PO Agent are peers under an App orchestrator;
  every figure must be a cited `GroundedChunk`; master data flows via git
  CSVs → CI gate → medallion → Direct Lake `sm_bva` → ontology.
- **`docs/BVA.md`'s live regex dependency**: `reconcile_bva.py` parses this
  file's prose directly at answer time (`bva_annual_run_cost`,
  `bva_rom_band`) — it is not just narrative documentation, it is a runtime
  data source for a deployed service. This was not obvious from the file's
  own content and caused a real regression (§4).

## 3. Scope decomposition and sequencing

Three sub-tasks, executed in dependency order rather than the user's listed
a/b/c order for one swap:

1. **(a) Master data** — restore the deleted `bva_*.csv` (additive, not a
   replacement — the new CSVs serve a *different* purpose, evidence/
   narrative grounding, not the cost-basis/archetype baseline), commit the
   ten new CSVs as a new domain, build `evidence_grounding.py` (pure
   transform, mirrors `costbasis.py`'s conventions), extend
   `validate_master_data.py`, write a Fabric notebook wrapper, merge
   `docs/BVA.md` drafts without losing the branding header.
2. **(c) Backstage card** — build on (a)'s data immediately (`bva-figures.ts`
   / `bva-evidence.ts` / `BvaDecisionSection.tsx`), since it has no
   dependency on (b) and is the most directly user-visible deliverable.
3. **(b) PO Agent competency** — done last because it required understanding
   `reconcile_bva.py`'s existing patterns in depth to extend consistently,
   and because implementing it surfaced the container-packaging bug (§4)
   that needed its own investigation before the work could be called done
   rather than merely "code that looks right."

Rationale for reordering: (c) is low-risk, high-visibility, and unblocks
user review of the *data* sooner. (b) touches a live service's request path
and deserved the most scrutiny — doing it last let the CSV shape and
validation rules stabilise first.

## 4. Problems discovered and fixed (not requested, but necessary)

### 4.1 `docs/BVA.md` regex regression (commit `cc2f48b7`)

Merging the uncommitted v2.0.0 draft lower-cased "Total Annual Run Cost" and
switched to comma-grouped numbers. `reconcile_bva.py`'s regexes required
exact case and comma-free digits. Found by *tracing every reader of the file
before finalising the merge* (the systematic-debugging skill's discipline),
confirmed by the file's own pre-existing test
(`test_cost_answer_is_a_range_within_bva_band_with_as_of`, which reads the
real repo file, not a fixture) failing before the fix and passing after.
Fixed with case-insensitive, comma-tolerant regexes. **Lesson recorded in
repo memory**: before editing `docs/BVA.md`, grep every consumer and run
its tests — a wording change can silently break a live parser.

### 4.2 `po-agent-service` container repo-root resolution (commit `49b90686`)

While wiring task (b), tracing `_class_c()`'s `repo_root =
_PO_AGENT_ROOT.parents[2]` against the actual container filesystem layout
(`runtime/Dockerfile` copies `corpus/liveproof/cost/ontology` flat into
`/app/`, never `docs/` or `data/`) showed this line evaluates to
`Path("/").parents[2]` inside the deployed image — an `IndexError`, caught
silently by the outer `except Exception: pass` in `get_tools()`. **This
means Class C (cost answers) has likely never actually initialised in the
deployed `po-agent-service`**, independent of anything in this sprint. Not
something the user asked to fix, but leaving it broken would have made task
(b)'s new code dead-on-arrival in production, and the whole point of task
(b) is that the evidence is *usable*, not merely unit-tested.

Fix: `_resolve_repo_root()` detects a container-shaped `/app/repo/` mirror
and falls back to the dev-tree formula otherwise (same "support both
layouts" pattern the file already uses for class-module sys.path wiring).
`runtime/Dockerfile`'s build context moved from
`data-platform/scripts/po-agent/` to the repo root so it can reach
`docs/BVA.md`, `data/master-data/bva/`, and `data-platform/bva/`; the repo's
existing allowlist-style root `.dockerignore` (already shared by three other
Dockerfiles) was extended rather than replaced.

**Verification limits**: no Docker engine is available in this dev
environment, so the actual `docker build` was validated only via the
`po-agent-runtime-build.yml` CI run triggered by pushing this change (not
via a local build). See §7 for the run to check before deploying.

## 5. Key decisions and rationale

| Decision | Alternatives considered | Why this one |
| -------- | ------------------------ | ------------- |
| New evidence CSVs are **additive**, old `bva_*.csv` restored | Treat the incomplete migration as intentional and finish deleting the old files | Old files are load-bearing for `costbasis.py`'s archetype simulation; deleting them breaks a different, unrelated feature. Confirmed by running its test suite before deciding. |
| `evidence_status` -> chunk `status`/`confidence` via an explicit mapping table | Pass the evidence_status string straight through as the chunk's `status` field | The `GroundedChunk` schema's `status` enum (`verified`/`partial`/`requires-validation`) is a *different, frozen* vocabulary from the CSV's `evidence_status` (`measured`/`estimated`/`mixed`/…). Conflating them would violate the schema and could silently produce an invalid contract. |
| Build-cost evidence is a **second chunk appended** to Class C, not a replacement of the live reconciliation | Replace `reconcile_bva()`'s single chunk | They answer different questions ("what does it cost to run" vs. "what did it cost to build"). Both are real and both should be citable independently. |
| Load `evidence_grounding.py` via `importlib.util.spec_from_file_location`, not sys.path + package import | Add `data-platform` to `sys.path` and `from bva.evidence_grounding import …` (mirrors `validate_master_data.py`) | The sys.path approach depends on `__file__`-relative parent-climbing, which is exactly the pattern that breaks inside the container. Loading by an explicit `repo_root`-derived path sidesteps package/sys.path assumptions entirely and works identically in both layouts. |
| Fix the container repo-root bug now, in this sprint | File a separate follow-up issue and ship task (b) as unreachable-in-prod code | Task (b)'s entire point is a working competency, not a passing unit test. The fix was small, local, reversible, and directly blocking the requested outcome. |
| Did **not** wire `bva_fanout.compose_onboarding_answer()` into the live endpoint | Complete the full PO+BVA peer fan-out this sprint | That mechanism needs a `po_verdict` producer that doesn't exist yet and a live `bva.simulate()` call site — a materially larger, separately-scoped integration. Flagged as the natural next step (§8), not silently dropped. |
| Design doc written retrospectively, after implementation | Block on user availability before writing any code | User's explicit instruction ("work autonomously and make good decisions") after two failed clarifying-question attempts. Documenting decisions after the fact, with rationale and alternatives, preserves the audit trail the brainstorming skill requires even though real-time approval wasn't possible. |

## 6. What changed (by commit)

1. `c2418a11` — restored 7 cost-basis CSVs; added 10 evidence CSVs + README;
   `data-platform/bva/evidence_grounding.py` (+7 tests); extended
   `validate_master_data.py` (+7 tests); Fabric notebook wrapper
   (`build_gold_bva_evidence.py`, not yet run against live Fabric); merged
   `docs/BVA.md` drafts.
2. `bb288be6` — Backstage MVP build-cost card: `bva-figures.ts` /
   `bva-evidence.ts` data, `BvaDecisionSection.tsx` new panel, en/de i18n,
   +1 test.
3. `cc2f48b7` — fixed the `docs/BVA.md` regex regression (§4.1).
4. `49b90686` — `build_cost_evidence_chunk()` in `reconcile_bva.py`, wired
   into `_class_c()`; fixed the container repo-root bug (§4.2);
   `runtime/Dockerfile` + `.dockerignore` + `po-agent-runtime-build.yml`
   updated to actually ship the required files into the image; +4 tests.

All four commits pushed to `main` directly (single-branch model per repo
convention). Test counts at each step are in the PR/commit trail; full
`po-agent` suite stands at 86 passed as of `49b90686`.

## 7. Verification status and what is still open

- [x] Unit/contract tests for all new code (86 po-agent tests, 71
      bva/master-data tests, 11 hcc-app-fluent BvaDecisionSection/i18n tests)
- [x] Mojibake/encoding lint clean on every touched file
- [x] `docs/BVA.md`'s live regex consumer test re-verified after the merge
- [x] **`po-agent-runtime-build` CI run for commit `49b90686`** — went green,
      confirming the new Docker build context actually builds.
- [x] Live Fabric execution of `build_gold_bva_evidence.py` against the SIT
      lakehouse — done same day; see §10.1.
- [x] SIT/PROD redeploy of `hcc-app-fluent` (task c's UI) and
      `po-agent-service` (task b's competency) — done same day.

## 8. Follow-up recommendations (not done, flagged for a future sprint)

1. **Wire `bva_fanout.compose_onboarding_answer()` into the live `/answer`
   endpoint.** This is the deeper "BVA Agent as PO Agent peer competency"
   integration ADR-0056 describes, distinct from and larger than this
   sprint's Class-C chunk addition. Needs: a live call site for
   `bva.simulate()`, a `po_verdict` producer, and intent-routing wiring in
   `app.py` (the `classify_intent`/`_ROUTE_PATTERNS` machinery already
   exists in `bva_fanout.py` and is fully tested — it is genuinely just
   unconnected, not unfinished).
2. **Confirm Class A/B production wiring** (flagged in the Sprint 41 design
   doc as unconfirmed, still true here) — worth re-auditing once Class C's
   container-packaging bug class is fixed, in case the same
   `__file__`-relative-parents pattern recurs elsewhere.
3. **Run the Fabric notebook** (`build_gold_bva_evidence.py`) against the
   live SIT lakehouse and confirm the `sm_bva` semantic model picks up the
   new evidence gold tables via Direct Lake, closing the loop ADR-0056
   describes (git CSV -> medallion -> Direct Lake -> ontology).
4. **Add a CI guard** analogous to the mojibake/conflict-marker pre-commit
   gate that runs `reconcile_bva`'s tests whenever `docs/BVA.md` changes,
   so a future wording edit cannot silently regress the live parser again
   without a local test run catching it first (today it only catches it if
   someone happens to run the po-agent suite before pushing).

## 9. Assumptions made without interactive confirmation

- That "establish master data in Fabric" for this sprint means committing
  validated, Fabric-ready CSVs plus a notebook wrapper — not necessarily
  executing that notebook against live Fabric in this same session (the
  live semantic model already exists; the notebook run is a follow-up).
- That "expose it via PO Agent as additional competency" means extending
  the existing, already-live Class C tool (lowest-risk, already-wired path)
  rather than completing the larger, unwired `bva_fanout` peer-agent
  mechanism (§8 item 1).
- That fixing the container repo-root bug was in-scope, since without it
  task (b)'s deliverable would not actually function once deployed.
- That the combined SIT/PROD redeploy should wait until this document is
  reviewed, rather than deploying task (b)'s code immediately after commit.

## 10. Follow-up completion (same day, user said "can we follow up on this part to finish it as well")

Both §8 items were completed later the same day, after the user reviewed the
sprint summary and asked to finish the deferred work. User was unavailable
for a second scoping question (about how far to take the `bva_fanout` wiring
given the newly-discovered Cosmos/verdict-producer gap); proceeded
autonomously per the same delegation.

### 10.1 Fabric notebook run + Direct Lake extension (§8 item 3) -- done

- Uploaded all 17 `data/master-data/bva/*.csv` (7 cost-basis + 10 evidence --
  neither had ever been uploaded to OneLake before this) via the existing
  `upload_to_onelake.py`.
- New `data-platform/scripts/fabric/publish_bva_evidence_notebook.py`
  published `build_gold_bva_evidence` as a live Fabric notebook, mirroring
  the already-live `build_gold_bva_costbasis` notebook's exact
  "notebook-content.py" shape (fetched and decoded live via `getDefinition`
  to confirm the template precisely, rather than guessing).
- Ran it live (SIT): completed in ~6 minutes. Verified via a direct SQL
  analytics-endpoint query (pyodbc + AAD token): all 10 tables populated,
  BC-999 spot-check exact (amount_chf=21286.0, evidence_status=mixed).
- New `generate_bva_evidence_tmdl.py` + `publish_sm_bva.py` extended
  `sm_bva.SemanticModel` with the 10 new `bva_evidence_*` Direct Lake table
  definitions (mirroring `bva_hospital_profile_dim.tmdl`'s shape) and
  published the updated definition (confirmed the exact part-path shape via
  a live `getDefinition` fetch first, rather than guessing).
- Verified via a live DAX query (Power BI REST `executeQueries`):
  `bva_evidence_build_cost_actual_fact` returns rows=5, total=21286.0 --
  Direct Lake pickup confirmed, closing the ADR-0056 loop (git CSV ->
  notebook -> Direct Lake) for this data product.
- 12 new tests for the three new scripts' pure/offline logic. Commit
  `52f2ebc1`.
- Not done: PROD notebook run / semantic model publish (SIT-only; PROD's
  `sm_bva` mirror can be republished the same way once reviewed).

### 10.2 `bva_fanout` wiring (§8 item 1) -- done, deliberately narrower than "complete"

Re-confirmed the finding from §5's decision table with a full trace of
`docs/data-platform/bva-po-fanout.md`: "Verdict is an input, never invented"
is an explicit design invariant, not an oversight. `po-agent-service` has
zero Cosmos DB wiring (no env vars, no RBAC, not in the Bicep module) --
building a real Cosmos-backed verdict lookup would mean new infra (Managed
Identity role assignment + Bicep + redeploy), and an LLM-based verdict
producer was ruled out as separately-scoped, safety-sensitive work this
session did not have room to do justice to. Asked the user how far to take
it (full build / financial-only / re-document only); user unavailable,
proceeded with the safe, no-new-infra middle path:

- `AnswerRequest` gains two **optional**, additive fields: `hospitalDelta`
  (the `bva.simulate` what-if inputs) and `poVerdict` (caller-supplied,
  never computed here). Existing callers are completely unaffected.
- `financial`/`strategic` questions with a `hospitalDelta` -> live
  `bva.simulate()` numbers cited through the standard grounded-answer
  contract (citation gate, threshold, DE/EN, audit).
- `onboarding` questions -> `bva_fanout.compose_onboarding_answer()`,
  verdict-first; no `poVerdict` supplied degrades to an honest transparent
  partial (never fabricates); a supplied `poVerdict` composes correctly.
- Invalid delta inputs degrade to a refusal, never a 500.
- Fixed a latent bug found while adding these Pydantic models: `app.py`
  only imported `Any` from `typing`; `Optional` was missing, which broke
  Pydantic v2's model rebuild under `from __future__ import annotations`.
- 5 new tests; full po-agent suite 91 passed (was 86). Commit `bed0da51`.
- Live-verified in **both SIT and PROD** (financial-only and
  onboarding+verdict paths both confirmed via direct HTTP smoke tests
  against the deployed services).
- Still not done, and now the accurate remaining scope for a genuinely
  "complete" fan-out: Cosmos-backed `Opportunity` write-back/lookup (new
  infra) and/or an LLM-based verdict producer (needs its own careful,
  separately-reviewed prompt-injection-safe design) -- both explicitly
  flagged, not silently dropped.

### 10.3 Deployment record

Both follow-ups deployed to SIT (`cd-infra-deploy-sit` runs, images
`52f2ebc1`-era and `bed0da5`) and PROD (`cd-infra-deploy-prod` run,
image `bed0da5` -- `po-agent-service`'s first-ever PROD image bump since
its `49b9068` rollout earlier the same day). All deploys used the same
what-if-first, `approved-to-apply`-gated discipline used throughout this
sprint.
