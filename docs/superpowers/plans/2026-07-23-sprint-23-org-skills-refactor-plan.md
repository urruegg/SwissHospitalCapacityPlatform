# Sprint 23 Org-Skills Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the Sprint 23 refactor (design D1-D6 / WS-A..D) as small, human-reviewed PRs: a dedicated ADLS landing zone + on-demand pipeline, a Sprint-21-style skills-evidence plugin package (all sources simulated), a hybrid batch/Eventstream transport, and a bed-vs-ops skill-demand split across the semantic model, ontology and Fabric IQ grounding.

**Architecture:** Mirror two proven repo patterns exactly — the Sprint 21 signal-provider plugin (`data-platform/scripts/external-signals/`: `connectors/base_connector.py` + per-source adapters + `normalize.py` + `*_synth.py` + `tests/`) for skills-evidence, and the Sprint 22 medallion (`upload_to_onelake.py` + `verify_gold_schema.py` + `validate_master_data.py`) for landing/validation/gold. Extend, do not replace: the atomic unit stays `fact_skill_assertion`; Gold stays deny-by-default; badge (`source_mode`/`trust_tier`) travels end-to-end.

**Tech Stack:** Python 3 stdlib (dependency-free connectors, simulators, validators — `pytest` for tests), Bicep (ADLS Gen2 + OneLake shortcut + Container Apps jobs + Eventstream), Fabric notebooks (PySpark bronze/silver/gold), TMDL semantic model, Markdown ontology + ADR + PRD.

---

## Hard constraints (apply to every task)

- **Runtime `python`, not `python3`.** All commands and shebang-independent invocations use `python`.
- **Commit with hooks disabled:** `git -c core.hooksPath=/dev/null commit -m "..."`.
- **Ingestion/simulation run as Azure Container Apps -> Event Hub/Eventstream. Never GitHub workflows.** No simulator is wired into `.github/workflows/`.
- **Synthetic / no-PHI only** (ADR-0013 / ADR-0016). Fixtures and seeds carry only fabricated Curavias workforce data.
- **Human always reviews + merges every PR. Never self-merge.** One small PR per slice, each linked to **#255** and stacked on the design PR **#309** (which must merge first).
- **Trunk-based per ADR-0038:** short-lived branch off `main` per PR; branch names `sprint-23/<ws>-<slice>`.
- **Deploy/delete gated by `approved-to-apply`** on the PR/issue thread before any `az deployment` apply.
- **Doc edits** follow §9 Document Versioning + the `document-authoring` skill; mechanical mojibake/lint gates are enforced by CI.

## Dependency order between work streams

```
PR #309 (design) ── merged ──┐
                             ▼
WS-B0 (relocate generator)   WS-A1..A4 (infra, independent)   WS-D1..D4 (governance, alongside)
        │                             │
        ▼                             │
WS-B1..B4 (plugin + medallion) ◄──────┘ (needs landing zone for B4 end-to-end)
        │
        ▼
WS-C1..C4 (semantic / ontology / Fabric IQ / CI rebaseline) ◄── needs gold tables from WS-B
```

WS-A and WS-D can start in parallel with WS-B0/B1 the moment #309 merges. WS-C is strictly downstream of WS-B gold output. Every PR below is independently reviewable and mergeable.

---

## File Structure

**WS-A — Infra (Bicep, UC-style outputs under `infra/`)**
- Create: `infra/modules/data-foundation/masterdata-landing/main.bicep` — ADLS Gen2 account/container `landing/curavias-org-skills/` + role assignments.
- Create: `infra/modules/data-foundation/masterdata-landing/onelake-shortcut.md` — OneLake shortcut creation runbook (portal/REST; shortcuts are not Bicep-provisionable).
- Create: `infra/modules/experience-hosting/skills-sim-jobs/main.bicep` — Container Apps **Jobs** (manual trigger) for the four simulators.
- Create: `infra/modules/integration-orchestration/skills-eventstream/main.bicep` — Eventstream lane for near-real-time skills events (reuse Sprint 21 real-time rail shape).
- Modify: `infra/main.bicep` — wire the three new modules; `infra/environments/sit.bicepparam` + `prod.bicepparam` — parameters.
- Create: `docs/runbooks/curavias-org-skills-upload.md` — `az`/portal upload + on-demand pipeline-run runbook.

