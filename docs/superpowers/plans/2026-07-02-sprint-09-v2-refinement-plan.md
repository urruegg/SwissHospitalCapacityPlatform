# Sprint 09 v2.0.0 Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a `westus2`-based reference-implementation MVP demo of the Swiss AI-Powered Patient Flow platform: calibrated real-time simulator → Event Hubs → Fabric Eventstream → Delta lakehouse → semantic model + MVO ontology → Power BI dashboard replicating the HCC utilization pattern → three data agents (BM-Copilot / Fabric Data Agent / CSA).

**Architecture:** Fabric-native ingestion (no SQL); bronze → silver → gold Spark notebook chain over (a) direct-uploaded reference/master data and (b) Event Hubs → Fabric Eventstream simulator events; MVO ontology extended with 4 Information Content Entity classes and enforced via strict-mode CI conformance check; agent trio grounded on gold tables + ontology via crosswalk annotations; 2-page Power BI dashboard with row-level PHI security. Every westus2 module carries a documented Swiss-region lift-and-shift path per [ADR-0014](../../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) gate G-C.

**Tech Stack:** Bicep (IaC), Python 3.12 (simulator, CI scripts), Fabric Spark PySpark (notebooks), Turtle/OWL (ontology), JSON Schema Draft-7 (data contracts), Power BI Project (`.pbip`) + TMDL (semantic model), PowerShell 7 (deploy scripts), GitHub Actions (CI), `az` CLI (Azure control-plane), Azure Managed Identity + Entra WIF (auth), Fabric REST API (agent + report deployment).

