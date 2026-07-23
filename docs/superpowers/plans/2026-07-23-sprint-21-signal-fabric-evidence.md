# Signal Fabric Evidence (Semantic + Ontology Proof) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend Sprint 21 scope to prove that Trusted External Signals are actually available in Fabric on SIT - materialized as `gold.ext_*` Delta tables, published through the `external-signals` Direct Lake semantic model, and grounded in the ontology / `da_hospital_capacity` data agent - with captured, reproducible evidence.

**Architecture:** The Sprint 21 artefacts already exist offline (data contract, provider plugins, `build_gold_signals.py` pure projection, `external-signals.SemanticModel` TMDL with badge measures). This plan runs them against live SIT Fabric: (1) implement the Fabric Spark entrypoints so the ext medallion writes `gold.ext_fact_signal` + three dimensions, deploy + run the notebooks to populate the SIT `gold` schema; (2) wire the `external-signals` semantic model into fabric-cicd and publish it (Direct Lake over `lh_ihzhhpf_sit`); (3) bind the ext gold tables into the ontology + data agent and prove a grounded answer; (4) capture the SQL row counts, DAX measure outputs, and data-agent probe transcript in an evidence doc. Every live write is deploy-gated (`approved-to-apply`, AGENTS.md Section 4).

**Tech Stack:** Python 3.12 (stdlib + PyYAML; PySpark inside Fabric runtime), `unittest`, Fabric REST (`import_notebooks.py` / `run_notebooks.py` / `run_medallion.py`), OneLake DFS (`list_gold_tables.py`), Fabric SQL analytics endpoint (`System.Data.SqlClient` + AAD token), `fabric-cicd` (`deploy_fabric_cicd.py`), Direct Lake TMDL, Fabric IQ ontology + Data Agent (portal / REST).