**WS-B — Data (plugin + medallion), mirrors `external-signals/` + Sprint 22**
- Move: `docs/superpowers/ideas/unified-curavias-organisation-and-skills-ontology/**` generator + 20 CSVs -> `data/master-data/curavias-org-skills/` (+ `README.md` with provenance).
- Create: `data-platform/scripts/skills-evidence/connectors/base_connector.py` — abstract adapter (`mode`, `fetch`, `parse`/`to_canonical`).
- Create: `data-platform/scripts/skills-evidence/connectors/{successfactors,lms,skills_manager,work_id}.py` — four adapters (simulated now, real-API-ready).
- Create: `data-platform/scripts/skills-evidence/normalize.py` — payload -> `DC-SKILL-EVIDENCE-v1` envelope (mirrors `external-signals/normalize.py`).
- Create: `data-platform/scripts/skills-evidence/dedup.py` — canonical de-dup of evidence records.
- Create: `data-platform/scripts/skills-evidence/skills_evidence_synth.py` — dependency-free seeder over committed fixtures (all four sources).
- Create: `data-platform/scripts/skills-evidence/tests/{__init__.py,_util.py,test_connectors.py,test_normalize.py,test_dedup.py,test_schema_conformance.py,fixtures/*.json}`.
- Create: `data/synthetic/schema/dc-skill-evidence-v1.schema.json` — the contract JSON schema (mirrors `dc-ext-signal-v1.schema.json`).
- Create: `data-platform/notebooks/skills-evidence/{ingest_bronze_skills.py,build_silver_skills.py,build_gold_skills.py}` — medallion.
- Modify: `data/master-data/validate_master_data.py` (or a lane-local `validate_org_skills.py`) — add GLN mod-10, enum-domain, load-order checks; reused inside the silver gate.

**WS-C — Semantic / Ontology / Fabric IQ**
- Modify: `data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/*.tmdl` — remove `dim_hospital`; add `dim_tenant`/`dim_org_unit`/`dim_department`, `care_setting`, skills tables + measures + live-vs-simulated measure.
- Create: `_hospital_to_org_crosswalk.csv` under `data/master-data/curavias-org-skills/` — legacy `hospital_id` -> `tenant_id`/`org_unit_id`.
- Modify: `docs/ontology/*.md` + `crosswalk.md` + conformance gate — org/skills + care-setting concepts.
- Modify: Fabric IQ `ont_hospital_capacity` + Data Agent grounding.
- Modify: `.github/workflows/verify-semantic-model.yml` — re-baseline exact counts; `data-platform/scripts/verify_gold_schema.py` — extend parity for new gold tables.

**WS-D — Governance**
- Create: `docs/adr/00NN-curavias-landing-zone-and-skills-evidence-plugins.md` — Accepted before WS-B merges.
- Modify: `docs/PRD.md` — FR/NFR rows (landing zone, plugin sources, bed-vs-ops) + §7 traceability matrix.
- Modify: `docs/COMPLIANCE.md` / `docs/SECURITY.md` — DSG tagging of `fact_skill_assertion` + `dim_work_id_profile`; Work-ID consent lineage.
- Modify: `AGENTS.md` / `.github/copilot/mcp.json` — **only if** a new MCP server is introduced (design says none; expect no change).

---

## WS-A — Infra landing zone + simulator jobs + Eventstream

> One PR per slice. WS-A is independent of the design merge only for authoring; `what-if`/apply is gated by `approved-to-apply`. No apply happens in a PR merge.

### Task A1: ADLS Gen2 landing-zone module (PR `sprint-23/ws-a-landing-zone`)

**Files:**
- Create: `infra/modules/data-foundation/masterdata-landing/main.bicep`
- Modify: `infra/main.bicep`, `infra/environments/sit.bicepparam`, `infra/environments/prod.bicepparam`

- [ ] **Step 1: Write the Bicep module** — ADLS Gen2 storage (`isHnsEnabled: true`), a `landing` filesystem, and the folder convention `landing/curavias-org-skills/<source>/<yyyy-mm-dd>/`. Name per §8: `st<...>masterdata` with env suffix (`-sit` / `-prod`). Tag `env`/`owner`/`costCenter`/`workload`. Add a `Storage Blob Data Contributor` role assignment for the pipeline's managed identity (parameterised principalId). Enable diagnostic settings -> Log Analytics for prod.
- [ ] **Step 2: Wire into `infra/main.bicep`** — module reference with env params; no hard-coded names/IDs.
- [ ] **Step 3: Build** — Run: `az bicep build --file infra/main.bicep` — Expected: builds clean, no warnings on the new module.
- [ ] **Step 4: `what-if` (SIT)** — Run: `az deployment group what-if -g <rg-sit> -f infra/main.bicep -p infra/environments/sit.bicepparam` — Expected: shows the new storage + container + role assignment as `Create`, nothing destructive. **Paste the summary into the PR; do not apply.**
- [ ] **Step 5: Commit** — `git -c core.hooksPath=/dev/null commit -am "feat(infra): add ADLS Gen2 landing zone for curavias org/skills master data (#255)"`