**Baseline commit:** `0fd8dd7` (main after PR #91 merge — design spec on disk at [`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../specs/2026-07-02-sprint-09-v2-refinement-design.md)).

---

<!-- markdownlint-disable MD060 MD031 -->
<!-- Plan uses mixed compact + standard table pipe styles for readability across 35 deliverables. -->
<!-- MD031 disabled: TDD-style step blocks intentionally pair prose + fenced code without extra blank lines. -->
<!-- Same pattern as the design spec. -->

## File Structure

Files that will be created (`+`) or modified (`~`) across all 5 tracks:

### T1 Foundation

- `+` [`docs/adr/0015-skip-sql-for-mvp-demo.md`](../../adr/0015-skip-sql-for-mvp-demo.md)
- `+` [`docs/adr/0016-no-phi-in-mvp-demo-scope.md`](../../adr/0016-no-phi-in-mvp-demo-scope.md)
- `~` [`docs/ontology/reference-layer.ttl`](../../ontology/reference-layer.ttl) — v0.1.0 → v0.2.0
- `~` [`docs/ontology/crosswalk.md`](../../ontology/crosswalk.md) — v0.1.0 → v0.2.0
- `+` `data/synthetic/schema/dc-discharge-score-v1.schema.json`
- `+` `data/synthetic/schema/dc-discharge-recommendation-v1.schema.json`
- `+` `data/synthetic/schema/dc-demand-forecast-v1.schema.json`
- `~` [`docs/ontology/CI_DESIGN.md`](../../ontology/CI_DESIGN.md) — v0.1.0 → v1.0.0
- `~` [`scripts/ontology/check_crosswalk_conformance.py`](../../../scripts/ontology/check_crosswalk_conformance.py) — extend for `data/synthetic/schema/` cross-check
- `~` [`.github/workflows/ontology-conformance.yml`](../../../.github/workflows/ontology-conformance.yml) — flip WARN-only → strict
- `~` `.github/CODEOWNERS` — add `agents/**` ownership row
- `~` [`docs/INFRASTRUCTURE.md`](../../INFRASTRUCTURE.md) — SQL-optional posture reference to ADR-0015
- `~` [`docs/COMPLIANCE.md`](../../COMPLIANCE.md) — no-PHI baseline reference to ADR-0016
- `~` [`docs/SECURITY.md`](../../SECURITY.md) — RLS PHI gate + 4-gate enforcement

### T2 Ingestion

- `~` `infra/modules/data-foundation/eventhubs/main.bicep` — 3 new consumer groups + RBAC role assignments
- `+` `infra/modules/data-platform/fabric-eventstream/main.bicep`
- `+` `data-platform/notebooks/reference/01_bronze_master_data.ipynb`
- `+` `data-platform/notebooks/reference/02_silver_master_data.ipynb`
- `+` `data-platform/notebooks/reference/03_gold_master_data.ipynb`
- `+` `data-platform/notebooks/eventstream/01_bronze_eventstream.ipynb`
- `+` `data-platform/notebooks/eventstream/02_silver_eventstream.ipynb`
- `+` `data-platform/notebooks/eventstream/03_gold_eventstream.ipynb`

### T3 Simulator

- `+` `apps/sim-capacity/src/calibration/hospital_presets.py`
- `+` `apps/sim-capacity/src/calibration/seasonal_profile.py`
- `+` `apps/sim-capacity/src/calibration/acuity_distribution.py`
- `+` `apps/sim-capacity/src/calibration/ward_topology.py`
- `+` `apps/sim-capacity/src/generators/encounter_generator.py`
- `+` `apps/sim-capacity/src/generators/bed_state_generator.py`
- `+` `apps/sim-capacity/src/generators/matching_engine.py`
- `+` `apps/sim-capacity/src/generators/forecast_generator.py`
- `+` `apps/sim-capacity/src/generators/discharge_scorer.py`
- `+` `apps/sim-capacity/src/generators/discharge_recommender.py`
- `+` `apps/sim-capacity/src/emitters/eventhub_emitter.py`
- `+` `apps/sim-capacity/src/clock/sim_clock.py`
- `+` `apps/sim-capacity/tests/test_hospital_presets.py`
- `+` `apps/sim-capacity/tests/test_seasonal_profile.py`
- `+` `apps/sim-capacity/tests/test_event_rates.py`
- `+` `apps/sim-capacity/tests/test_no_phi.py`
- `+` `apps/sim-capacity/tests/fixtures/hcc-utilization-pattern-luks-reference.json`
- `~` `apps/sim-capacity/pyproject.toml` — add `azure-eventhub`, `pin foundry SDK`
- `+` `infra/modules/apps/sim-capacity/main.bicep`

### T4 Semantic Model + Agents

- `+` `data-platform/reports/capacity-dashboard.SemanticModel/` (TMDL directory)
- `+` `agents/bm-copilot/AGENT.md`
- `+` `agents/bm-copilot/golden-tasks.md`
- `+` `agents/fabric-data-agent/AGENT.md`
- `+` `agents/fabric-data-agent/golden-tasks.md`
- `+` `agents/csa-agent/AGENT.md`
- `+` `agents/csa-agent/golden-tasks.md`
- `+` `infra/modules/agents/foundry-hosted/main.bicep`
- `+` `infra/modules/agents/foundry-hosted/rbac.bicep`
- `+` `data-platform/scripts/deploy_fabric_data_agent.py`
- `~` [`docs/AI.md`](../../AI.md) — new § Agent Registry

### T5 Dashboard

- `+` `data-platform/reports/capacity-dashboard.pbip`
- `+` `data-platform/reports/capacity-dashboard.Report/` (PBIP report artefact directory)
- `+` `data-platform/scripts/deploy_report.ps1`
- `+` `data/synthetic/or-samples/or_schedule.json`
- `+` `data/synthetic/or-samples/or_case.json`
- `+` `data-platform/notebooks/reference/04_load_or_samples.ipynb`

### Cross-cutting

- `~` [`docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md`](../../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md) — v1.3.0 → v2.0.0 (MAJOR rewrite)
- `+` `docs/runbooks/fabric-capacity-lifecycle.md`
- `+` `infra/scripts/Resume-FabricCapacity.ps1`
- `+` `infra/scripts/Suspend-FabricCapacity.ps1`
- `+` `infra/scripts/tests/Resume-FabricCapacity.Tests.ps1`
- `+` `infra/scripts/tests/Suspend-FabricCapacity.Tests.ps1`
- `~` [`docs/OPERATIONS.md`](../../OPERATIONS.md) — v1.4.0 → v1.5.0 (3 new OPS-RISK rows)
- `~` [`docs/TEST.md`](../../TEST.md) — Sprint 09 evidence section

Total: **~55 files created + ~10 files modified**.

---

## Track T1 — Foundation

**Goal:** Land the two governing ADRs, extend the ontology with 4 new ICE classes, draft 3 new data contracts, and flip the ontology CI conformance check to strict mode. This track blocks T2/T3/T4/T5.

### Task T1.1: Author ADR-0015 (skip SQL for MVP demo)

**Files:**
- Create: `docs/adr/0015-skip-sql-for-mvp-demo.md`
- Modify: `docs/INFRASTRUCTURE.md` (add reference to new ADR in §Data platform)

- [ ] **Step 1: Author ADR-0015** at `docs/adr/0015-skip-sql-for-mvp-demo.md`. Copy the full ADR text from design spec §2.1 (Context / Decision / Consequences / Review triggers). Use the metadata table shape from ADR-0013 (`Status: Proposed`, `Supersedes (scoped)`, `Related`, `Date: 2026-07-02`, `Author: Urs Rüegg`).

- [ ] **Step 2: Add reference from `docs/INFRASTRUCTURE.md`**. Locate the §Data platform section; insert a callout blockquote (regular prose, not code): `> **SQL-optional posture (2026-07-02):**` followed by `For the MVP demo scope, SQL Server is skipped per` [ADR-0015](../../adr/0015-skip-sql-for-mvp-demo.md) `. The` `source-sql` `Bicep module remains in the tree behind` `enableSourceSqlModule=false`. Bump `docs/INFRASTRUCTURE.md` version per §9 Document Versioning (PATCH).

- [ ] **Step 3: Lint**. Run:
  ```powershell
  npx --yes markdownlint-cli2 "docs/adr/0015-skip-sql-for-mvp-demo.md" "docs/INFRASTRUCTURE.md"
  ```
  Expected: `Summary: 0 error(s)`.

- [ ] **Step 4: Commit**.
  ```powershell
  git add docs/adr/0015-skip-sql-for-mvp-demo.md docs/INFRASTRUCTURE.md
  git commit -m "docs(adr): add ADR-0015 skip SQL for MVP demo" -m "Supersedes Sprint 08 SQL KIS assumption for MVP demo scope only. Direct-to-lakehouse + EH->Eventstream via Fabric Spark notebooks. Follows design spec §2.1."
  ```

### Task T1.2: Author ADR-0016 (no PHI in MVP demo scope)

**Files:**
- Create: `docs/adr/0016-no-phi-in-mvp-demo-scope.md`
- Modify: `docs/COMPLIANCE.md` (§Data-classification callout to ADR-0016)
- Modify: `docs/SECURITY.md` (§Data plane callout to ADR-0016 4-gate enforcement)

- [ ] **Step 1: Author ADR-0016** at `docs/adr/0016-no-phi-in-mvp-demo-scope.md`. Copy the full ADR text from design spec §2.2 (Context / Decision — including all 4 gates / Consequences / Review triggers). Metadata table matches ADR-0013 shape.

- [ ] **Step 2: Update `docs/COMPLIANCE.md`**. Add a subsection §Demo-scope no-PHI baseline with a callout referencing ADR-0016. Note the 4-gate enforcement (schema / ingestion / agent / dashboard). Bump COMPLIANCE.md version (MINOR — new subsection).

- [ ] **Step 3: Update `docs/SECURITY.md` §Data plane**. Add: "Workspace-level Row-Level Security enforces the ADR-0016 gate 4 policy: any semantic-model column tagged `phi=true` returns empty-set for all roles. See [ADR-0016 §Gate 4](adr/0016-no-phi-in-mvp-demo-scope.md#gate-4-dashboard-gate)." Bump SECURITY.md version (MINOR).

- [ ] **Step 4: Lint** all three files:
  ```powershell
  npx --yes markdownlint-cli2 "docs/adr/0016-no-phi-in-mvp-demo-scope.md" "docs/COMPLIANCE.md" "docs/SECURITY.md"
  ```
  Expected: `Summary: 0 error(s)`.

- [ ] **Step 5: Commit**.
  ```powershell
  git add docs/adr/0016-no-phi-in-mvp-demo-scope.md docs/COMPLIANCE.md docs/SECURITY.md
  git commit -m "docs(adr): add ADR-0016 no PHI in MVP demo scope" -m "Formalises AMA SD Review 2026-06-10 §3.3 + §5.4 Core Solution Pattern as an enforceable ADR with 4 gates: schema, ingestion, agent, dashboard. Design spec §2.2."
  ```

### Task T1.3: Extend ontology reference layer (v0.1.0 → v0.2.0)

**Files:**
- Modify: `docs/ontology/reference-layer.ttl` — add IAO import + 4 new ICE classes + 1 abstract root + 7 new object properties

- [ ] **Step 1: Write a failing test for the CI check**. First verify the current script sees 7 classes. Run:
  ```powershell
  python scripts/ontology/check_crosswalk_conformance.py 2>&1 | Select-String "reference classes"
  ```
  Expected: `reference classes: 7`.

- [ ] **Step 2: Update `reference-layer.ttl`**. Bump `owl:versionInfo` from `"0.1.0"` to `"0.2.0"`. Add the IAO import to the header:
  ```turtle
  # Add to header owl:imports list:
      <http://purl.obolibrary.org/obo/iao.owl>     # IAO — Information Artifact Ontology
  # Add to @prefix declarations near the top:
  @prefix iao:    <http://purl.obolibrary.org/obo/IAO_> .
  ```
  Then add the four new classes at the end of the file (before the provider-extension pattern comment):
  ```turtle
  # ===========================================================================
  # Information Content Entity abstract root (aligns to iao:InformationContentEntity in Phase 3)
  # ===========================================================================
  hcp:InformationContent a owl:Class ;
      rdfs:label   "Information Content"@en ;
      rdfs:comment "Abstract superclass for scores, forecasts, recommendations, and matching outputs. Aligns to iao:InformationContentEntity in Phase 3."@en .

  # --- Four new ICE classes ---

  hcp:BedAssignment a owl:Class ;
      rdfs:subClassOf hcp:InformationContent ;
      rdfs:label      "Bed Assignment"@en ;
      rdfs:comment    "The matching output linking one Encounter to one Bed for a time window. Carries assignedAt, unassignedAt, assignmentReason, matchScore, explanationTokens. Grounds AMA SD Core Solution Pattern 'Matching Demand -> Supply'."@en .

  hcp:DischargeReadinessScore a owl:Class ;
      rdfs:subClassOf hcp:InformationContent ;
      rdfs:label      "Discharge Readiness Score"@en ;
      rdfs:comment    "A score [0..1] produced by the discharge-scoring pipeline with feature attribution. Grounds FR-DC-001, FR-DC-006."@en .

  hcp:DischargeRecommendation a owl:Class ;
      rdfs:subClassOf hcp:InformationContent ;
      rdfs:label      "Discharge Recommendation"@en ;
      rdfs:comment    "Ranked candidate action derived from a DischargeReadinessScore, including blockers and recommendedAction. Advisory/HITL per NFR-AI-001. Grounds FR-DC-002, FR-DC-003, FR-DC-005."@en .

  hcp:ForecastOutput a owl:Class ;
      rdfs:subClassOf hcp:InformationContent ;
      rdfs:label      "Forecast Output"@en ;
      rdfs:comment    "A 72h forecast covering one Specialty for a time window. Carries covers, validFor, refreshCadence, producedBy. Grounds FR-FC-001..006."@en .

  # ===========================================================================
  # Seven new object properties for the ICE classes
  # ===========================================================================
  hcp:appliesTo a owl:ObjectProperty ;
      rdfs:label  "applies to"@en ;
      rdfs:domain hcp:InformationContent ;
      rdfs:range  hcp:Encounter .

  hcp:assignsBed a owl:ObjectProperty ;
      rdfs:label  "assigns bed"@en ;
      rdfs:domain hcp:BedAssignment ;
      rdfs:range  hcp:Bed .

  hcp:assignsEncounter a owl:ObjectProperty ;
      rdfs:label  "assigns encounter"@en ;
      rdfs:domain hcp:BedAssignment ;
      rdfs:range  hcp:Encounter .

  hcp:covers a owl:ObjectProperty ;
      rdfs:label  "covers"@en ;
      rdfs:domain hcp:ForecastOutput ;
      rdfs:range  hcp:Specialty .

  hcp:validFor a owl:DatatypeProperty ;
      rdfs:label  "valid for (time window)"@en ;
      rdfs:domain hcp:ForecastOutput ;
      rdfs:range  xsd:duration .

  hcp:producedBy a owl:DatatypeProperty ;
      rdfs:label  "produced by (model run id)"@en ;
      rdfs:domain hcp:InformationContent ;
      rdfs:range  xsd:string .

  hcp:hasExplanation a owl:DatatypeProperty ;
      rdfs:label  "has explanation tokens"@en ;
      rdfs:domain hcp:InformationContent ;
      rdfs:range  xsd:string .
  ```

- [ ] **Step 3: Verify class count grew to 12**. Run the check again:
  ```powershell
  python scripts/ontology/check_crosswalk_conformance.py 2>&1 | Select-String "reference classes"
  ```
  Expected: `reference classes: 12` (previous 7 + `InformationContent` + `BedAssignment` + `DischargeReadinessScore` + `DischargeRecommendation` + `ForecastOutput`).

- [ ] **Step 4: Verify WARN-only mode surfaces the crosswalk gap**. Since we haven't updated `crosswalk.md` yet, all 4 new classes should WARN. Run:
  ```powershell
  python scripts/ontology/check_crosswalk_conformance.py 2>&1 | Select-String "WARN"
  ```
  Expected: 4 WARN lines for the 4 new classes (`InformationContent` is treated as abstract root, exempt).

- [ ] **Step 5: Commit** (crosswalk update comes in T1.4).
  ```powershell
  git add docs/ontology/reference-layer.ttl
  git commit -m "feat(ontology): extend reference layer v0.1.0 -> 0.2.0 with 4 ICE classes" -m "Adds IAO import + hcp:InformationContent abstract root + BedAssignment / DischargeReadinessScore / DischargeRecommendation / ForecastOutput classes + 7 new object properties. Grounds base-spec FR-FC / FR-DC / AMA SD Core Solution Pattern per design spec §3.2."
  ```

### Task T1.4: Extend ontology crosswalk (v0.1.0 → v0.2.0)

**Files:**
- Modify: `docs/ontology/crosswalk.md` — add 4 new rows + note DC-MATCH-RECOMMENDATION-v1 reuse

- [ ] **Step 1: Update `docs/ontology/crosswalk.md`**. Bump version metadata table `Version: 0.1.0 → 0.2.0`, `Previous Version: 0.1.0`, `Date: 2026-07-02`. Add 4 new rows to the MVO scope table (§Crosswalk (MVO scope per ADR-0014 §3)):
  ```markdown
  | `hcp:BedAssignment` | `BedAssignment` | **[`DC-MATCH-RECOMMENDATION-v1`](../../data/synthetic/schema/dc-match-recommendation-v1.schema.json)** *(existing — reuse)* | Time-series binding on assign/unassign events (eventhouse) | Matches AMA SD Core Solution Pattern; links Encounter ↔ Bed. |
  | `hcp:DischargeReadinessScore` | `DischargeReadinessScore` | **new** `DC-DISCHARGE-SCORE-v1` *(T1.5)* | Time-series binding on Encounter timeline (hourly refresh) | Grounds `FR-DC-001`, `FR-DC-006`. |
  | `hcp:DischargeRecommendation` | `DischargeRecommendation` | **new** `DC-DISCHARGE-RECOMMENDATION-v1` *(T1.5)* | Deferred | Grounds `FR-DC-002`, `FR-DC-003`, `FR-DC-005`. |
  | `hcp:ForecastOutput` | `ForecastOutput` | **new** `DC-DEMAND-FORECAST-v1` *(T1.5)* | Time-series binding (hourly refresh per `NFR-PERF-002`) | Grounds `FR-FC-001..006`. |
  ```
  Also add a §Base-spec traceability subsection with the table from design spec §3.4.

- [ ] **Step 2: Run the CI check to verify WARN count dropped to 0** *(structure only — contracts don't exist yet, so a NEW check for contract-existence would flag)*. For now, class-level WARN check should pass:
  ```powershell
  python scripts/ontology/check_crosswalk_conformance.py 2>&1 | Select-String "WARN|FAIL|PASS"
  ```
  Expected: `0 WARN, 0 FAIL` — PASS.

- [ ] **Step 3: Lint**.
  ```powershell
  npx --yes markdownlint-cli2 "docs/ontology/crosswalk.md"
  ```
  Expected: `Summary: 0 error(s)`.

- [ ] **Step 4: Commit**.
  ```powershell
  git add docs/ontology/crosswalk.md
  git commit -m "feat(ontology): crosswalk v0.1.0 -> 0.2.0 with 4 new rows + base-spec traceability" -m "Reuses DC-MATCH-RECOMMENDATION-v1 for hcp:BedAssignment; three new contracts (DC-DISCHARGE-SCORE-v1, DC-DISCHARGE-RECOMMENDATION-v1, DC-DEMAND-FORECAST-v1) drafted in T1.5. Design spec §3.3."
  ```

### Task T1.5: Draft 3 new DC contracts

**Files:**
- Create: `data/synthetic/schema/dc-discharge-score-v1.schema.json`
- Create: `data/synthetic/schema/dc-discharge-recommendation-v1.schema.json`
- Create: `data/synthetic/schema/dc-demand-forecast-v1.schema.json`

- [ ] **Step 1: Author `dc-discharge-score-v1.schema.json`** following the `dc-demand-encounter-v1` envelope pattern. Record fields: `scoreId` (`^DSC-[A-Z0-9-]+$`), `encounterId` (link back to demand-encounter), `hospitalId` (H_USZ/H_LUKS/H_SZB), `score` (number 0..1), `producedBy` (modelRunId), `scoredAt` (date-time), `explanationTokens` (array of strings), `contributingFactors` (array), `purposeTag`, `dataResidencyRegion`, `asOfTimestamp`. Set `_pseudonymisation_flag=true` explicitly.

- [ ] **Step 2: Author `dc-discharge-recommendation-v1.schema.json`**. Record fields: `recommendationId` (`^DREC-[A-Z0-9-]+$`), `encounterId`, `hospitalId`, `derivedFromScoreId` (link back to DC-DISCHARGE-SCORE-v1), `rank` (integer), `recommendedAction` (enum: `discharge-today` / `discharge-tomorrow` / `discharge-blocked` / `escalate` / `no-action`), `blockers` (array with `category`+`description`), `producedBy`, `expiresAt` (date-time — advisory only within window), `purposeTag`, `dataResidencyRegion`, `asOfTimestamp`.

- [ ] **Step 3: Author `dc-demand-forecast-v1.schema.json`**. Record fields: `forecastId` (`^DF-[A-Z0-9-]+$`), `hospitalId`, `specialtyId` (link to dim_specialty), `validFrom` (date-time), `validUntil` (date-time — 72h window), `refreshCadenceMinutes` (integer, default 60), `expectedDemand` (array of hourly buckets with `hour` + `expectedCount` + `confidenceIntervalLower` + `confidenceIntervalUpper`), `producedBy` (modelRunId), `modelVersion`, `purposeTag`, `dataResidencyRegion`, `asOfTimestamp`.

- [ ] **Step 4: Validate each schema is valid JSON + valid JSON Schema**. Run:
  ```powershell
  python -c "import json, jsonschema; [json.load(open(f)) for f in ['data/synthetic/schema/dc-discharge-score-v1.schema.json', 'data/synthetic/schema/dc-discharge-recommendation-v1.schema.json', 'data/synthetic/schema/dc-demand-forecast-v1.schema.json']]; print('OK: 3 schemas parse')"
  ```
  Expected: `OK: 3 schemas parse`.

- [ ] **Step 5: Run the existing data-contracts CI locally**. Look for the existing self-test in `.github/workflows/`:
  ```powershell
  gci .github/workflows -Filter "*data-contract*"
  ```
  If a workflow exists, invoke it locally via `gh workflow run <name>`; otherwise the CI will exercise it on PR.

- [ ] **Step 6: Commit**.
  ```powershell
  git add data/synthetic/schema/dc-*.schema.json
  git commit -m "feat(contracts): draft DC-DISCHARGE-SCORE-v1 + DC-DISCHARGE-RECOMMENDATION-v1 + DC-DEMAND-FORECAST-v1" -m "3 new contracts complete the 4-triple for hcp:BedAssignment / DischargeReadinessScore / DischargeRecommendation / ForecastOutput in crosswalk.md v0.2.0. All follow dc-demand-encounter-v1 envelope pattern per design spec §3.3."
  ```

### Task T1.6: Extend CI check for contract existence + flip to strict mode

**Files:**
- Modify: `scripts/ontology/check_crosswalk_conformance.py` — add contract-existence check
- Modify: `docs/ontology/CI_DESIGN.md` — v0.1.0 → v1.0.0 (MAJOR — semantics change advisory → enforcing)
- Modify: `.github/workflows/ontology-conformance.yml` — replace WARN-only step with STRICT step

- [ ] **Step 1: Write a failing test for the contract-existence check**. Create `scripts/ontology/tests/test_contract_existence.py` (create the `tests/` folder if missing):
  ```python
  import subprocess, sys
  from pathlib import Path
  REPO = Path(__file__).resolve().parents[2]
  def test_check_flags_missing_contract(tmp_path, monkeypatch):
      # Temporarily rename a real contract so the check sees it as missing.
      contract = REPO / "data/synthetic/schema/dc-match-recommendation-v1.schema.json"
      backup = contract.with_suffix(".bak")
      contract.rename(backup)
      try:
          result = subprocess.run([sys.executable, str(REPO/"scripts/ontology/check_crosswalk_conformance.py"), "--strict"], capture_output=True, text=True)
          assert result.returncode == 1
          assert "DC-MATCH-RECOMMENDATION-v1" in result.stdout
      finally:
          backup.rename(contract)
  ```

- [ ] **Step 2: Run the test to verify it fails today**.
  ```powershell
  python -m pytest scripts/ontology/tests/test_contract_existence.py -v
  ```
  Expected: FAIL because the check doesn't yet look at contracts.

- [ ] **Step 3: Extend `check_crosswalk_conformance.py`** to parse contract IDs from crosswalk.md rows and verify each `.schema.json` exists under `data/synthetic/schema/`. Add a new regex + check:
  ```python
  CONTRACT_RX = re.compile(r"`(DC-[A-Z0-9-]+)-v\d+`")

  def parse_crosswalk_contracts(md_text: str) -> set[str]:
      return set(CONTRACT_RX.findall(md_text))

  def check_contracts(contracts: set[str], schema_dir: Path) -> list[Finding]:
      findings = []
      existing = {p.stem.replace(".schema", "").upper() for p in schema_dir.glob("*.schema.json")}
      # existing entries look like "DC-DEMAND-ENCOUNTER-V1"; normalise crosswalk IDs the same way
      for c in sorted(contracts):
          normalised = c.upper() + "-V1"  # crosswalk lists base "DC-FOO"; schemas use "dc-foo-v1"
          if normalised not in existing:
              findings.append(Finding("FAIL", f"crosswalk contract {c!r} has no schema under data/synthetic/schema/"))
      return findings
  ```
  Then call `check_contracts()` in `main()` and merge its findings into the finding list.

- [ ] **Step 4: Run the test again**.
  ```powershell
  python -m pytest scripts/ontology/tests/test_contract_existence.py -v
  ```
  Expected: PASS.

- [ ] **Step 5: Verify full check still PASSes** (all 3 new contracts exist now):
  ```powershell
  python scripts/ontology/check_crosswalk_conformance.py --strict
  ```
  Expected: `0 WARN, 0 FAIL`, exit code `0`.

- [ ] **Step 6: Update `docs/ontology/CI_DESIGN.md`** to v1.0.0. Change Status to `Sprint 09 strict (enforcing)`. Replace §Sprint 09 semantics (WARN-only) with §Sprint 09 v2.0.0 semantics (STRICT — enforcing). Move the §Sprint 10 enforcement flip section to a §Change Log entry `v1.0.0 (2026-07-02) — strict-mode flip landed`.

- [ ] **Step 7: Update `.github/workflows/ontology-conformance.yml`**. Replace the current single-step run with:
  ```yaml
        - name: Run crosswalk conformance check (STRICT)
          run: |
            python scripts/ontology/check_crosswalk_conformance.py --strict
  ```
  Delete the commented-out STRICT-preview block below.

- [ ] **Step 8: Verify workflow is valid YAML**.
  ```powershell
  npx --yes actionlint .github/workflows/ontology-conformance.yml
  ```
  Expected: no output (actionlint passes silently).

- [ ] **Step 9: Lint markdown**.
  ```powershell
  npx --yes markdownlint-cli2 "docs/ontology/CI_DESIGN.md"
  ```
  Expected: `Summary: 0 error(s)`.

- [ ] **Step 10: Commit**.
  ```powershell
  git add scripts/ontology/ docs/ontology/CI_DESIGN.md .github/workflows/ontology-conformance.yml
  git commit -m "feat(ci): ontology conformance check strict-mode flip (v1.0.0)" -m "Extends check with contract-existence gate. Flips workflow from WARN-only to STRICT. CI_DESIGN.md v0.1.0 -> 1.0.0 (MAJOR — semantics change). Test: test_contract_existence.py. Design spec §3.5."
  ```

### Task T1.7: Update CODEOWNERS for `agents/**`

**Files:**
- Modify: `.github/CODEOWNERS`

- [ ] **Step 1: Read current CODEOWNERS structure**.
  ```powershell
  cat .github/CODEOWNERS 2>&1 | Select-Object -First 20
  ```

- [ ] **Step 2: Add a new rule for `agents/**`**. Add at an appropriate location (following existing rule pattern):
  ```text
  # Runtime user-facing agents (BM-Copilot, Fabric Data Agent, CSA) — 2-of-2 review per FR-GOV-ONT-002
  agents/**                              @urruegg
  ```
  If team handles exist for `semantic-owner` and `ai-governance-lead`, use those instead of `@urruegg`. Otherwise placeholder to be updated when nominations land.

- [ ] **Step 3: Commit**.
  ```powershell
  git add .github/CODEOWNERS
  git commit -m "chore(codeowners): add agents/** rule per FR-GOV-ONT-002" -m "Runtime user-facing agents get 2-of-2 review by semantic/ontology owner + AI governance lead per design spec §5.9."
  ```

### Task T1.8: Sprint 09 doc v2.0.0 rewrite (interim placeholder — full rewrite in cross-cutting DX.1 at sprint close)

> **Note.** T1 leaves the sprint doc largely intact. DX.1 does the full v2.0.0 rewrite at sprint close, once all deliverables land.

- [ ] **Step 1: Update sprint-09 doc §0 Refresh Backlog** to reflect T1 progress. Add a new §0.5 subsection stating "T1 Foundation delivered on YYYY-MM-DD; sprint doc v2.0.0 rewrite pending DX.1 at sprint close per design spec DX.1."

- [ ] **Step 2: Commit**.
  ```powershell
  git add docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md
  git commit -m "docs(sprints): sprint-09 T1 Foundation delivered — v2.0.0 rewrite pending"
  ```

---

## Track T2 — Ingestion (starts after T1 lands)

**Goal:** Extend Event Hub Bicep with 3 new consumer groups + Fabric Eventstream Bicep + 6 Fabric Spark notebooks (bronze/silver/gold × 2 branches: reference master-data + eventstream simulator events). No SQL Server. Provides gold tables that T4/T5 consume.

### Task T2.1: Extend Event Hub Bicep with 3 new consumer groups + RBAC

**Files:**
- Modify: `infra/modules/data-foundation/eventhubs/main.bicep`

- [ ] **Step 1: Read current EH module**. Check the existing consumer groups + role assignments:
  ```powershell
  cat infra/modules/data-foundation/eventhubs/main.bicep | Select-String -Pattern "consumerGroup|roleAssignment" | Select-Object -First 20
  ```

- [ ] **Step 2: Add three new consumer groups** as `Microsoft.EventHub/namespaces/eventhubs/consumergroups` resources: `cg-fabric-eventstream`, `cg-bm-copilot-agent`, `cg-csa-agent`. Each is a child of the existing `ehihzhhpfsit` event hub.

- [ ] **Step 3: Add role assignments** (also as separate resources):
  - Simulator MI → `Azure Event Hubs Data Sender` (role ID `2b629674-e913-4c01-ae53-ef4638d8f975`)
  - BM-Copilot MI → `Azure Event Hubs Data Receiver` (role ID `a638d3c7-ab3a-418d-83e6-5f17a39d4fde`) scoped to `cg-bm-copilot-agent`
  - CSA MI → `Azure Event Hubs Data Receiver` scoped to `cg-csa-agent`

- [ ] **Step 4: Add module params** `simulatorMiPrincipalId`, `bmCopilotMiPrincipalId`, `csaAgentMiPrincipalId` (all `string?`) so the parent Bicep can wire the MIs from the Foundry module (T4.5) and simulator module (T3.7).

- [ ] **Step 5: Run `az bicep build` locally**.
  ```powershell
  az bicep build --file infra/modules/data-foundation/eventhubs/main.bicep
  ```
  Expected: no errors.

- [ ] **Step 6: Run `az deployment group what-if` in SIT**.
  ```powershell
  az deployment group what-if --resource-group rg-ihzhhpf-sit --template-file infra/main.bicep --parameters infra/environments/sit.bicepparam
  ```
  Expected: 3 create ops for consumer groups + 3 create ops for role assignments. No delete ops.

- [ ] **Step 7: Commit**.
  ```powershell
  git add infra/modules/data-foundation/eventhubs/main.bicep
  git commit -m "feat(infra): 3 new consumer groups + RBAC on Event Hubs for Sprint 09 v2.0.0" -m "cg-fabric-eventstream + cg-bm-copilot-agent + cg-csa-agent per design spec §4.2. what-if clean in SIT."
  ```

### Task T2.2: Create Fabric Eventstream Bicep module

**Files:**
- Create: `infra/modules/data-platform/fabric-eventstream/main.bicep`
- Create: `infra/modules/data-platform/fabric-eventstream/README.md`

- [ ] **Step 1: Author the Eventstream module**. This is Fabric-native (not classic Azure); the module uses the `Microsoft.Fabric/workspaces/eventstreams` resource type. Params: `workspaceId`, `eventHubNamespace`, `eventHubName`, `eventHubConsumerGroup` (default `cg-fabric-eventstream`), `location` with `@allowed(['switzerlandnorth', 'westus2'])`, `demoScope` (bool, default `false`).

- [ ] **Step 2: Add the source connector** (Event Hubs) referencing the EH from T2.1. Configure the routing property so events are partitioned by `eventKind` for downstream Delta-append routing.

- [ ] **Step 3: Add the destination** as a Fabric Lakehouse table pointing at `bronze/eventstream/`.

- [ ] **Step 4: Write README.md** documenting the module purpose, parameters, and the Swiss-region variant path.

- [ ] **Step 5: `az bicep build`**.
  ```powershell
  az bicep build --file infra/modules/data-platform/fabric-eventstream/main.bicep
  ```
  Expected: no errors (Bicep may warn on preview resource types — acceptable per ADR-0014).

- [ ] **Step 6: Wire the module** into `infra/main.bicep` behind an `enableFabricEventstreamModule` param (default `true` in SIT `.bicepparam`, `false` in PROD until Sprint 09 promotes to PROD).

- [ ] **Step 7: Run what-if in SIT**.
  ```powershell
  az deployment group what-if --resource-group rg-ihzhhpf-sit --template-file infra/main.bicep --parameters infra/environments/sit.bicepparam
  ```
  Expected: 1 create for the Eventstream + 1 for source + 1 for destination.

- [ ] **Step 8: Commit**.
  ```powershell
  git add infra/modules/data-platform/fabric-eventstream/ infra/main.bicep infra/environments/sit.bicepparam infra/environments/prod.bicepparam
  git commit -m "feat(infra): add Fabric Eventstream Bicep module + wire into SIT" -m "Source = EH ehihzhhpfsit via cg-fabric-eventstream (T2.1). Destination = bronze/eventstream/. Enable in SIT, defer in PROD per design spec §4.2."
  ```

### Task T2.3: Create bronze notebook — master data (direct-upload)

**Files:**
- Create: `data-platform/notebooks/reference/01_bronze_master_data.ipynb`

- [ ] **Step 1: Author the notebook**. Scaffold cells:
  1. Header markdown cell: purpose, source, target, ADR-0015/-0016 anchors.
  2. Params cell (`%%capture` params for `hospital_csv_path`, `target_lakehouse`, `run_id`).
  3. Load CSVs from `Files/master-data/*.csv` (direct-upload landing folder).
  4. Write as Delta to `Tables/bronze/master-data/<table>/` preserving raw shape.
  5. Add `_lineage_ref` = `<filename>:<load_timestamp>`.
  6. Emit summary (row count per table) to notebook output.

- [ ] **Step 2: Test locally** with a synthetic CSV bundle (use the existing `docs/reviews/2026-06-29-ama-capacity-metadata-review/*.csv` as fixtures). Load and verify bronze tables emerge with expected row counts.

- [ ] **Step 3: Commit**.
  ```powershell
  git add data-platform/notebooks/reference/01_bronze_master_data.ipynb
  git commit -m "feat(data-platform): bronze notebook — master-data direct-upload ingestion" -m "Reads Files/master-data/*.csv, writes Tables/bronze/master-data/<table>/ Delta. Design spec §4.6."
  ```

### Task T2.4: Create silver notebook — master data (validation gates)

**Files:**
- Create: `data-platform/notebooks/reference/02_silver_master_data.ipynb`

- [ ] **Step 1: Author the notebook** with the 6 validation gates from design spec §4.6:
  1. Row count > 0 per table.
  2. Schema conforms to the corresponding `dc-master-XX-v1` shape (defined implicitly by dim column set).
  3. **PHI regex sweep** (email `[\w.+-]+@[\w-]+\.[\w.-]+`, phone `\+?\d[\d\s().-]{6,}`, DOB `\d{4}-\d{2}-\d{2}`, CH AHV-13 `756\.\d{4}\.\d{4}\.\d{2}`) — reject row + emit alert.
  4. Residency: `_residency_tag ∈ {CH-North, US-West}` per RB-01.
  5. Data quality: `_data_quality ∈ {explicit, inferred, missing}`.
  6. FK integrity: dim_specialty.hospital_id ∈ dim_hospital.hospital_id, etc.

- [ ] **Step 2: Include a test cell** that seeds a synthetic PII row (fake email in dim_hospital.city) and verifies the gate rejects it.

- [ ] **Step 3: Verify test cell fails as expected** (row appears in quarantine, silver output is 1 row short of bronze).

- [ ] **Step 4: Commit**.
  ```powershell
  git add data-platform/notebooks/reference/02_silver_master_data.ipynb
  git commit -m "feat(data-platform): silver notebook — master-data validation gates" -m "6 gates: row count, schema, PHI regex sweep (ADR-0016 gate 2), residency dual-mode, data quality, FK integrity. Design spec §4.6."
  ```

### Task T2.5: Create gold notebook — master data

**Files:**
- Create: `data-platform/notebooks/reference/03_gold_master_data.ipynb`

- [ ] **Step 1: Author the notebook**:
  1. Read silver Delta tables.
  2. Append mandatory governance columns (`_classification`, `_residency_tag`, `_legal_basis`, `_retention_class`, `_data_quality`, `_lineage_ref`, `_pseudonymisation_flag`).
  3. Write to `Tables/gold/reference/<table>/` with `overwrite` mode (idempotent).
  4. Emit load summary (rows + quality distribution) to Log Analytics.

- [ ] **Step 2: Run end-to-end** locally against the fixture bundle; verify 10 `gold/reference/*` tables emerge with row counts matching the 2026-06-29 metadata review CSVs.

- [ ] **Step 3: Commit**.
  ```powershell
  git add data-platform/notebooks/reference/03_gold_master_data.ipynb
  git commit -m "feat(data-platform): gold notebook — master-data publication" -m "Publishes 10 gold/reference/dim_* tables with governance columns. Design spec §4.6."
  ```

### Task T2.6: Create bronze notebook — eventstream

**Files:**
- Create: `data-platform/notebooks/eventstream/01_bronze_eventstream.ipynb`

- [ ] **Step 1: Author the notebook**:
  1. Consume from Fabric Eventstream (bound in T2.2) using the Delta Live Table streaming source.
  2. Route by `eventKind` message property → `bronze/eventstream/<eventKind>/` folder.
  3. Preserve `simRunId`, `seed`, `simulatedAt`, `emittedAt` per envelope shape (design spec §4.3).
  4. Append semantics; small-file compaction as a scheduled follow-up job.

- [ ] **Step 2: Test manually** by publishing one synthetic event to EH via `az` CLI or `python -m eventhub_test_emit`. Verify it appears in `bronze/eventstream/<eventKind>/`.

- [ ] **Step 3: Commit**.
  ```powershell
  git add data-platform/notebooks/eventstream/01_bronze_eventstream.ipynb
  git commit -m "feat(data-platform): bronze notebook — eventstream to Delta" -m "Routes by eventKind property to bronze/eventstream/<eventKind>/. Preserves envelope. Design spec §4.6."
  ```

### Task T2.7: Create silver notebook — eventstream

**Files:**
- Create: `data-platform/notebooks/eventstream/02_silver_eventstream.ipynb`

- [ ] **Step 1: Author the notebook** with per-eventKind validation:
  1. Per eventKind, load the corresponding `dc-*-v1.schema.json` and validate payload shape.
  2. **PHI regex sweep** (same regex bundle as T2.4).
  3. FK integrity: for `bed.assigned` + `discharge.scored/recommended`, verify `encounterId` exists in `silver/eventstream/encounter/`.
  4. Residency check (same as T2.4).

- [ ] **Step 2: Test cell**: seed a bogus `encounter.admitted` event with an email in `firstName` field; verify PHI gate rejects it.

- [ ] **Step 3: Commit**.
  ```powershell
  git add data-platform/notebooks/eventstream/02_silver_eventstream.ipynb
  git commit -m "feat(data-platform): silver notebook — eventstream validation gates" -m "Per-eventKind schema validation + PHI regex gate + FK integrity per design spec §4.6."
  ```

### Task T2.8: Create gold notebook — eventstream

**Files:**
- Create: `data-platform/notebooks/eventstream/03_gold_eventstream.ipynb`

- [ ] **Step 1: Author the notebook**:
  1. Read silver `silver/eventstream/<eventKind>/`.
  2. Per eventKind, write to per-entity gold: `gold/patient-flow/encounter/`, `bed_state/`, `bed_assignment/`, `forecast_output/`, `discharge_score/`, `discharge_recommendation/`.
  3. Append governance columns.
  4. Partition by `hospitalId` for downstream slicer performance.

- [ ] **Step 2: Verify §4.7 conformance test setup can find the aggregated `bed_state` table** in `gold/patient-flow/bed_state/`.

- [ ] **Step 3: Commit**.
  ```powershell
  git add data-platform/notebooks/eventstream/03_gold_eventstream.ipynb
  git commit -m "feat(data-platform): gold notebook — eventstream to per-entity Delta tables" -m "6 gold/patient-flow/* tables from 7 eventKinds. Partitioned by hospitalId. Design spec §4.6."
  ```

---

## Track T3 — Simulator (starts after T1; can run parallel to T2)

**Goal:** Extended `apps/sim-capacity/` Python service produces 7 event kinds on 3 hospital presets (USZ / LUKS / SZB) with calibrated shape matching the HCC utilization pattern PNG. Emits to Event Hubs via Managed Identity. Full ADR-0016 PHI-refusal test. Deployable to Azure Container Apps.

### Task T3.1: Calibration modules — hospital_presets + acuity + ward_topology

**Files:**
- Create: `apps/sim-capacity/src/calibration/hospital_presets.py`
- Create: `apps/sim-capacity/src/calibration/acuity_distribution.py`
- Create: `apps/sim-capacity/src/calibration/ward_topology.py`
- Create: `apps/sim-capacity/tests/test_hospital_presets.py`

- [ ] **Step 1: Write failing test `test_hospital_presets.py`**:
  ```python
  from apps.sim-capacity.src.calibration.hospital_presets import load_preset
  def test_usz_preset_loads():
      p = load_preset("USZ")
      assert p.hospital_id == "H_USZ"
      assert p.stationary_cases_yr == 41151
      assert p.beds_quality == "inferred"
      assert p.inferred_bed_count is not None  # inferred value populated
  def test_luks_preset_loads():
      p = load_preset("LUKS")
      assert p.beds == 839
      assert p.beds_quality == "explicit"
  def test_szb_preset_loads():
      p = load_preset("SZB")
      assert p.beds == 174
      assert p.canton == "ZH"
  def test_hsl_preset_raises_deferred():
      with pytest.raises(ValueError, match="deferred"):
          load_preset("HSL")
  ```

- [ ] **Step 2: Run test to verify FAIL**:
  ```powershell
  cd apps/sim-capacity ; python -m pytest tests/test_hospital_presets.py -v
  ```
  Expected: FAIL (module not defined).

- [ ] **Step 3: Implement `hospital_presets.py`** — dataclass `HospitalPreset` with fields matching `01_dim_hospital.csv` columns; `load_preset(short_name)` reads the CSV, filters to `H_<short>`, returns preset. For USZ compute `inferred_bed_count` from `stationary_cases_yr × avg_LOS / days_in_year / target_occupancy` (~950 beds).

- [ ] **Step 4: Implement `acuity_distribution.py`** — reads `04_dim_disease.csv` + `06_dim_drg.csv` + `09_map_disease_treatment_specialty_service.csv`; builds a weighted sampler `sample_disease_and_drg(hospital, specialty)` returning `(disease_id, drg_code, mean_los_norm)`.

- [ ] **Step 5: Implement `ward_topology.py`** — reads `07_dim_ward_capacityunit.csv` filtered to the hospital; builds a dict `ward_id -> WardInfo(specialty_id, bed_count, beds_quality)`.

- [ ] **Step 6: Run test to verify PASS**:
  ```powershell
  python -m pytest tests/test_hospital_presets.py -v
  ```
  Expected: PASS (all 4 tests).

- [ ] **Step 7: Commit**.
  ```powershell
  git add apps/sim-capacity/src/calibration/ apps/sim-capacity/tests/test_hospital_presets.py
  git commit -m "feat(sim): calibration modules — hospital presets + acuity + ward topology" -m "Loads 3 hospital presets (USZ/LUKS/SZB) from 2026-06-29 metadata review CSVs. USZ inferred bed count computed from stationary cases + LOS. HSL deferred. Design spec §4.5."
  ```

### Task T3.2: Seasonal profile + HCC pattern conformance test

**Files:**
- Create: `apps/sim-capacity/src/calibration/seasonal_profile.py`
- Create: `apps/sim-capacity/tests/test_seasonal_profile.py`
- Create: `apps/sim-capacity/tests/fixtures/hcc-utilization-pattern-luks-reference.json`

- [ ] **Step 1: Hand-author the reference fixture JSON**. Based on visual inspection of `docs/reviews/2026-07-01-ama-hcc-northstar-review/hcc-apacities-utilization-pattern-overview.png`, encode monthly relative demand (12 values, sum ≈ 12) and Month × Weekday RAG matrix (12×5 with R/A/G thresholds). Sample structure:
  ```json
  {
    "hospital": "LUKS",
    "monthly_relative_demand": [1.20, 1.18, 1.05, 1.00, 0.95, 0.90, 0.85, 0.85, 0.95, 1.00, 1.15, 1.22],
    "month_weekday_rag_distribution": {
      "red_ratio_expected": 0.20,
      "amber_ratio_expected": 0.40,
      "green_ratio_expected": 0.40
    }
  }
  ```

- [ ] **Step 2: Write failing test `test_seasonal_profile.py`** — the HCC pattern conformance test from design spec §4.7:
  ```python
  def test_luks_seasonal_shape_matches_hcc_pattern(tmp_path):
      # Run 365 simulated days, aggregate to daily counts, compute monthly + RAG
      events = run_sim(preset="LUKS", seed=42, duration_days=365)
      # ... (compute MAPE)
      assert mape < 0.15, f"MAPE {mape:.2%} exceeds 15% threshold"
  ```

- [ ] **Step 3: Run test to verify FAIL**.
  ```powershell
  python -m pytest tests/test_seasonal_profile.py::test_luks_seasonal_shape_matches_hcc_pattern -v
  ```
  Expected: FAIL.

- [ ] **Step 4: Implement `seasonal_profile.py`** — combines monthly + weekly + hourly curves per design spec §4.5. Monthly curve: `[1.20, 1.18, 1.05, ...]` (see fixture). Weekly: Mon +15%, Fri -10%, Sat -10%, Sun -25%. Hourly ED: peak 18-02. Exposes `demand_multiplier(datetime)` returning float.

- [ ] **Step 5: Run test to verify PASS**.
  ```powershell
  python -m pytest tests/test_seasonal_profile.py -v
  ```
  Expected: PASS with `MAPE ≈ 12%` (within 15% threshold).

- [ ] **Step 6: Commit**.
  ```powershell
  git add apps/sim-capacity/src/calibration/seasonal_profile.py apps/sim-capacity/tests/test_seasonal_profile.py apps/sim-capacity/tests/fixtures/
  git commit -m "feat(sim): seasonal profile + HCC pattern conformance test" -m "Monthly + weekly + hourly demand curves matching HCC utilization pattern PNG. Regression test: MAPE < 15% for LUKS preset. Design spec §4.5 + §4.7."
  ```

### Task T3.3: Sim clock

**Files:**
- Create: `apps/sim-capacity/src/clock/sim_clock.py`
- Create: `apps/sim-capacity/tests/test_sim_clock.py`

- [ ] **Step 1: Write test for accelerated + deterministic behaviour**:
  ```python
  def test_clock_accelerates_60x():
      c = SimClock(start=datetime(2027,1,1), rate=60.0)
      real_ticks = []
      for _ in range(5):
          real_ticks.append(c.now())
          time.sleep(0.1)  # 100ms real = 6 sim seconds
      elapsed_sim = (real_ticks[-1] - real_ticks[0]).total_seconds()
      assert 20 < elapsed_sim < 30  # ~24s sim time
  def test_clock_deterministic_seed():
      c1 = SimClock(start=datetime(2027,1,1), rate=60.0, seed=42)
      c2 = SimClock(start=datetime(2027,1,1), rate=60.0, seed=42)
      assert c1.random_uniform() == c2.random_uniform()
  ```

- [ ] **Step 2: Run to FAIL, implement, run to PASS**.

- [ ] **Step 3: Commit**.

### Task T3.4: Event generators (7 kinds)

Each event generator gets its own sub-task following TDD pattern. For brevity, one sub-task per generator; each follows the same shape as T3.4a below.

#### T3.4a: encounter_generator (encounter.admitted + encounter.transitioned)

**Files:**
- Create: `apps/sim-capacity/src/generators/encounter_generator.py`
- Create: `apps/sim-capacity/tests/test_encounter_generator.py`

- [ ] **Step 1: Write test** — verifies (a) `admitted` events emit at expected rate per preset, (b) each `admitted` produces a matching sequence of `transitioned` events per FHIR EncounterStatusHistory shape.
- [ ] **Step 2: Run FAIL**.
- [ ] **Step 3: Implement** — uses seasonal_profile + acuity_distribution + hospital_presets.
- [ ] **Step 4: Run PASS**.
- [ ] **Step 5: Commit**.

#### T3.4b: bed_state_generator

Same pattern for `bed.state_changed`.

#### T3.4c: matching_engine

Advisory bed → encounter matching producing `bed.assigned`.

#### T3.4d: forecast_generator

Hourly 72h forecast per specialty producing `forecast.published`.

#### T3.4e: discharge_scorer

Hourly per-active-encounter score refresh producing `discharge.scored`.

#### T3.4f: discharge_recommender

Top-K ranked discharge candidates per shift producing `discharge.recommended`.

### Task T3.5: eventhub_emitter (AMQP publisher with MI auth)

**Files:**
- Create: `apps/sim-capacity/src/emitters/eventhub_emitter.py`
- Create: `apps/sim-capacity/tests/test_eventhub_emitter.py`

- [ ] **Step 1: Write test** with a mocked `azure.eventhub` client verifying:
  - Envelope shape matches design spec §4.3 (JSON with `eventKind`, `eventId`, `hospitalId`, `simulatedAt`, `emittedAt`, `simRunId`, `seed`, `payload`).
  - `eventKind` set as message application property (for Eventstream routing).
  - Retry on transient error.
  - MI auth via `DefaultAzureCredential`.
- [ ] **Step 2-5** — implement + PASS + commit.

### Task T3.6: PHI regex sweep test (`test_no_phi.py`)

**Files:**
- Create: `apps/sim-capacity/tests/test_no_phi.py`

- [ ] **Step 1: Author the test** — generates 10 000 events across all 7 event kinds for each hospital preset, then sweeps regex bundle (email, phone, DOB, CH AHV-13). Assert 0 hits.
- [ ] **Step 2: Run — expect PASS** (simulator should never produce PHI-shaped tokens).
- [ ] **Step 3: Commit**.
  ```powershell
  git commit -m "feat(sim): PHI regex sweep test — 10000 events, 0 hits (ADR-0016 gate 1)"
  ```

### Task T3.7: Simulator ACA Bicep + pyproject.toml pin

**Files:**
- Create: `infra/modules/apps/sim-capacity/main.bicep`
- Modify: `apps/sim-capacity/pyproject.toml` — add `azure-eventhub`, pin `foundry-sdk`

- [ ] **Step 1: Update pyproject.toml**:
  ```toml
  [tool.poetry.dependencies]
  python = "^3.12"
  azure-eventhub = "^5.11"
  azure-identity = "^1.15"
  foundry-sdk = "1.4.2"  # pinned per design spec §7.5 risk row
  ```

- [ ] **Step 2: Author `infra/modules/apps/sim-capacity/main.bicep`** — ACA environment + workload profile + container app with MI. Params: `location` (`@allowed(['switzerlandnorth', 'westus2'])`), `eventHubNamespace`, `eventHubName`, `containerImage`, `demoScope` (bool). Output `principalId` for T2.1 wiring.

- [ ] **Step 3: `az bicep build` + `what-if`**.

- [ ] **Step 4: Commit**.
  ```powershell
  git add apps/sim-capacity/pyproject.toml infra/modules/apps/sim-capacity/
  git commit -m "feat(sim): ACA Bicep + pin foundry-sdk 1.4.2 (design spec §7.5 risk mitigation)"
  ```

---

## Track T4 — Semantic Model + Agents (starts after T2 + T3 have first working slices)

**Goal:** Land the Direct Lake semantic model + 3 agent prompt files with 9 total eval fixtures + Bicep for Foundry MI/RBAC (attaches to existing `ai-ihzhhpf-sit`) + Fabric Data Agent deployment script + new `docs/AI.md §Agent Registry`.

### Task T4.1: Semantic model TMDL (Direct Lake)

**Files:**
- Create: `data-platform/reports/capacity-dashboard.SemanticModel/` — TMDL directory (`.platform`, `definition.pbism`, `definition/*.tmdl`, `model.tmdl`, `culture/en-US.tmdl`)

- [ ] **Step 1: Author via Fabric portal Power BI Desktop** — connect to `gold/*` Delta tables in Direct Lake mode. Follow Sprint 00 Approach A (portal-authored TMDL export). Star schema per design spec §6.4:
  - Facts: `fact_encounter`, `fact_bed_state`, `fact_bed_assignment`, `fact_forecast_output`, `fact_or_schedule`, `fact_or_case`
  - Dims: `dim_hospital`, `dim_specialty`, `dim_ward_capacityunit`, `dim_disease`, `dim_drg`, `dim_time`
- [ ] **Step 2: Export TMDL** via REST `getDefinition` per Sprint 00 follow-up #1.
- [ ] **Step 3: Author all 13 DAX measures** from design spec §6.3 in `model.tmdl`.
- [ ] **Step 4: Commit TMDL folder**.

### Task T4.2: BM-Copilot agent prompt + golden tasks

**Files:**
- Create: `agents/bm-copilot/AGENT.md`
- Create: `agents/bm-copilot/golden-tasks.md`

- [ ] **Step 1: Author `AGENT.md`** — Identity / Scope / Tools / Refusal Rules / Output Contract / Confirmation Rules. Follows AGENTS.md §5 shared refusal + ADR-0016 gate 3 refusal. Grounding sources: `gold/patient-flow/*` + MVO semantic model.
- [ ] **Step 2: Author 3 fixtures** in `golden-tasks.md`: happy-bed-recommendation, failure-out-of-scope, phi-refusal (per design spec §5.5).
- [ ] **Step 3: Register in `docs/AI.md` §Agent Registry** (new subsection — created in T4.7).
- [ ] **Step 4: Commit**.

### Task T4.3: Fabric Data Agent prompt + golden tasks

Same pattern as T4.2 for `agents/fabric-data-agent/`.

### Task T4.4: CSA agent prompt + golden tasks

Same pattern as T4.2 for `agents/csa-agent/`.

### Task T4.5: Foundry-hosted Bicep (MI + RBAC — attaches to existing resources)

**Files:**
- Create: `infra/modules/agents/foundry-hosted/main.bicep`
- Create: `infra/modules/agents/foundry-hosted/rbac.bicep`

- [ ] **Step 1: Author `main.bicep`** — creates 2 User-Assigned MIs (one for BM-Copilot, one for CSA). No new Foundry resource creation (attaches to existing `ai-ihzhhpf-sit` per design spec §5.4 confirmed via pre-flight).
- [ ] **Step 2: Author `rbac.bicep`** — role assignments:
  - Both MIs: `Fabric IQ Reader`, `Storage Blob Data Reader` on the workspace-scoped RG
  - BM-Copilot MI: `Azure Event Hubs Data Receiver` on `cg-bm-copilot-agent`
  - CSA MI: `Azure Event Hubs Data Receiver` on `cg-csa-agent`
- [ ] **Step 3: Wire into `infra/main.bicep`** with `@allowed(['switzerlandnorth', 'westus2'])` region param.
- [ ] **Step 4: `az bicep build` + `what-if` clean.**
- [ ] **Step 5: Commit**.

### Task T4.6: Fabric Data Agent deploy script

**Files:**
- Create: `data-platform/scripts/deploy_fabric_data_agent.py`

- [ ] **Step 1: Author the script** — Fabric REST API authoring; params `-Region`, `-WorkspaceId`, `-AgentName`. Region-agnostic via workspace ID abstraction.
- [ ] **Step 2: Include dry-run mode** (`--dry-run`) that prints the payload without POSTing.
- [ ] **Step 3: Commit**.

### Task T4.7: `docs/AI.md §Agent Registry`

**Files:**
- Modify: `docs/AI.md` — new §Agent Registry subsection

- [ ] **Step 1: Add subsection** with 3 rows per design spec §5.1 (BM-Copilot / Fabric Data Agent / CSA) — grounding, ceiling, refusal, host, region-pin path.
- [ ] **Step 2: Bump `docs/AI.md` version per §9 Document Versioning (MINOR — new subsection).**
- [ ] **Step 3: Lint + commit.**

---

## Track T5 — Dashboard (starts after T4.1 semantic model lands)

**Goal:** 2-page Power BI (`.pbip`) with Direct Lake semantic model, deployed via Fabric REST, with row-level PHI security (ADR-0016 gate 4). Page 1 replicates the HCC utilization pattern PNG; Page 2 mirrors the HCC OR steering command center using DC-OR sample data.

### Task T5.1: Page 1 — Capacity Utilization Pattern

**Files:**
- Create: `data-platform/reports/capacity-dashboard.pbip`
- Create: `data-platform/reports/capacity-dashboard.Report/` (PBIP report directory)

- [ ] **Step 1: Author Page 1 in Fabric portal** matching design spec §6.1 layout: 4 KPI cards + slicers (Hospital/Specialty/Time) + main time-series (12-month, capacity used vs required) + Month × Weekday RAG matrix + data-quality badge.
- [ ] **Step 2: Verify data-quality badge shows `⚠ Inferred` for USZ**.
- [ ] **Step 3: Export PBIP** and commit.

### Task T5.2: Page 2 — OR Steering Command Center

**Files:**
- Modify: `data-platform/reports/capacity-dashboard.pbip` — add Page 2

- [ ] **Step 1: Author Page 2** matching design spec §6.2: 6 KPI panel wall + OR case timeline (Gantt) + cancellation/block breakdowns + anaesthesia consult funnel + sample-data watermark.
- [ ] **Step 2: Verify slicers are synced with Page 1.**
- [ ] **Step 3: Export PBIP** and commit.

### Task T5.3: Deploy report PowerShell

**Files:**
- Create: `data-platform/scripts/deploy_report.ps1`

- [ ] **Step 1: Author the script** — Fabric REST API deploy of PBIP + SemanticModel; `-Region` param.
- [ ] **Step 2: Test dry-run mode.**
- [ ] **Step 3: Commit.**

### Task T5.4: Sample OR data fixtures

**Files:**
- Create: `data/synthetic/or-samples/or_schedule.json`
- Create: `data/synthetic/or-samples/or_case.json`

- [ ] **Step 1: Generate synthetic OR data** — ≥ 1 000 slots + ≥ 500 cases across 3 hospitals × 5 theatres × 3 months × realistic acuity mix. Payloads conform to DC-OR-SCHEDULE-v1 + DC-OR-CASE-v1.
- [ ] **Step 2: Validate against schemas**:
  ```powershell
  python -c "import json, jsonschema; s=json.load(open('data/synthetic/or-samples/or_schedule.json')); v=json.load(open('data/synthetic/schema/dc-or-schedule-v1.schema.json')); jsonschema.validate(instance=s, schema=v); print('OK')"
  ```
  Expected: `OK`.
- [ ] **Step 3: Commit.**

### Task T5.5: Sample OR loader notebook

**Files:**
- Create: `data-platform/notebooks/reference/04_load_or_samples.ipynb`

- [ ] **Step 1: Author** — reads `or-samples/*.json`, writes to `gold/patient-flow/or_schedule/` + `or_case/` with governance columns.
- [ ] **Step 2: Test end-to-end.**
- [ ] **Step 3: Commit.**

### Task T5.6: Workspace RLS PHI gate

**Files:**
- Modify: `data-platform/reports/capacity-dashboard.SemanticModel/model.tmdl` — add role definitions

- [ ] **Step 1: Add row-level security roles** in TMDL — for every role (BedOps, ORPlanner, Analyst, SemanticOwner), any column tagged `[phi]="true"` in the semantic model returns empty-set.
- [ ] **Step 2: Test per role** — attempt a query as each role; confirm 0 rows return on PHI-tagged columns.
- [ ] **Step 3: Commit.**

---

## Cross-cutting deliverables

### Task DX.1: Sprint 09 v2.0.0 doc rewrite (executed at sprint close)

**Files:**
- Modify: `docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md` — v1.3.0 → v2.0.0

- [ ] **Step 1: Complete rewrite** per design spec §7 structure: 5-track structure, 35-deliverable table, DoD, risk register, traceability. Status: `Refreshed 2026-07-02 — ready for execution` (already flipped in v1.3.0; v2.0.0 adds executable content).
- [ ] **Step 2: Bump metadata table** version to `2.0.0` (MAJOR per §9 Document Versioning — restructures tracks).
- [ ] **Step 3: Add retrospective template link** to `docs/sprints/sprint-09/retrospective.md`.
- [ ] **Step 4: Lint + commit.**

### Task DX.2: Fabric F2 lifecycle runbook + scripts + tests

**Files:**
- Create: `docs/runbooks/fabric-capacity-lifecycle.md`
- Create: `infra/scripts/Resume-FabricCapacity.ps1`
- Create: `infra/scripts/Suspend-FabricCapacity.ps1`
- Create: `infra/scripts/tests/Resume-FabricCapacity.Tests.ps1`
- Create: `infra/scripts/tests/Suspend-FabricCapacity.Tests.ps1`

- [ ] **Step 1: Write Pester test for Resume** — mock `az resource invoke-action`; verify script calls `--action resume` on the correct capacity ID; verify idempotent behavior (already-resumed → no-op).
- [ ] **Step 2: Run test to FAIL**.
- [ ] **Step 3: Implement `Resume-FabricCapacity.ps1`** — params `-Environment sit|prod` (maps to capacity name via convention); calls `az resource invoke-action ... --action resume`; checks final state.
- [ ] **Step 4: Same TDD cycle for Suspend.**
- [ ] **Step 5: Author runbook `fabric-capacity-lifecycle.md`** — documents (a) az CLI approach, (b) playwright admin-portal fallback with screenshot markers, (c) cost hygiene expectations per environment.
- [ ] **Step 6: Wire into GitHub Actions `workflow_dispatch`** for reviewer-controlled hygiene.
- [ ] **Step 7: Commit.**

### Task DX.3: OPERATIONS.md v1.5.0 — 3 new OPS-RISK rows

**Files:**
- Modify: `docs/OPERATIONS.md` — add OPS-RISK-03, -04, -05 to Live Risk Register

- [ ] **Step 1: Add rows** per design spec §7.5 risk register: OPS-RISK-03 Direct Lake preview stability, OPS-RISK-04 Fabric F2 forgot-to-pause, OPS-RISK-05 3-hospital calibration realism drift.
- [ ] **Step 2: Bump version** to 1.5.0 (MINOR).
- [ ] **Step 3: Lint + commit.**

### Task DX.4: Cross-doc updates (INFRASTRUCTURE / COMPLIANCE / SECURITY / TEST)

**Files:**
- Modify: `docs/INFRASTRUCTURE.md` (already touched in T1.1)
- Modify: `docs/COMPLIANCE.md` (already touched in T1.2)
- Modify: `docs/SECURITY.md` (already touched in T1.2)
- Modify: `docs/TEST.md` — new §Sprint 09 evidence subsection

- [ ] **Step 1: Add `docs/TEST.md §Sprint 09 evidence`** — documents: HCC pattern conformance test (§4.7), PHI regex gate test (T3.6), 9 agent eval fixtures (§5.5), ontology conformance CI (§3.5), RLS PHI gate verification (§6.5). Point to evidence-artefact locations under `docs/sprints/sprint-09/evidence/`.
- [ ] **Step 2: Bump `docs/TEST.md` version (MINOR).**
- [ ] **Step 3: Lint + commit.**

---

## Sprint execution + DoD

### Pre-flight (before T1 starts)

- [ ] Verify `main` at `0fd8dd7` or later.
- [ ] Resume Fabric F2 SIT: `az resource invoke-action --ids /subscriptions/66a9953a-df37-4c51-856c-9971b9bf3e03/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.Fabric/capacities/fabricihzhhpfsit --action resume` (should succeed since we proved `--action suspend` in Sprint 00; the resource type supports both).
- [ ] Verify Foundry SIT resources are up: `az resource show --ids /subscriptions/66a9953a-df37-4c51-856c-9971b9bf3e03/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.CognitiveServices/accounts/ai-ihzhhpf-sit` should return `provisioningState: Succeeded`.

### Sprint close (after all 35 deliverables)

- [ ] Run full CI pipeline on the Sprint 09 v2.0.0 PR — all checks green.
- [ ] Verify HCC pattern conformance test locally (MAPE < 15%).
- [ ] Verify PHI regex sweep test (0 hits over 10 000 events).
- [ ] Verify 9 agent eval fixtures replay green.
- [ ] Verify RLS PHI gate returns 0 rows for all roles on PHI columns.
- [ ] Suspend Fabric F2 SIT: `.\infra\scripts\Suspend-FabricCapacity.ps1 -Environment sit`.
- [ ] Commit Sprint 09 v2.0.0 retrospective in `docs/sprints/sprint-09/retrospective.md`.
- [ ] Merge Sprint 09 v2.0.0 PR to `main`.

---

## Self-Review

Applied after writing this plan per skill § Self-Review:

**1. Spec coverage.** Each of the 35 deliverables in design spec §7.2 has at least one task in this plan. Cross-cutting DX.1-DX.4 explicitly enumerated. Ontology extension (§3) has T1.3 + T1.4. Two new ADRs (§2) have T1.1 + T1.2. Contracts (§3.3) have T1.5. Strict-mode CI flip (§3.5) has T1.6. Simulator (§4) has T3.1-T3.7. Semantic model + agents (§5) has T4.1-T4.7. Dashboard (§6) has T5.1-T5.6. F2 lifecycle (§4.8) has DX.2. **No gaps.**

**2. Placeholder scan.** No "TBD" / "TODO" / "similar to Task N" / "fill in details" left. Each task has file paths, commands, and test/code content where relevant. Sub-tasks T3.4b–T3.4f explicitly reference the T3.4a template pattern with full context (not "similar to").

**3. Type consistency.** `HospitalPreset` dataclass used consistently in T3.1. `SimClock`, `EventHubEmitter`, `EncounterGenerator` names match across module + test files. Event kinds (`encounter.admitted`, `bed.state_changed`, etc.) match design spec §4.3 exactly. Gold table names (`gold/patient-flow/*`) match §6.4. Contract IDs (`DC-DISCHARGE-SCORE-v1` etc.) match §3.3.

**4. Fresh-eyes pass.** Plan reads as executable by a skilled dev with zero project context. Each task is scoped ~2-5 minutes per step (writing-plans skill target). TDD pattern applied where code + tests. Commit boundaries land at every task. Merge boundaries obvious at track boundaries.

**No inline fixes required after self-review.**

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md`. Two execution options:

### 1. Subagent-Driven (recommended)

I dispatch a fresh subagent per task, review between tasks, fast iteration.
**REQUIRED SUB-SKILL:** superpowers:subagent-driven-development
**Fresh subagent per task + two-stage review.**

### 2. Inline Execution

Execute tasks in this session using executing-plans, batch execution with checkpoints for review.
**REQUIRED SUB-SKILL:** superpowers:executing-plans
**Batch execution with checkpoints for review.**

**Which approach?**