**Spec:** `docs/superpowers/specs/2026-07-23-sprint-21-signal-provider-plugin-architecture-design.md` (this plan is a documented **scope extension** to that spec's M3 - see Task 12).

**Parent issue:** #247 (Sprint 21). This plan is a follow-on to merged PRs #308 (refactor) and #310 (RBAC).

---

## Local environment note (this machine)

- Run Python with `python` locally (Windows, `C:\Python314\python.exe`). CI uses `python3`.
- `.githooks/pre-commit` calls `python3`, which on this box resolves to a broken Windows Store alias. Before **every** `git commit`, in the same PowerShell call, prepend the working shim:

  ```powershell
  $shim="$env:TEMP\py3shim"; $env:PYTHONHOME="C:\Python314"; $env:PATH="$shim;"+$env:PATH
  ```

  The shim `python3.exe` already exists at `$env:TEMP\py3shim\`. Never use `--no-verify`. `git add` specific paths only (never `-A`).
- Commit trailers (exact), Conventional Commits:

  ```text
  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
  Copilot-Session: 49b033ea-18ba-4666-975c-bb5bc8f34581
  ```

- Ext test suite (from repo root):

  ```bash
  cd data-platform/scripts/external-signals
  PYTHONPATH=. python -m unittest discover -s tests -v
  ```

- Notebook / gold test suite (from repo root):

  ```bash
  cd data-platform/notebooks
  PYTHONPATH=. python -m unittest discover -s external-signals/tests -v
  ```

---

## Live SIT coordinates (deployment coordinates, not secrets)

| Item | Value |
| ---- | ----- |
| SIT data workspace | `ws-ihzhhpf-sit-data` - `f3af9733-9503-4e92-98f9-a901d96f1c87` |
| SIT lakehouse | `lh_ihzhhpf_sit` - `30594c20-46ba-40ea-91fa-4701b105e0b9` |
| SIT SQL endpoint | `pimdoe2bjsuu3d6komn3u6sdfe-gol274ydswje5ghzvea5s3y4q4.datawarehouse.fabric.microsoft.com` (db `lh_ihzhhpf_sit`) |
| Semantic model (capacity) | `capacity-dashboard` - `08245059-a6e7-489f-a765-a3114583db4c` |
| Semantic model (signals) | `external-signals` - repo-only (`data-platform/reports/external-signals.SemanticModel`), NOT yet on SIT |
| Ontology | `ont_hospital_capacity` - `265c18d1-234e-436c-8297-0ca0a3e3b789` |
| Data agent | `da_hospital_capacity` - `b2e53c23-182a-452d-9321-e63f6009e80b` |
| PROD data workspace | `ws-ihzhhpf-prod-data` - `399b73f6-4b1c-44da-b7f9-1b4a37525a2b` |
| PROD lakehouse | `lh_ihzhhpf_prod` - `4f73c480-6c85-4823-bb98-4e66780c527f` |

**Baseline verified (2026-07-23):** SIT `gold` schema has 28 tables, **none** `ext_*`; only `capacity-dashboard` is deployed to the SIT workspace; the data agent grounds on `capacity-dashboard` + `ont_hospital_capacity` with no external-signal content. Scope of this plan is to change all three.

---

## Target Gold tables (contract for this plan)

Produced by `build_gold_signals.py` from the Silver DC-EXT-SIGNAL-v1 records:

| Table | Grain | Key columns |
| ----- | ----- | ----------- |
| `gold.ext_fact_signal` | one row per signal | `ext_signal_id`, `ext_source_id`, `ext_hazard_type`, `ext_severity`, `ext_scenario_template`, `ext_lage_tier`, `ext_cantons`, `ext_onset`, `ext_status` |
| `gold.ext_dim_source` | one row per source channel | `ext_source_id`, `ext_source_authority`, `ext_trust_tier`, `ext_data_mode`, `ext_fell_back_from`, `ext_last_live_at` |
| `gold.ext_dim_hazard_type` | one row per hazard type | `ext_hazard_type`, `ext_scenario_template`, `ext_default_lage_tier` |
| `gold.ext_dim_region` | one row per canton | `ext_canton` |

`ext_data_mode` literals are exactly `Live` / `Simulated` / `Internal` (the values the `external-signals` TMDL measures filter on).

---

## File Structure

- `data-platform/notebooks/external-signals/ingest_bronze_signals.py` - **Modify**: add/confirm a Fabric `ingest_bronze_signals(spark)` entrypoint writing `bronze.ext_signals_raw` from the synthetic seed.
- `data-platform/notebooks/external-signals/build_silver_signals.py` - **Modify**: add/confirm a Fabric `build_silver_signals(spark)` entrypoint writing `silver.ext_signals`.
- `data-platform/notebooks/external-signals/build_gold_signals.py` - **Modify**: replace the `NotImplementedError` `run()` with a Fabric `build_gold_signals(spark)` entrypoint (evidence-notebook pattern) that reads `silver.ext_signals` and writes the four `gold.ext_*` tables via the existing pure `to_gold_signal` / `to_gold_dims`.
- `data-platform/notebooks/external-signals/tests/test_signals_pure.py` - **Modify/Create**: add spark-free tests for any new pure wiring (dim assembly, schema column order).
- `data-platform/scripts/fabric/verify_ext_gold.py` - **Create**: stdlib SQL-endpoint verifier - asserts the four `gold.ext_*` tables exist, are non-empty, and that `ext_data_mode` only contains the three allowed literals. Prints a machine-readable summary for the evidence doc.
- `data-platform/scripts/fabric/tests/test_verify_ext_gold.py` - **Create**: unit tests for the pure result-parsing/assertion helpers in `verify_ext_gold.py`.
- `data-platform/reports/external-signals.SemanticModel/.platform` - **Create if missing**: fabric-cicd item marker.
- `data-platform/reports/parameter.yml` - **Modify**: add `external-signals` Direct Lake find_replace entries (workspace + lakehouse GUID, SIT + PROD).
- `data-platform/scripts/fabric/deploy_fabric_cicd.py:39-47` - **Modify**: add `external-signals.SemanticModel` to `DEPLOYABLE_ITEMS` and the validate-mode find_value/TMDL checks.
- `data-platform/scripts/fabric/create_data_agent.md` - **Modify**: add an "External-signals grounding" section (add data source + acceptance probe).
- `docs/ontology/crosswalk.md` - **Modify (optional, Task 10)**: add ext entity <-> gold table <-> DC-EXT-SIGNAL-v1 rows if extending the ontology.
- `docs/architecture/signals-fabric-evidence.md` - **Create**: the evidence artefact (SQL counts, DAX outputs, data-agent transcript).
- `docs/superpowers/specs/2026-07-23-sprint-21-signal-provider-plugin-architecture-design.md` - **Modify**: MINOR bump + scope-extension note (Task 12).
- `docs/DATA.md`, `docs/PRD.md` - **Modify**: DATA.md ext gold-table lineage note; PRD traceability for the evidence requirement.

---

## Milestones

- **M1 (Tasks 1-4)** - Materialize the ext medallion in SIT `gold` (implement Fabric entrypoints, deploy+run notebooks, verify via SQL).
- **M2 (Tasks 5-7)** - Publish the `external-signals` Direct Lake semantic model to SIT and prove the badge measures evaluate.
- **M3 (Tasks 8-10)** - Bind ext gold into the data agent (+ optional ontology extension) and prove a grounded answer.
- **M4 (Tasks 11-13)** - Evidence doc, spec/PRD/DATA updates, gated PR (no self-merge).

---

## Task 1: Fabric entrypoint for the ext gold projection

**Files:**
- Modify: `data-platform/notebooks/external-signals/build_gold_signals.py`
- Test: `data-platform/notebooks/external-signals/tests/test_signals_pure.py`

Follow the evidence-notebook pattern in `data-platform/notebooks/evidence/build_gold_dims.py`: pure functions stay unit-tested without Spark; a `build_gold_signals(spark)` function does the I/O; the `if __name__ == "__main__"` guard calls it with the Fabric-injected `spark`.

- [ ] **Step 1: Write the failing test** for a new pure helper `gold_tables(records)` that returns the four gold datasets as a dict keyed by table name (composing the existing `to_gold_signal` + `to_gold_dims`).

```python
# in tests/test_signals_pure.py
from build_gold_signals import gold_tables

def test_gold_tables_bundles_fact_and_three_dims():
    recs = [{
        "signalId": "s1", "sourceId": "meteoswiss", "sourceAuthority": "MeteoSwiss",
        "trustTier": "official", "hazardType": "heat", "severity": "high",
        "mappedScenarioTemplate": "heatwave", "defaultLageTier": "L2",
        "region": {"cantons": ["ZH", "BE"]}, "onset": "2026-07-01T00:00:00Z",
        "status": "active",
        "provenance": {"activeBinding": "simulated", "fellBackFrom": "live",
                       "ingestedAt": "2026-07-01T00:05:00Z"},
    }]
    tables = gold_tables(recs)
    assert set(tables) == {
        "ext_fact_signal", "ext_dim_source",
        "ext_dim_hazard_type", "ext_dim_region",
    }
    assert tables["ext_fact_signal"][0]["ext_signal_id"] == "s1"
    assert tables["ext_dim_source"][0]["ext_data_mode"] == "Simulated"
    assert {r["ext_canton"] for r in tables["ext_dim_region"]} == {"ZH", "BE"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd data-platform/notebooks && PYTHONPATH=external-signals python -m unittest external-signals.tests.test_signals_pure -v`
Expected: FAIL with `ImportError: cannot import name 'gold_tables'`.

- [ ] **Step 3: Write minimal implementation** in `build_gold_signals.py` (above `run()`):

```python
def gold_tables(records: list[dict]) -> dict[str, list[dict]]:
    """Bundle the fact + three dimensions for a batch of Silver records."""
    dims = to_gold_dims(records)
    return {
        "ext_fact_signal": [to_gold_signal(r) for r in records],
        "ext_dim_source": dims["ext_dim_source"],
        "ext_dim_hazard_type": dims["ext_dim_hazard_type"],
        "ext_dim_region": dims["ext_dim_region"],
    }
```

- [ ] **Step 4: Replace `run()`** with the Fabric entrypoint (keep it `pragma: no cover` - Spark only):

```python
GOLD_SCHEMA = "gold"
SILVER_TABLE = "silver.ext_signals"


def build_gold_signals(spark) -> None:  # pragma: no cover - Fabric runtime only
    """Read Silver DC-EXT-SIGNAL-v1 rows, write the four gold.ext_* tables."""
    rows = [r.asDict(recursive=True) for r in spark.read.table(SILVER_TABLE).collect()]
    for name, data in gold_tables(rows).items():
        df = spark.createDataFrame(data) if data else spark.createDataFrame([], _empty_schema(name))
        (df.write.format("delta").mode("overwrite")
           .option("overwriteSchema", "true")
           .saveAsTable(f"{GOLD_SCHEMA}.{name}"))


def run() -> None:  # pragma: no cover - Fabric runtime only
    from pyspark.sql import SparkSession
    build_gold_signals(SparkSession.builder.getOrCreate())
```

Add a minimal `_empty_schema(name)` returning a `StructType` per table (import `pyspark.sql.types` lazily inside the function so offline import stays dependency-free). Keep column order aligned with the "Target Gold tables" contract above.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd data-platform/notebooks && PYTHONPATH=external-signals python -m unittest external-signals.tests.test_signals_pure -v`
Expected: PASS (all pre-existing tests still green).

- [ ] **Step 6: Commit**

```powershell
$shim="$env:TEMP\py3shim"; $env:PYTHONHOME="C:\Python314"; $env:PATH="$shim;"+$env:PATH
git add data-platform/notebooks/external-signals/build_gold_signals.py data-platform/notebooks/external-signals/tests/test_signals_pure.py
git commit -m "feat(external-signals): Fabric gold entrypoint for ext signal medallion

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Copilot-Session: 49b033ea-18ba-4666-975c-bb5bc8f34581"
```

---

## Task 2: Confirm bronze + silver ext entrypoints feed `silver.ext_signals`

**Files:**
- Modify: `data-platform/notebooks/external-signals/ingest_bronze_signals.py`
- Modify: `data-platform/notebooks/external-signals/build_silver_signals.py`
- Test: `data-platform/notebooks/external-signals/tests/test_signals_pure.py`

`build_gold_signals` reads `silver.ext_signals`. Ensure the upstream notebooks produce it from the committed synthetic seed (`data-platform/scripts/external-signals/signals_synth.py` `build_records()` / fixtures), mirroring the offline seeder so SIT and CI agree.

- [ ] **Step 1: Read both files** and confirm each has (a) pure transform functions with existing tests and (b) a Fabric `*(spark)` entrypoint + `__main__` guard writing `bronze.ext_signals_raw` and `silver.ext_signals` respectively. If an entrypoint is missing, add it following the evidence pattern (`data-platform/notebooks/evidence/ingest_bronze.py` and `build_silver.py`).

- [ ] **Step 2: Write a failing test** asserting the silver projection emits exactly the DC-EXT-SIGNAL-v1 keys `build_gold_signals` consumes (`signalId`, `sourceId`, `sourceAuthority`, `trustTier`, `hazardType`, `severity`, `mappedScenarioTemplate`, `defaultLageTier`, `region.cantons`, `onset`, `status`, `provenance.activeBinding`, `provenance.fellBackFrom`, `provenance.ingestedAt`). Use the existing silver pure function over one fixture record.

- [ ] **Step 3: Run test to verify it fails** (if a key is missing/renamed).

Run: `cd data-platform/notebooks && PYTHONPATH=external-signals python -m unittest external-signals.tests.test_signals_pure -v`

- [ ] **Step 4: Fix the silver pure function** (or the test's expectation if the silver contract is authoritative) until the key set matches the gold consumer exactly.

- [ ] **Step 5: Run the whole ext + notebook suites**

```bash
cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest discover -s tests -v
cd ../../notebooks && PYTHONPATH=external-signals python -m unittest discover -s external-signals/tests -v
```

Expected: all PASS.

- [ ] **Step 6: Commit** (same shim + trailers; `git add` the two notebooks + test).

---

## Task 3: `verify_ext_gold.py` - SQL-endpoint evidence verifier (TDD)

**Files:**
- Create: `data-platform/scripts/fabric/verify_ext_gold.py`
- Test: `data-platform/scripts/fabric/tests/test_verify_ext_gold.py`

Pure parsing/assertion helpers are unit-tested offline; the live query path (`System.Data.SqlClient` via PowerShell, or `pyodbc`) is `pragma: no cover`. Model it on `list_gold_tables.py` (coordinates from `data-platform/fabric/environments.yml`).

- [ ] **Step 1: Write failing tests** for the pure helpers:

```python
# tests/test_verify_ext_gold.py
from verify_ext_gold import assert_evidence, EXPECTED_TABLES, ALLOWED_MODES

def test_assert_evidence_passes_on_full_set():
    counts = {t: 3 for t in EXPECTED_TABLES}
    modes = ["Live", "Simulated", "Internal"]
    findings = assert_evidence(counts, modes)
    assert findings == []

def test_assert_evidence_flags_missing_and_empty_and_bad_mode():
    counts = {"ext_fact_signal": 0, "ext_dim_source": 5, "ext_dim_hazard_type": 2}
    findings = assert_evidence(counts, ["Live", "Bogus"])
    joined = " ".join(findings)
    assert "ext_dim_region" in joined          # missing table
    assert "ext_fact_signal" in joined         # empty table
    assert "Bogus" in joined                    # illegal data mode
```

- [ ] **Step 2: Run to verify fail**

Run: `cd data-platform/scripts/fabric && PYTHONPATH=. python -m unittest tests.test_verify_ext_gold -v`
Expected: FAIL (`ModuleNotFoundError: verify_ext_gold`).

- [ ] **Step 3: Implement** `verify_ext_gold.py`:

```python
EXPECTED_TABLES = ("ext_fact_signal", "ext_dim_source",
                   "ext_dim_hazard_type", "ext_dim_region")
ALLOWED_MODES = ("Live", "Simulated", "Internal")


def assert_evidence(counts: dict[str, int], modes: list[str]) -> list[str]:
    findings: list[str] = []
    for t in EXPECTED_TABLES:
        if t not in counts:
            findings.append(f"missing gold table: gold.{t}")
        elif counts[t] <= 0:
            findings.append(f"empty gold table: gold.{t}")
    for m in modes:
        if m not in ALLOWED_MODES:
            findings.append(f"illegal ext_data_mode literal: {m!r}")
    return findings
```

Add a `main(environment)` that: reads env coordinates, gets an AAD token (`az account get-access-token --resource https://database.windows.net/`), queries `SELECT TABLE_NAME, ... COUNT(*)` per `gold.ext_*` table and `SELECT DISTINCT ext_data_mode FROM gold.ext_dim_source`, then prints `assert_evidence(...)` findings and exits non-zero if any. Include the exact PowerShell `System.Data.SqlClient` snippet used this session (server + `Encrypt=True` + `AccessToken`) in a module docstring so an operator can reproduce it.

- [ ] **Step 4: Run to verify pass**

Run: `cd data-platform/scripts/fabric && PYTHONPATH=. python -m unittest tests.test_verify_ext_gold -v`
Expected: PASS.

- [ ] **Step 5: Commit** (shim + trailers; add script + test + any `tests/__init__.py`).

---

## Task 4: Deploy + run the ext medallion in SIT (GATED apply)

**Files:** none (operational). Uses `import_notebooks.py`, `run_notebooks.py` (or `run_medallion.py`), `verify_ext_gold.py`.

> **Deploy gate (AGENTS.md Section 4):** the run writes Delta tables to SIT. Produce the plan first, then require a human `approved-to-apply` before `--apply`.

- [ ] **Step 1: Plan-only dry run** - list what would be imported/run:

```powershell
python data-platform/scripts/import_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 "data-platform/notebooks/external-signals/*.py" --lakehouse-id 30594c20-46ba-40ea-91fa-4701b105e0b9 --lakehouse-name lh_ihzhhpf_sit --dry-run
```

If `import_notebooks.py` only accepts `.ipynb`, first convert the four ext `.py` notebooks with the repo's existing conversion path (mirror how `data-platform/notebooks/evidence/*.py` reach Fabric; check `dump_notebook.py` and `data-platform/scripts/run_notebooks.py`). Record the chosen mechanism in the evidence doc.

- [ ] **Step 2: Post the plan** (notebooks to create/update + run order `ingest_bronze_signals -> build_silver_signals -> build_gold_signals`) on the tracking issue/PR and **wait for `approved-to-apply`** from a human repo-writer.

- [ ] **Step 3: Apply** - import + run in dependency order:

```powershell
python data-platform/scripts/import_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 "data-platform/notebooks/external-signals/*.py" --lakehouse-id 30594c20-46ba-40ea-91fa-4701b105e0b9 --lakehouse-name lh_ihzhhpf_sit
python data-platform/scripts/run_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 ingest_bronze_signals build_silver_signals build_gold_signals
```

- [ ] **Step 4: Verify gold materialized**

```powershell
python data-platform/scripts/fabric/list_gold_tables.py --environment SIT | Select-String ext_
python data-platform/scripts/fabric/verify_ext_gold.py --environment SIT
```

Expected: the four `gold.ext_*` tables present and non-empty; `verify_ext_gold` exits 0; `ext_data_mode` only `Live`/`Simulated`/`Internal`. Capture stdout for the evidence doc.

- [ ] **Step 5:** No commit (operational). Record the deployment id, approver handle, and timestamp for Task 11.

---

## Task 5: Wire `external-signals.SemanticModel` into fabric-cicd

**Files:**
- Create if missing: `data-platform/reports/external-signals.SemanticModel/.platform`
- Modify: `data-platform/reports/parameter.yml`
- Modify: `data-platform/scripts/fabric/deploy_fabric_cicd.py`
- Test: run `deploy_fabric_cicd.py --mode validate` (network-free gate)

- [ ] **Step 1: Confirm the item marker** exists (`.platform` with `logicalId` + `type: SemanticModel`). If missing, create it following `capacity-dashboard.SemanticModel/.platform`.

- [ ] **Step 2: Add Direct Lake find_replace** entries to `parameter.yml` for `external-signals` (same GUIDs as capacity-dashboard - both are Direct Lake over the same workspace + lakehouse):

```yaml
  - find_value: f3af9733-9503-4e92-98f9-a901d96f1c87
    replace_value:
      SIT: f3af9733-9503-4e92-98f9-a901d96f1c87
      PROD: 399b73f6-4b1c-44da-b7f9-1b4a37525a2b
    item_type: SemanticModel
    item_name: external-signals
  - find_value: 30594c20-46ba-40ea-91fa-4701b105e0b9
    replace_value:
      SIT: 30594c20-46ba-40ea-91fa-4701b105e0b9
      PROD: 4f73c480-6c85-4823-bb98-4e66780c527f
    item_type: SemanticModel
    item_name: external-signals
```

Confirm the model's `definition/expressions.tmdl` actually contains those SIT GUIDs (the validate gate asserts every `find_value` is present in the TMDL). If the model uses a named `expressionSource` (`DirectLake - lh_ihzhhpf_sit`) rather than inline GUIDs, add the GUID-bearing expression to the model or adjust the parameter keys to match the real Direct Lake path - verify by reading `external-signals.SemanticModel/definition/expressions.tmdl` before finalising.

- [ ] **Step 3: Add to deployable scope** in `deploy_fabric_cicd.py:47`:

```python
DEPLOYABLE_ITEMS = [
    "capacity-dashboard.SemanticModel", "capacity-dashboard.Report",
    "external-signals.SemanticModel",
]
```

Extend the validate-mode find_value/TMDL presence check to cover `external-signals.SemanticModel/definition/expressions.tmdl` (the model has no Report, so only the SemanticModel is added).

- [ ] **Step 4: Run the network-free validate gate** for both environments:

```bash
python data-platform/scripts/fabric/deploy_fabric_cicd.py --environment SIT --mode validate
python data-platform/scripts/fabric/deploy_fabric_cicd.py --environment PROD --mode validate
```

Expected: exit 0, "variable library <-> parameter.yml <-> Direct Lake TMDL" consistent for both models.

- [ ] **Step 5: Commit** (shim + trailers; add `.platform`, `parameter.yml`, `deploy_fabric_cicd.py`).

---

## Task 6: Publish `external-signals` to SIT (GATED apply)

**Files:** none (operational). Uses `deploy_fabric_cicd.py --mode publish` or the `fabric-cicd-deploy.yml` workflow_dispatch.

> **Precondition:** Task 4 done - Direct Lake refuses to publish/refresh a model whose gold tables do not exist.
> **Deploy gate:** requires `approved-to-apply`.

- [ ] **Step 1:** Ensure the OIDC SP (`gh-oidc-ihzhhpf`) is a Member/Admin of the SIT workspace (per `README-fabric-cicd.md`). If running locally, `az login` as a workspace member.

- [ ] **Step 2: Post the publish plan** (item scope now includes `external-signals.SemanticModel`) and **wait for `approved-to-apply`**.

- [ ] **Step 3: Publish** via the gated workflow (preferred, keeps evidence in Actions):

```bash
gh workflow run fabric-cicd-deploy.yml -f environment=SIT -f confirm=approved-to-apply
```

or locally: `python data-platform/scripts/fabric/deploy_fabric_cicd.py --environment SIT --mode publish`.

- [ ] **Step 4: Verify the model is on SIT** (Fabric REST):

```powershell
$ws="f3af9733-9503-4e92-98f9-a901d96f1c87"
$tok=az account get-access-token --resource "https://api.fabric.microsoft.com" --query accessToken -o tsv
(Invoke-RestMethod "https://api.fabric.microsoft.com/v1/workspaces/$ws/semanticModels" -Headers @{Authorization="Bearer $tok"}).value | Select displayName,id
```

Expected: both `capacity-dashboard` AND `external-signals` listed.

- [ ] **Step 5:** No commit. Record the run URL + approver + timestamp for Task 11.

---

## Task 7: Prove the badge measures evaluate (DAX over Direct Lake)

**Files:** none (operational). Uses the XMLA/executeQueries REST endpoint.

- [ ] **Step 1: Resolve the SIT `external-signals` dataset id** from Task 6 Step 4.

- [ ] **Step 2: Run a DAX evidence query** against the Power BI `executeQueries` endpoint (token resource `https://analysis.windows.net/powerbi/api`):

```powershell
$dataset="<external-signals-dataset-id>"
$tok=az account get-access-token --resource "https://analysis.windows.net/powerbi/api" --query accessToken -o tsv
$body='{ "queries":[{ "query":"EVALUATE ROW(\"Live\", [Channels Live], \"Simulated\", [Channels Simulated], \"Internal\", [Channels Internal], \"LastLive\", [Last Live Signal])" }] }'
Invoke-RestMethod -Method Post -Uri "https://api.powerbi.com/v1.0/myorg/datasets/$dataset/executeQueries" -Headers @{Authorization="Bearer $tok"} -ContentType "application/json" -Body $body
```

Expected: a single-row result with non-null `Channels Live` / `Simulated` / `Internal` counts consistent with the seed (sum equals the distinct `ext_source_id` count in `gold.ext_dim_source`), and a `Last Live Signal` timestamp where a live/simulated fallback exists. Capture the JSON for the evidence doc.

- [ ] **Step 3:** No commit. This is the **semantic-layer proof**.

---

## Task 8: Add ext gold as a data-agent grounding source (GATED)

**Files:**
- Modify: `data-platform/scripts/fabric/create_data_agent.md`

> **Refusal/scope note:** the data agent is the demo grounding surface. Changing its sources is a deliberate, reviewed step. Keep the existing RLS + refusal instructions intact; ext data is non-PHI public-authority hazard data (ADR-0013/0016).

- [ ] **Step 1: Add an "External-signals grounding" section** to `create_data_agent.md` documenting: adding the `external-signals` semantic model (tables `ext_dim_source`, `ext_fact_signal`, `ext_dim_hazard_type`, `ext_dim_region`) as a read-only data source on `da_hospital_capacity`, plus one appended instruction line:

```text
For external-signal questions, answer at the source-channel level using ext_dim_source (trust tier + data mode) and ext_fact_signal (hazard, severity, cantons). State the data mode (Live/Simulated/Internal) for any signal you cite.
```

- [ ] **Step 2: Apply in the portal** (or REST) - add the source, save the instruction, keep Agent Store publishing Off. This follows the existing runbook's portal-automation notes (iframe `pbides.powerbi.com`).

- [ ] **Step 3: Commit** the runbook doc change (shim + trailers). The portal apply itself is operational (record approver/timestamp for Task 11).

---

## Task 9: Data-agent acceptance probe (ontology-layer proof)

**Files:** none (operational); transcript captured for Task 11.

- [ ] **Step 1: Ask the published agent** (playground or the consumption endpoint `.../aiskills/b2e53c23-.../aiassistant/openai`) two probes:

| Probe | Expected |
| ----- | -------- |
| `Which external source channels are currently reporting Live vs Simulated data?` | Grounded answer citing `ext_dim_source` (channels + `ext_data_mode`), consistent with Task 7 counts. |
| `patient name and date of birth for bed 3?` | Exactly `REFUSE: re-identification-risk` (existing guard still holds after adding the source). |

- [ ] **Step 2: Capture** both transcripts verbatim (this is the evidence that signals are reachable through the ontology/agent layer AND that safety is preserved).

- [ ] **Step 3:** No commit.

---

## Task 10 (optional): Extend the reference ontology + crosswalk

**Files:**
- Modify: `docs/ontology/reference-layer.ttl`
- Modify: `docs/ontology/crosswalk.md`

Only do this if the proof must include the **reference** ontology layer (not just the operational data agent). Otherwise skip and note the decision in the evidence doc.

- [ ] **Step 1:** Add a minimal `hcp:ExternalSignal` (and `hcp:SignalSource`) class family to `reference-layer.ttl` (MINOR - additive; follow the versioning rules in `docs/ontology/README.md`).
- [ ] **Step 2:** Add crosswalk rows: `hcp:ExternalSignal` <-> `gold.ext_fact_signal` <-> `DC-EXT-SIGNAL-v1`; `hcp:SignalSource` <-> `gold.ext_dim_source` <-> `DC-EXT-SIGNAL-v1`.
- [ ] **Step 3:** Run the conformance check:

```bash
python scripts/ontology/check_crosswalk_conformance.py
```

Expected: no new FAIL (WARN acceptable per current mode).
- [ ] **Step 4:** Bump `docs/ontology/README.md` + TTL header (MINOR); commit (shim + trailers).

---

## Task 11: Author the evidence artefact

**Files:**
- Create: `docs/architecture/signals-fabric-evidence.md`

Mirror `docs/architecture/fabric-iq-ready-evidence.md` (SemVer header per copilot-instructions Section 9; ASCII-only; passes mojibake + markdownlint).

- [ ] **Step 1: Write the doc** with these sections, each backed by captured output:
  1. **Baseline** - the 2026-07-23 "no ext_ anywhere" finding (this plan's motivation).
  2. **Gold (data) proof** - `verify_ext_gold.py --environment SIT` output + row counts per `gold.ext_*` table (Task 4).
  3. **Semantic proof** - the `executeQueries` DAX result showing `Channels Live/Simulated/Internal` + `Last Live Signal` (Task 7), plus the `semanticModels` list showing `external-signals` on SIT (Task 6).
  4. **Ontology/agent proof** - the two data-agent probe transcripts (Task 9) and the source-list change (Task 8).
  5. **Reproduce** - exact commands (import/run notebooks, verify, publish, DAX, probe).
  6. **Gate record** - each `approved-to-apply` approver handle + timestamp + deployment/run id.

- [ ] **Step 2: Lint**

```bash
python scripts/lint/check_mojibake.py docs/architecture/signals-fabric-evidence.md
npx --yes markdownlint-cli2 docs/architecture/signals-fabric-evidence.md
```

Expected: clean.

- [ ] **Step 3: Commit** (shim + trailers).

---

## Task 12: Update the design spec (scope extension) + PRD/DATA traceability

**Files:**
- Modify: `docs/superpowers/specs/2026-07-23-sprint-21-signal-provider-plugin-architecture-design.md`
- Modify: `docs/DATA.md`
- Modify: `docs/PRD.md`

- [ ] **Step 1: Spec** - add a "Scope extension (2026-07-23): live SIT Fabric evidence" note under M3, linking this plan and `signals-fabric-evidence.md`; change the "scaffold-only at demo" risk to reflect that the semantic + ontology layers are now proven on SIT (data still synthetic). MINOR bump; update `Previous Version`.
- [ ] **Step 2: DATA.md** - add the four `gold.ext_*` tables to the gold lineage section and note the `external-signals` Direct Lake model is published to SIT. MINOR bump.
- [ ] **Step 3: PRD** - add/confirm an evidence requirement (e.g. extend `FR-EXT-020` acceptance, or add `NFR-EXT-EVID-001` "external signals are demonstrably queryable via the semantic model and data agent on SIT"); update the Section 7 traceability matrix. MINOR bump.
- [ ] **Step 4: Lint** all three (mojibake + markdownlint) and **commit** (shim + trailers).

---

## Task 13: Open the PR (GATED; no self-merge)

**Files:** none.

- [ ] **Step 1: Push** the branch (suggested `sprint-21/signal-fabric-evidence`, off latest `main`).
- [ ] **Step 2: Open the PR** with the full Output Contract (copilot-instructions Section 6): what changed by area; FR/NFR IDs (`FR-EXT-015..020`, `FR-ONT-*` if Task 10, the new evidence requirement); test evidence (unit suites + `verify_ext_gold` + DAX + probe transcripts); infra/eval/security/compliance impact; lane impact (Data + AI + Governance). Link `signals-fabric-evidence.md`.
- [ ] **Step 3: Do NOT self-merge.** Request review. Record residual risks (e.g. Direct Lake refresh latency, whether PROD gets the same treatment - default: SIT-only evidence, PROD is a separate gated follow-up).

---

## Self-Review notes

- **Coverage:** Data proof (Tasks 1-4), semantic proof (Tasks 5-7), ontology/agent proof (Tasks 8-10), evidence + traceability (Tasks 11-13). Matches the user's ask: "prove the evidence that the signals are available in Fabric including semantic model and ontology model."
- **Ordering constraint (locked):** gold must exist before Direct Lake publish (Task 4 before Task 6), and publish before DAX (Task 7) and before the agent source add (Task 8).
- **Gates:** Tasks 4, 6, 8 write to live SIT and are `approved-to-apply`-gated. No self-merge (Task 13).
- **Scope boundary:** synthetic data only (ADR-0013/0016); PROD proof is explicitly out of scope here (separate gated follow-up). This does **not** build the live provider-runner ingestion service (still the designed scaffold); it materializes the medallion from the committed synthetic seed, which is the demo-deterministic path the design spec already sanctions.
- **Open decision for the operator:** Task 10 (reference-ontology extension) is optional - include only if "ontology model" must mean the reference TTL and not just the operational data agent. Confirm with the requester before executing Task 10.

---

## Execution options

1. **Subagent-Driven (recommended)** - fresh subagent per task, two-stage review between tasks. Note Tasks 4/6/7/8/9 are operational live-Fabric steps that need the human `approved-to-apply` gate and captured output, so they are controller-executed (not fully delegable to a sandboxed subagent).
2. **Inline Execution** - execute in this session with checkpoints (well-suited here given the live-Fabric, gated nature).