**Acceptance gate:** `az bicep build` clean; `what-if` shows only additive changes; PR contains the `what-if` summary + tag list; no secrets/IDs hard-coded. Human reviews + merges.

### Task A2: OneLake shortcut runbook (PR `sprint-23/ws-a-onelake-shortcut`)

**Files:** Create `infra/modules/data-foundation/masterdata-landing/onelake-shortcut.md`, `docs/runbooks/curavias-org-skills-upload.md`

- [ ] **Step 1** — Document the OneLake shortcut from the Fabric lakehouse `Files/landing/curavias-org-skills/` to the ADLS `landing` container (portal steps + Fabric REST `POST .../shortcuts` body with placeholders, no real IDs). Shortcuts are not Bicep-provisionable — state this explicitly.
- [ ] **Step 2** — Write the upload runbook: `az storage fs directory upload` per `<source>/<yyyy-mm-dd>/` folder + the on-demand pipeline run (parameterised `--workspace-id`/`--lakehouse-id`/`--source-root`, consistent with `upload_to_onelake.py`).
- [ ] **Step 3: Doc gates** — Run: `npx --yes markdownlint-cli2 "docs/runbooks/**/*.md" "infra/modules/**/*.md"` — Expected: pass. Version header per §9.
- [ ] **Step 4: Commit** — `git -c core.hooksPath=/dev/null commit -am "docs(infra): OneLake shortcut + landing-zone upload runbook (#255)"`

**Acceptance gate:** markdownlint + link-check green; runbook parameterised (no real IDs); §9 version header present. Human reviews + merges.

### Task A3: Container Apps simulator Jobs module (PR `sprint-23/ws-a-sim-jobs`)

**Files:** Create `infra/modules/experience-hosting/skills-sim-jobs/main.bicep`; modify `infra/main.bicep` + params.

- [ ] **Step 1** — Define four Container Apps **Jobs** (`triggerType: Manual`) — one per source (`successfactors`/`lms`/`skills-manager`/`work-id`) — that run the WS-B `skills_evidence_synth.py` seeder and write extract files to the ADLS landing zone via managed identity. Image param + `--source`/`--output` args. **No GitHub workflow triggers them** — manual/on-demand only.
- [ ] **Step 2: Build** — Run: `az bicep build --file infra/main.bicep` — Expected: clean.
- [ ] **Step 3: `what-if` (SIT)** — additive only; paste summary; do not apply.
- [ ] **Step 4: Commit** — `git -c core.hooksPath=/dev/null commit -am "feat(infra): Container Apps jobs for skills-evidence simulators (#255)"`

**Acceptance gate:** builds; `what-if` additive; jobs are manual-trigger (verified in the module); constraint "never GitHub workflows" honoured. Human reviews + merges.

### Task A4: Eventstream lane module (PR `sprint-23/ws-a-eventstream`)

**Files:** Create `infra/modules/integration-orchestration/skills-eventstream/main.bicep`; modify `infra/main.bicep` + params. Reference `infra/deploy-eventstream.bicep` as the shape template.

- [ ] **Step 1** — Define an Eventstream (or Event Hub source feeding the existing rail) carrying only the three near-real-time events: `credential-expiry`, `consent-grant/revoke`, `newly-confirmed-assertion`. Narrow by design (D4).
- [ ] **Step 2: Build** — `az bicep build --file infra/main.bicep` — Expected: clean.
- [ ] **Step 3: `what-if` (SIT)** — additive; paste; do not apply.
- [ ] **Step 4: Commit** — `git -c core.hooksPath=/dev/null commit -am "feat(infra): Eventstream lane for near-real-time skills events (#255)"`

**Acceptance gate:** builds; `what-if` additive; event set limited to the three D4 events. Human reviews + merges.

---

## WS-B — Data: generator relocation + skills-evidence plugin + medallion

### Task B0: Relocate generator + 20 CSVs (PR `sprint-23/ws-b-relocate-generator`)

**Files:** Move idea-pack generator + CSVs -> `data/master-data/curavias-org-skills/`; Create `data/master-data/curavias-org-skills/README.md`.

- [ ] **Step 1** — `git mv` the Step-4 generator (`generate_master_data.py`) + the 20 CSVs from the idea pack into `data/master-data/curavias-org-skills/`. Preserve history. **Fix the path mismatch called out in the sprint doc DoD.**
- [ ] **Step 2** — Add `README.md`: provenance (idea pack Steps 1-4), regeneration command `python generate_master_data.py`, and the synthetic/no-PHI note.
- [ ] **Step 3: Regenerate + diff** — Run: `cd data/master-data/curavias-org-skills; python generate_master_data.py` — Expected: regenerates the 20 CSVs byte-identical to the committed copies (`git diff --stat` empty), proving reproducibility.
- [ ] **Step 4: Commit** — `git -c core.hooksPath=/dev/null commit -am "refactor(data): relocate curavias org/skills generator + CSVs to data/master-data (#255)"`

**Acceptance gate:** generator runs with `python`, output reproducible (clean diff); README provenance present; git history preserved. Human reviews + merges.

### Task B1: Contract schema + normalize (PR `sprint-23/ws-b-contract`)

**Files:**
- Create: `data/synthetic/schema/dc-skill-evidence-v1.schema.json`
- Create: `data-platform/scripts/skills-evidence/normalize.py`
- Create: `data-platform/scripts/skills-evidence/tests/{__init__.py,_util.py,test_normalize.py}`

- [ ] **Step 1: Write the failing test** — `tests/test_normalize.py`:

```python
from normalize import build_record, envelope, CONTRACT_ID

def test_build_record_carries_badge_and_provenance():
    rec = build_record(
        evidence_id="ev-1", external_system="lms", source_mode="simulated",
        trust_tier="A", external_person_ref="p-1", external_skill_code="BLS",
        external_skill_label="Basic Life Support", self_or_confirmed="employer_confirmed",
        captured_at="2026-07-01", connector_version="lms-1.0.0",
        licence="synthetic", raw={"x": 1}, worker_gln=None, external_level="proficient",
        consent_scope=None,
    )
    assert rec["sourceMode"] == "simulated"      # live-vs-simulated badge
    assert rec["trustTier"] == "A"
    assert rec["selfOrConfirmed"] == "employer_confirmed"
    assert rec["provenance"]["connectorVersion"] == "lms-1.0.0"
    assert "rawHash" in rec["provenance"]

def test_envelope_sets_contract_id():
    env = envelope([], dataset_id="d1")
    assert env["contractId"] == CONTRACT_ID
    assert env["contractVersion"] == "1.0.0"
```

- [ ] **Step 2: Run test to verify it fails** — Run: `cd data-platform/scripts/skills-evidence; set PYTHONPATH=. && python -m pytest tests/test_normalize.py -v` — Expected: FAIL (`ModuleNotFoundError: normalize`).
- [ ] **Step 3: Write `normalize.py`** — mirror `external-signals/normalize.py`: `CONTRACT_ID = "DC-SKILL-EVIDENCE-v1"`, `CONTRACT_VERSION = "1.0.0"`, `raw_hash`, `dedup_key`, `build_record(...)` returning the `DC-SKILL-EVIDENCE-v1` fields (camelCase keys: `evidenceId`, `externalSystem`, `sourceMode`, `trustTier`, `externalPersonRef`, `workerGln`, `externalSkillCode`, `externalSkillLabel`, `selfOrConfirmed`, `externalLevel`, `consentScope`, `capturedAt`, `provenance`), and `envelope(records, dataset_id, residency="CH")` with `classification: "personal-synthetic"`, `purposeTags: ["skills-evidence", "workforce-capability"]`.
- [ ] **Step 4: Write the schema** — `dc-skill-evidence-v1.schema.json` with envelope `required` + `records.items.required` matching the record keys above (mirror `dc-ext-signal-v1.schema.json` shape).
- [ ] **Step 5: Run test to verify it passes** — same pytest command — Expected: PASS (2 passed).
- [ ] **Step 6: Commit** — `git -c core.hooksPath=/dev/null commit -am "feat(skills-evidence): DC-SKILL-EVIDENCE-v1 contract + normalize (#255)"`

**Acceptance gate:** tests green with `python -m pytest`; schema `required` matches `build_record` output keys; badge (`sourceMode`/`trustTier`) present in every record. Human reviews + merges.

### Task B2: Base connector + four adapters (PR `sprint-23/ws-b-connectors`)

**Files:**
- Create: `data-platform/scripts/skills-evidence/connectors/{__init__.py,base_connector.py,successfactors.py,lms.py,skills_manager.py,work_id.py}`
- Create: `tests/test_connectors.py` + `tests/fixtures/{successfactors,lms,skills_manager,work_id}.json`

- [ ] **Step 1: Write the failing test** — `tests/test_connectors.py`:

```python
import json
from pathlib import Path
from connectors.successfactors import SuccessFactorsConnector
from connectors.lms import LmsConnector
from connectors.skills_manager import SkillsManagerConnector
from connectors.work_id import WorkIdConnector

FIX = Path(__file__).parent / "fixtures"

CASES = [
    (SuccessFactorsConnector(), "successfactors.json", "successfactors"),
    (LmsConnector(), "lms.json", "lms"),
    (SkillsManagerConnector(), "skills_manager.json", "skills_manager"),
    (WorkIdConnector(), "work_id.json", "work_id"),
]

def test_each_connector_emits_simulated_badge():
    for conn, fixture, system in CASES:
        recs = conn.parse(json.loads((FIX / fixture).read_text()))
        assert recs, f"{system} produced no records"
        for r in recs:
            assert r["externalSystem"] == system
            assert r["sourceMode"] == "simulated"      # all four simulated now
            assert r["selfOrConfirmed"] in ("self", "employer_confirmed")

def test_work_id_gln_only_on_consent():
    recs = WorkIdConnector().parse(json.loads((FIX / "work_id.json").read_text()))
    for r in recs:
        if r["consentScope"] is None:
            assert r["workerGln"] is None    # GLN promotion key only on consent
```

- [ ] **Step 2: Run test to verify it fails** — Run: `cd data-platform/scripts/skills-evidence; set PYTHONPATH=. && python -m pytest tests/test_connectors.py -v` — Expected: FAIL (import errors).
- [ ] **Step 3: Write `base_connector.py`** — mirror `external-signals/connectors/base_connector.py`: ABC with `source_id`, `source_authority`, `licence`, `version`, `source_mode = "simulated"`, abstract `parse(payload) -> list[dict]`, and an optional `fetch(url)` guarded by a lazy `requests` import (real-API-ready).
- [ ] **Step 4: Write the four adapters** — each subclasses `BaseConnector`, calls `normalize.build_record` per row. SuccessFactors -> `employer_confirmed` HRIS records (L1); LMS -> course/cert completions (L1); SkillsManager -> company inventory (Step-3 modes A/B/C); WorkId -> worker passport, `self` by default, `workerGln`/`consentScope` only when the fixture row grants consent. Each sets `source_mode="simulated"`.
- [ ] **Step 5: Write the four fixtures** — minimal synthetic payloads (2-3 rows each), fabricated person refs, no PHI.
- [ ] **Step 6: Run test to verify it passes** — same pytest command — Expected: PASS.
- [ ] **Step 7: Commit** — `git -c core.hooksPath=/dev/null commit -am "feat(skills-evidence): base connector + successfactors/lms/skills-manager/work-id adapters (#255)"`

**Acceptance gate:** all four adapters green; every record carries `sourceMode=simulated`; Work-ID GLN gated by consent; adapters share the `base_connector` surface (real-API drop-in preserved). Human reviews + merges.

### Task B3: Dedup + synth seeder + schema conformance (PR `sprint-23/ws-b-synth`)

**Files:**
- Create: `dedup.py`, `skills_evidence_synth.py`
- Create: `tests/{test_dedup.py,test_schema_conformance.py}`

- [ ] **Step 1: Write the failing tests** — `test_dedup.py` (two records same `externalSystem`+`externalPersonRef`+`externalSkillCode` collapse to one, keeping the higher `selfOrConfirmed`), and `test_schema_conformance.py` (build the full envelope from all four fixtures, assert `skills_evidence_synth.validate(doc)` returns `[]` and record count == sum of fixture rows).
- [ ] **Step 2: Run tests to verify they fail** — Run: `... python -m pytest tests/test_dedup.py tests/test_schema_conformance.py -v` — Expected: FAIL (modules missing).
- [ ] **Step 3: Write `dedup.py`** — mirror `external-signals/dedup.py`: group by canonical key `(externalSystem, externalPersonRef, externalSkillCode)`; `employer_confirmed` beats `self`.
- [ ] **Step 4: Write `skills_evidence_synth.py`** — mirror `signals_synth.py`: `_CONNECTORS` list over the four fixtures, `build_records()`, `build_envelope()`, dependency-free `validate(doc)` against `dc-skill-evidence-v1.schema.json`, and a `main()` with `--dataset-id`/`--output`/`--dry-run`. Docstring: synthetic-only, run via Container Apps job, `PYTHONPATH=. python skills_evidence_synth.py --dry-run`.
- [ ] **Step 5: Run tests to verify they pass** — Expected: PASS.
- [ ] **Step 6: Dry-run the seeder** — Run: `... python skills_evidence_synth.py --dry-run` — Expected: `OK: N DC-SKILL-EVIDENCE-v1 records validated against schema.`
- [ ] **Step 7: Commit** — `git -c core.hooksPath=/dev/null commit -am "feat(skills-evidence): dedup + synthetic seeder + schema conformance (#255)"`

**Acceptance gate:** dedup + conformance tests green; `--dry-run` validates clean; seeder dependency-free (stdlib only). Human reviews + merges.

### Task B4: Silver validation gate + medallion notebooks (PR `sprint-23/ws-b-medallion`)

**Files:**
- Modify/Create: `data/master-data/validate_master_data.py` (extend) **or** `data/master-data/curavias-org-skills/validate_org_skills.py` (new lane-local validator)
- Create: `data-platform/notebooks/skills-evidence/{ingest_bronze_skills.py,build_silver_skills.py,build_gold_skills.py}`
- Modify: `data-platform/scripts/verify_gold_schema.py` (extend contract), add `tests/test_validate_org_skills.py`

- [ ] **Step 1: Write the failing validator test** — assert GLN mod-10 rejects a bad check digit, enum-domain check rejects an out-of-domain `care_setting`, FK check rejects a dangling `org_unit_id`, and load-order is enforced (parents before children). (Note: `data/master-data/validate_master_data.py` already exists with PK/FK logic — resolves design open item §6 #3; extend it, don't re-author.)
- [ ] **Step 2: Run test to verify it fails** — Run: `python -m pytest data/master-data/tests/test_validate_org_skills.py -v` — Expected: FAIL.
- [ ] **Step 3: Implement the validator additions** — GLN mod-10 (13-digit, weighted 1/3), enum domains (incl. `care_setting in {bed, ops}`, `source_mode in {live, simulated}`, assurance `L0..L4`), cross-CSV FK for the org/skills tables, deterministic load order. Reuse the existing PK/FK helpers.
- [ ] **Step 4: Run test to verify it passes** — Expected: PASS; then run against the real relocated CSVs: `python data/master-data/validate_master_data.py` -> `OK`.
- [ ] **Step 5: Write the three notebooks** — `ingest_bronze_skills.py` (raw typed copy of landed `Files/landing/curavias-org-skills/**` + the `DC-SKILL-EVIDENCE-v1` envelope; preserve `sourceMode`/`trustTier`); `build_silver_skills.py` (type-cast, run the validator logic, dedupe, ESCO crosswalk, assurance L0-L4, **quarantine bad rows** to `silver.*_quarantine`); `build_gold_skills.py` (deny-by-default: assurance >= L2 valid, L4 where legally required; emit the 19 `gold.*` org/skills tables; badge surfaces on `gold.fact_skill_assertion`).
- [ ] **Step 6: Extend `verify_gold_schema.py`** — add the new org/skills gold tables to the contract set (they'll be picked up from the TMDL by WS-C; until then, add an explicit produced-list fixture test asserting the 19 names appear).
- [ ] **Step 7: Commit** — `git -c core.hooksPath=/dev/null commit -am "feat(skills-evidence): silver validation gate + bronze/silver/gold medallion notebooks (#255)"`

**Acceptance gate:** validator tests green + real CSVs valid; notebooks reviewed for deny-by-default + quarantine + badge preservation; `verify_gold_schema.py` lists the 19 gold tables. (End-to-end pipeline run needs WS-A landing zone + `approved-to-apply`; capture the run evidence in a follow-up comment, not the PR merge.) Human reviews + merges.

---

## WS-C — Semantic model / ontology / Fabric IQ / CI rebaseline (needs WS-B gold)

### Task C1: Replace `dim_hospital` + org spine + crosswalk (PR `sprint-23/ws-c-org-spine`)

**Files:** Modify TMDL tables; Create `data/master-data/curavias-org-skills/_hospital_to_org_crosswalk.csv`; re-key fact tables/generators.

- [ ] **Step 1** — Author `_hospital_to_org_crosswalk.csv` (legacy `hospital_id` -> `tenant_id`/`org_unit_id`; CuraNova/Curalp/Vialta). Deterministic, reviewable.
- [ ] **Step 2** — Remove `dim_hospital.tmdl`; add `dim_tenant`/`dim_org_unit`/`dim_department` TMDL; re-key `fact_capacity_baseline`, `encounter`, `bed_assignment`, `or_case`, `or_schedule`. **Keep `bva_dim_hospital` untouched** (separate domain, D3).
- [ ] **Step 3: Validate** — export TMDL + run the model validation locally; confirm relationships resolve, no `dim_hospital` references remain (grep the TMDL tree).
- [ ] **Step 4: Commit** — `git -c core.hooksPath=/dev/null commit -am "refactor(model): replace dim_hospital with tenant/org-unit/department spine + crosswalk (#255)"`

**Acceptance gate:** no `dim_hospital` outside `bva_*`; facts re-keyed; crosswalk deterministic; model validates. Human reviews + merges.

### Task C2: Skills + live-vs-simulated + bed-vs-ops measures (PR `sprint-23/ws-c-measures`)

**Files:** Modify TMDL — add skills tables (`fact_skill_assertion`, `fact_skill_demand`, `bridge_role_skill_demand_template`, `dim_work_id_profile`, `dim_care_setting`, ...) + measures.

- [ ] **Step 1** — Add the skills gold tables to the model (Direct Lake) and the measures: supply / demand / gap / eligibility (per T6), a **live-vs-simulated** measure driven by `sourceMode`, and a `care_setting` (`bed`=Pflegepersonal/nursing | `ops`=Doctors+specialised) dimension so demand/gap report per care setting (T14 / requirement #4).
- [ ] **Step 2: Validate** — model validates; measures compile; care-setting slices resolve.
- [ ] **Step 3: Commit** — `git -c core.hooksPath=/dev/null commit -am "feat(model): skills supply/demand/gap + live-vs-simulated + bed-vs-ops care_setting measures (#255)"`

**Acceptance gate:** measures compile; care-setting split reports nursing vs ops gaps separately; badge measure reads `sourceMode` (never invented). Human reviews + merges.

### Task C3: CI count rebaseline + gold parity (PR `sprint-23/ws-c-ci-rebaseline`)

**Files:** Modify `.github/workflows/verify-semantic-model.yml`; `data-platform/scripts/verify_gold_schema.py`.

- [ ] **Step 1** — Re-baseline the exact table/measure/relationship counts in `verify-semantic-model.yml` in the **same PR** as the model expansion (Sprint 22 pattern) — bump to the new counts after C1+C2.
- [ ] **Step 2** — Confirm `verify_gold_schema.py` derives the new gold tables from the TMDL contract (now that C1/C2 added them) and the parity test passes.
- [ ] **Step 3: Run** — Run: `python data-platform/scripts/verify_gold_schema.py --produced <produced.txt>` — Expected: `OK: gold parity (... contract tables covered).`
- [ ] **Step 4: Commit** — `git -c core.hooksPath=/dev/null commit -am "ci(model): re-baseline verify-semantic-model counts + gold parity for org/skills (#255)"`

**Acceptance gate:** `verify-semantic-model.yml` green with new counts; gold parity green. Human reviews + merges.

### Task C4: Ontology + crosswalk + Fabric IQ grounding (PR `sprint-23/ws-c-ontology`)

**Files:** Modify `docs/ontology/*.md` + `crosswalk.md` + conformance gate; Fabric IQ `ont_hospital_capacity` + Data Agent grounding.

- [ ] **Step 1** — Extend the ontology + crosswalk with the org spine (tenant/org-unit/department), the skills domain (assertion/demand/eligibility), and the `care_setting` split; keep the GLN golden thread + proficiency(1-5)/assurance(L0-L4) axes verbatim (D6).
- [ ] **Step 2** — Extend `ont_hospital_capacity` + the Data Agent grounding so it cites org/skills + care-setting concepts (T9).
- [ ] **Step 3: Conformance** — Run the ontology conformance gate — Expected: green.
- [ ] **Step 4: Commit** — `git -c core.hooksPath=/dev/null commit -am "feat(ontology): org/skills + care-setting concepts in ontology, crosswalk, Fabric IQ grounding (#255)"`

**Acceptance gate:** conformance gate green; Data Agent grounding cites the new concepts; doc §9 versions bumped. Human reviews + merges.

---

## WS-D — Governance (runs alongside; ADR must be Accepted before WS-B merges)

### Task D1: ADR (PR `sprint-23/ws-d-adr`)

**Files:** Create `docs/adr/00NN-curavias-landing-zone-and-skills-evidence-plugins.md`.

- [ ] **Step 1** — Write the ADR: context (MCAPS can't provision Entra users), decision (dedicated ADLS landing zone + on-demand pipeline + Sprint-21-style skills-evidence plugin + hybrid batch/Eventstream transport), consequences, and relation/supersession vs the 2026-07-19 shared design. Status `Proposed` -> `Accepted` on merge.
- [ ] **Step 2: Doc gates** — markdownlint + link-check green.
- [ ] **Step 3: Commit** — `git -c core.hooksPath=/dev/null commit -am "docs(adr): landing zone + skills-evidence plugin architecture + hybrid transport (#255)"`

**Acceptance gate:** ADR complete + `Accepted`; doc gates green. Human reviews + merges. **Merge before WS-B4.**

### Task D2: PRD FR/NFR + §7 matrix (PR `sprint-23/ws-d-prd`)

**Files:** Modify `docs/PRD.md`.

- [ ] **Step 1** — Add FR/NFR rows: landing zone (on-demand load), plugin sources (SuccessFactors/LMS/Skills-Manager/Work-ID, live-vs-simulated badge), hybrid transport, bed-vs-ops split; update §7 traceability matrix mapping each to WS/PR. §9 MINOR bump.
- [ ] **Step 2: Doc gates** — markdownlint + link-check green.
- [ ] **Step 3: Commit** — `git -c core.hooksPath=/dev/null commit -am "docs(prd): FR/NFR rows + traceability for landing zone, plugins, bed-vs-ops (#255)"`

**Acceptance gate:** new FR/NFR IDs stable; §7 matrix consistent; §9 version bumped. Human reviews + merges.

### Task D3: DSG tagging + consent lineage (PR `sprint-23/ws-d-compliance`)

**Files:** Modify `docs/COMPLIANCE.md`, `docs/SECURITY.md`.

- [ ] **Step 1** — Tag `fact_skill_assertion` + `dim_work_id_profile` as `PII-personal`; record `source_system`/`consent_basis` lineage; Work-ID consent first-class + revocable (Step-3 §4). §9 bump.
- [ ] **Step 2: Doc gates** — green.
- [ ] **Step 3: Commit** — `git -c core.hooksPath=/dev/null commit -am "docs(compliance): DSG tagging + Work-ID consent lineage for skills evidence (#255)"`

**Acceptance gate:** tagging + consent lineage documented; §9 bumped; doc gates green. Human reviews + merges.

### Task D4: MCP allow-list check (PR only if needed)

- [ ] **Step 1** — Confirm no new MCP server is required (design says WS uses existing `github-mcp`/`fabric-mcp`; expect no `.github/copilot/mcp.json` change). If a new server is genuinely needed, open a **separate** CODEOWNERS-gated PR documenting purpose + permissions + a golden task. Otherwise state `none` in the WS-D PR descriptions.

**Acceptance gate:** either no change (stated explicitly) or a CODEOWNERS-approved allow-list PR. Human reviews + merges.

---

## Definition of Done (rolls up the design §5)

- [ ] WS-A: ADLS landing zone + OneLake shortcut + Container Apps sim jobs + Eventstream lane — `what-if` clean, runbook documented.
- [ ] WS-B: generator relocated (path mismatch fixed); `DC-SKILL-EVIDENCE-v1` + 4 simulated adapters + dedup + seeder + tests green; silver gate (validate + quarantine); gold deny-by-default produces the 19 `gold.*` tables; badge preserved end-to-end.
- [ ] WS-C: `dim_hospital` replaced + facts re-keyed; skills + live-vs-simulated + bed-vs-ops measures; `verify-semantic-model.yml` re-baselined + green; ontology + crosswalk + conformance + Fabric IQ cover org/skills + care-setting.
- [ ] WS-D: ADR Accepted; PRD FR/NFR + §7 updated; DSG tagging applied.
- [ ] Every PR small, linked to #255, stacked on merged #309; SIT + PROD identical; live applies gated by `approved-to-apply`; all merges human-performed; all CI green.

## Self-Review (against the design spec)

- **Spec coverage:** D1 (landing zone) -> A1/A2/D1; D2 (ADLS+shortcut) -> A1/A2; D3 (plugin mirrors S21) -> B1/B2/B3; D4 (hybrid transport) -> A3/A4/B4; D5 (silver gate) -> B4; D6 (extend not replace) -> B4/C1/C4. Requirements #1-#4 -> A1-A4/B*/C2/D1. Sprint T1-T14 -> B0(T1), B4(T2/T3), C1(T4/T5), C2(T6/T14), C3(T7), C4(T8/T9), D1-D3(T10), A1-A2(T11), B1-B3(T12), A3-A4(T13).
- **Placeholder scan:** none — every code step shows concrete test/impl; Bicep/notebook steps specify exact resources + gates.
- **Type consistency:** `sourceMode`/`trustTier`/`selfOrConfirmed`/`workerGln`/`consentScope` used identically across B1/B2/B3 tests, `normalize.build_record`, and the schema.
- **Discovered fact:** `data/master-data/validate_master_data.py` exists (design open item §6 #3 resolved) — B4 extends it rather than authoring from scratch.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-23-sprint-23-org-skills-refactor-plan.md`. **Do not start coding** until design PR #309 is merged and you give the go-ahead. Once unblocked, two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per WS slice (WS-A/B/C/D), two-stage review between tasks (`superpowers:subagent-driven-development`).
2. **Inline Execution** — execute tasks in this session with checkpoints (`superpowers:executing-plans`).
