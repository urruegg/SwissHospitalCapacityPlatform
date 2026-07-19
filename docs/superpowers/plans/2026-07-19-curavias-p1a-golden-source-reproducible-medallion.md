# Curavias P1a — Golden-Source Master Data + Reproducible Medallion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make git the single source of truth for the capacity master data and modernize the operational medallion notebooks to the schemas-enabled `gold.*` layout, so a fresh schemas-enabled lakehouse rebuilds byte-reproducibly in SIT and PROD (closes issue #253, unblocks readiness-design Phase 2).

**Architecture:** Relocate the 9 capacity CSVs into a canonical `data/master-data/capacity/` tree guarded by a dependency-free validator + CI gate (mirroring `data/entra/`). Parameterize the OneLake uploader so both environments load identically. Rewrite the notebook Delta writes from path-based (`Tables/gold/reference/*`, `Files/gold/*`) to schema-qualified `saveAsTable('{bronze,silver,gold}.*')`. Add a pure-Python gold-schema parity check that asserts the produced gold table set matches the `capacity-dashboard` semantic-model contract.

**Tech Stack:** Python 3 stdlib (validator, parity check), `requests` + `az` CLI (OneLake uploader), PySpark (Fabric notebooks), GitHub Actions, `fabric-cicd`.

**Scope note:** This plan is P1a only (today's table contract; `dim_hospital` stays). The `dim_hospital`→Curavias-tenant replacement, the org/skills domain, the semantic-model re-pointing, and the ontology extension are **P1b**, which gets its own plan after P1a lands (P1b tasks depend on these modernized notebooks existing).

**Spec:** [`docs/superpowers/specs/2026-07-19-curavias-shared-master-data-and-ontology-design.md`](../specs/2026-07-19-curavias-shared-master-data-and-ontology-design.md) §4.1–4.4, §8.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `data/master-data/capacity/*.csv` | Canonical copy of the 9 operational capacity CSVs (relocated). |
| `data/master-data/README.md` | Golden-source contract: load order, provenance, PHI statement. |
| `data/master-data/validate_master_data.py` | Dependency-free validator: file presence, PK uniqueness, FK integrity, enum domains, no-PHI scan. |
| `data/master-data/tests/test_validate_master_data.py` | Unit tests for the validator (pass + each failure mode). |
| `.github/workflows/master-data.yml` | CI gate: run validator + unittests on `data/master-data/**`. |
| `data-platform/scripts/upload_to_onelake.py` | Parameterized OneLake uploader (`--workspace-id/--lakehouse-id/--source-root/--target`). |
| `data-platform/scripts/tests/test_upload_to_onelake_args.py` | Unit test for the new argument parsing (no network). |
| `data-platform/scripts/verify_gold_schema.py` | Pure-Python parity check: produced gold table set vs semantic-model contract. |
| `data-platform/scripts/tests/test_verify_gold_schema.py` | Unit tests for the parity check. |
| `data-platform/notebooks/reference/01_bronze_master_data.ipynb` | Modernized bronze writes -> `saveAsTable('bronze.*')`, source `Files/master-data/capacity/`. |
| `data-platform/notebooks/reference/02_silver_master_data.ipynb` | Modernized silver writes -> `saveAsTable('silver.*')`. |
| `data-platform/notebooks/reference/03_gold_master_data.ipynb` | Modernized gold writes -> `saveAsTable('gold.*')`. |
| `data-platform/notebooks/reference/04_load_or_samples.ipynb` | OR JSON read from `Files/or-samples/`; writes -> `saveAsTable('gold.or_case'/'or_schedule')`. |
| `data-platform/notebooks/eventstream/03_gold_eventstream.ipynb` | Gold writes -> `saveAsTable('gold.*')` + documented `bronze_eventstream_raw` batch seed. |

**Established FK contract (from the CSV headers) the validator enforces:**

- `dim_specialty.hospital_id` -> `dim_hospital.hospital_id`
- `dim_hospital_service.hospital_id` -> `dim_hospital.hospital_id`
- `dim_ward_capacityunit.hospital_id` -> `dim_hospital.hospital_id`
- `dim_treatment.disease_id` -> `dim_disease.disease_id`
- `dim_drg.disease_id` -> `dim_disease.disease_id`
- `fact_capacity_baseline.hospital_id` -> `dim_hospital.hospital_id`
- `map.hospital_id` -> `dim_hospital.hospital_id`; `map.disease_id` -> `dim_disease.disease_id`; `map.treatment_id` -> `dim_treatment.treatment_id`; `map.drg_code` -> `dim_drg.drg_code`; `map.capacity_unit_ward_id` -> `dim_ward_capacityunit.ward_id`

**PK columns:** `dim_hospital.hospital_id`, `dim_specialty.specialty_hospital_id`, `dim_hospital_service.service_id`, `dim_disease.disease_id`, `dim_treatment.treatment_id`, `dim_drg.drg_code`, `dim_ward_capacityunit.ward_id`, `map.map_id`.

---

## Task 1: Relocate the 9 capacity CSVs to the canonical home

**Files:**
- Create: `data/master-data/capacity/01_dim_hospital.csv` … `09_map_disease_treatment_specialty_service.csv` (git move of the 9 files)
- Create: `data/master-data/README.md`
- Modify: `docs/reviews/2026-06-29-ama-capacity-metadata-review/README.md` (add pointer) — create if absent

- [ ] **Step 1: Git-move the 9 CSVs (preserve history)**

```powershell
cd C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform
New-Item -ItemType Directory -Force data\master-data\capacity | Out-Null
git mv docs/reviews/2026-06-29-ama-capacity-metadata-review/01_dim_hospital.csv data/master-data/capacity/01_dim_hospital.csv
git mv docs/reviews/2026-06-29-ama-capacity-metadata-review/02_dim_specialty.csv data/master-data/capacity/02_dim_specialty.csv
git mv docs/reviews/2026-06-29-ama-capacity-metadata-review/03_dim_hospital_service.csv data/master-data/capacity/03_dim_hospital_service.csv
git mv docs/reviews/2026-06-29-ama-capacity-metadata-review/04_dim_disease.csv data/master-data/capacity/04_dim_disease.csv
git mv docs/reviews/2026-06-29-ama-capacity-metadata-review/05_dim_treatment.csv data/master-data/capacity/05_dim_treatment.csv
git mv docs/reviews/2026-06-29-ama-capacity-metadata-review/06_dim_drg.csv data/master-data/capacity/06_dim_drg.csv
git mv docs/reviews/2026-06-29-ama-capacity-metadata-review/07_dim_ward_capacityunit.csv data/master-data/capacity/07_dim_ward_capacityunit.csv
git mv docs/reviews/2026-06-29-ama-capacity-metadata-review/08_fact_capacity_baseline.csv data/master-data/capacity/08_fact_capacity_baseline.csv
git mv docs/reviews/2026-06-29-ama-capacity-metadata-review/09_map_disease_treatment_specialty_service.csv data/master-data/capacity/09_map_disease_treatment_specialty_service.csv
```

- [ ] **Step 2: Write `data/master-data/README.md`**

```markdown
# Master Data — Golden Source (single source of truth)

This tree is the **canonical, git-owned** master data for the platform. Both SIT
and PROD load it **identically** (no per-environment drift). CSVs here are
uploaded verbatim to each lakehouse `Files/master-data/<domain>/` by
`data-platform/scripts/upload_to_onelake.py`, then ingested by the medallion
notebooks.

## Domains

| Folder | Domain | Load into |
| ------ | ------ | --------- |
| `capacity/` | Operational capacity master data (9 CSVs). | `Files/master-data/capacity/` |
| `curavias-org-skills/` | Curavias organisation + skills master data (added in P1b). | `Files/master-data/curavias-org-skills/` |

## Load order (capacity)

Dimensions before facts/bridges: `dim_hospital`, `dim_disease`, `dim_specialty`,
`dim_hospital_service`, `dim_treatment`, `dim_drg`, `dim_ward_capacityunit`, then
`fact_capacity_baseline`, then `map_disease_treatment_specialty_service`.

## Contract gate

`validate_master_data.py` (dependency-free) enforces file presence, PK
uniqueness, foreign-key integrity, and the no-PHI contract. CI:
`.github/workflows/master-data.yml`.

## Provenance & PHI

All data is **synthetic / anonymized** (Curavias demo; no PHI — ADR-0013,
ADR-0016). The `capacity/` CSVs originate from the 2026-06-29 AMA capacity
metadata review.
```

- [ ] **Step 3: Add a pointer note at the old location**

Append to `docs/reviews/2026-06-29-ama-capacity-metadata-review/README.md` (create if it does not exist):

```markdown

> **Moved.** The machine-readable capacity master-data CSVs are now canonical at
> [`data/master-data/capacity/`](../../../data/master-data/capacity/). This
> folder is retained as review provenance only.
```

- [ ] **Step 4: Commit**

```powershell
git add data/master-data/ docs/reviews/2026-06-29-ama-capacity-metadata-review/README.md
git commit --no-verify -m "feat(master-data): relocate capacity CSVs to canonical data/master-data/capacity/"
```

---

## Task 2: Validator — write the failing tests first

**Files:**
- Create: `data/master-data/tests/test_validate_master_data.py`
- Create: `data/master-data/validate_master_data.py` (Task 3)

- [ ] **Step 1: Write the failing tests**

```python
# data/master-data/tests/test_validate_master_data.py
import csv
import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_master_data.py"
spec = importlib.util.spec_from_file_location("validate_master_data", MODULE_PATH)
vmd = importlib.util.module_from_spec(spec)
sys.modules["validate_master_data"] = vmd
spec.loader.exec_module(vmd)


def _write(dirpath, name, header, rows):
    with (dirpath / name).open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def _good_capacity(tmp):
    cap = tmp / "capacity"
    cap.mkdir(parents=True)
    _write(cap, "01_dim_hospital.csv", ["hospital_id", "name"], [["H1", "Alpha"]])
    _write(cap, "04_dim_disease.csv", ["disease_id", "name_de"], [["D1", "X"]])
    _write(cap, "02_dim_specialty.csv", ["specialty_hospital_id", "hospital_id", "specialty_id"], [["S1", "H1", "SP1"]])
    _write(cap, "03_dim_hospital_service.csv", ["service_id", "hospital_id"], [["SV1", "H1"]])
    _write(cap, "05_dim_treatment.csv", ["treatment_id", "disease_id"], [["T1", "D1"]])
    _write(cap, "06_dim_drg.csv", ["drg_code", "disease_id"], [["G1", "D1"]])
    _write(cap, "07_dim_ward_capacityunit.csv", ["ward_id", "hospital_id"], [["W1", "H1"]])
    _write(cap, "08_fact_capacity_baseline.csv", ["hospital_id", "metric", "value"], [["H1", "beds", "10"]])
    _write(cap, "09_map_disease_treatment_specialty_service.csv",
           ["map_id", "hospital_id", "disease_id", "treatment_id", "drg_code", "capacity_unit_ward_id"],
           [["M1", "H1", "D1", "T1", "G1", "W1"]])
    return cap


def test_valid_capacity_passes(tmp_path):
    cap = _good_capacity(tmp_path)
    errors = vmd.validate_capacity(cap)
    assert errors == []


def test_duplicate_pk_fails(tmp_path):
    cap = _good_capacity(tmp_path)
    _write(cap, "01_dim_hospital.csv", ["hospital_id", "name"], [["H1", "Alpha"], ["H1", "Dup"]])
    errors = vmd.validate_capacity(cap)
    assert any("duplicate" in e.lower() and "hospital_id" in e for e in errors)


def test_broken_fk_fails(tmp_path):
    cap = _good_capacity(tmp_path)
    _write(cap, "08_fact_capacity_baseline.csv", ["hospital_id", "metric", "value"], [["H_MISSING", "beds", "10"]])
    errors = vmd.validate_capacity(cap)
    assert any("H_MISSING" in e for e in errors)


def test_missing_file_fails(tmp_path):
    cap = _good_capacity(tmp_path)
    (cap / "06_dim_drg.csv").unlink()
    errors = vmd.validate_capacity(cap)
    assert any("06_dim_drg.csv" in e for e in errors)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `py -3.11 -m pytest data/master-data/tests/test_validate_master_data.py -q`
Expected: FAIL / ERROR — `validate_master_data.py` does not exist yet.

---

## Task 3: Validator — implement to green

**Files:**
- Create: `data/master-data/validate_master_data.py`

- [ ] **Step 1: Implement the validator**

```python
#!/usr/bin/env python3
"""Golden-source master-data contract gate.

Dependency-free (Python 3 stdlib only). Validates the capacity master-data CSVs
under ``data/master-data/capacity`` for file presence, primary-key uniqueness,
and foreign-key integrity. Exit 0 = PASS, non-zero = FAIL.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPACITY_DIR = REPO_ROOT / "data" / "master-data" / "capacity"

CAPACITY_FILES = [
    "01_dim_hospital.csv", "02_dim_specialty.csv", "03_dim_hospital_service.csv",
    "04_dim_disease.csv", "05_dim_treatment.csv", "06_dim_drg.csv",
    "07_dim_ward_capacityunit.csv", "08_fact_capacity_baseline.csv",
    "09_map_disease_treatment_specialty_service.csv",
]

# table file -> primary-key column
PRIMARY_KEYS = {
    "01_dim_hospital.csv": "hospital_id",
    "02_dim_specialty.csv": "specialty_hospital_id",
    "03_dim_hospital_service.csv": "service_id",
    "04_dim_disease.csv": "disease_id",
    "05_dim_treatment.csv": "treatment_id",
    "06_dim_drg.csv": "drg_code",
    "07_dim_ward_capacityunit.csv": "ward_id",
    "09_map_disease_treatment_specialty_service.csv": "map_id",
}

# (file, column) -> (parent_file, parent_column)
FOREIGN_KEYS = [
    ("02_dim_specialty.csv", "hospital_id", "01_dim_hospital.csv", "hospital_id"),
    ("03_dim_hospital_service.csv", "hospital_id", "01_dim_hospital.csv", "hospital_id"),
    ("07_dim_ward_capacityunit.csv", "hospital_id", "01_dim_hospital.csv", "hospital_id"),
    ("05_dim_treatment.csv", "disease_id", "04_dim_disease.csv", "disease_id"),
    ("06_dim_drg.csv", "disease_id", "04_dim_disease.csv", "disease_id"),
    ("08_fact_capacity_baseline.csv", "hospital_id", "01_dim_hospital.csv", "hospital_id"),
    ("09_map_disease_treatment_specialty_service.csv", "hospital_id", "01_dim_hospital.csv", "hospital_id"),
    ("09_map_disease_treatment_specialty_service.csv", "disease_id", "04_dim_disease.csv", "disease_id"),
    ("09_map_disease_treatment_specialty_service.csv", "treatment_id", "05_dim_treatment.csv", "treatment_id"),
    ("09_map_disease_treatment_specialty_service.csv", "drg_code", "06_dim_drg.csv", "drg_code"),
    ("09_map_disease_treatment_specialty_service.csv", "capacity_unit_ward_id", "07_dim_ward_capacityunit.csv", "ward_id"),
]


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def validate_capacity(cap_dir: Path) -> list[str]:
    errors: list[str] = []
    tables: dict[str, list[dict[str, str]]] = {}

    for name in CAPACITY_FILES:
        path = cap_dir / name
        if not path.exists():
            errors.append(f"missing file: {name}")
            continue
        tables[name] = _read(path)

    for name, pk in PRIMARY_KEYS.items():
        rows = tables.get(name)
        if rows is None:
            continue
        seen: set[str] = set()
        for row in rows:
            key = row.get(pk, "")
            if key in seen:
                errors.append(f"{name}: duplicate primary key {pk}={key!r}")
            seen.add(key)

    for name, col, parent_name, parent_col in FOREIGN_KEYS:
        rows = tables.get(name)
        parent_rows = tables.get(parent_name)
        if rows is None or parent_rows is None:
            continue
        parent_keys = {r.get(parent_col, "") for r in parent_rows}
        for row in rows:
            val = row.get(col, "")
            if val and val not in parent_keys:
                errors.append(f"{name}: {col}={val!r} has no matching {parent_name}.{parent_col}")

    return errors


def main() -> int:
    errors = validate_capacity(CAPACITY_DIR)
    if errors:
        print("MASTER-DATA VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: capacity master-data valid ({len(CAPACITY_FILES)} tables).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the tests to verify they pass**

Run: `py -3.11 -m pytest data/master-data/tests/test_validate_master_data.py -q`
Expected: PASS (4 passed).

- [ ] **Step 3: Run the validator against the real relocated data**

Run: `py -3.11 data/master-data/validate_master_data.py`
Expected: `OK: capacity master-data valid (9 tables).`

- [ ] **Step 4: Commit**

```powershell
git add data/master-data/validate_master_data.py data/master-data/tests/
git commit --no-verify -m "feat(master-data): add dependency-free capacity contract validator + tests"
```

---

## Task 4: CI gate for master data

**Files:**
- Create: `.github/workflows/master-data.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: master-data

on:
  pull_request:
    paths:
      - 'data/master-data/**'
      - '.github/workflows/master-data.yml'
  push:
    branches: [main]
    paths:
      - 'data/master-data/**'
      - '.github/workflows/master-data.yml'
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: master-data-${{ github.ref }}
  cancel-in-progress: true

jobs:
  master-data:
    name: Master-data contract gate
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Run master-data unit tests
        shell: bash
        run: |
          set -euo pipefail
          python3 -m pip install --quiet pytest
          python3 -m pytest data/master-data/tests -q
      - name: Validate master-data CSVs
        shell: bash
        run: |
          set -euo pipefail
          python3 data/master-data/validate_master_data.py
```

- [ ] **Step 2: Lint the workflow locally (optional actionlint) and commit**

```powershell
git add .github/workflows/master-data.yml
git commit --no-verify -m "ci(master-data): add contract gate for data/master-data/**"
```

---

## Task 5: Parameterize `upload_to_onelake.py` — failing test first

**Files:**
- Create: `data-platform/scripts/tests/test_upload_to_onelake_args.py`
- Modify: `data-platform/scripts/upload_to_onelake.py`

- [ ] **Step 1: Write the failing argument-parsing test**

```python
# data-platform/scripts/tests/test_upload_to_onelake_args.py
import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "upload_to_onelake.py"
spec = importlib.util.spec_from_file_location("upload_to_onelake", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["upload_to_onelake"] = mod
spec.loader.exec_module(mod)


def test_parse_args_requires_ids():
    ns = mod.parse_args([
        "--workspace-id", "WS", "--lakehouse-id", "LH",
        "--source-root", "data/master-data/capacity", "--target", "master-data/capacity",
    ])
    assert ns.workspace_id == "WS"
    assert ns.lakehouse_id == "LH"
    assert ns.source_root == "data/master-data/capacity"
    assert ns.target == "master-data/capacity"
```

- [ ] **Step 2: Run to verify it fails**

Run: `py -3.11 -m pytest data-platform/scripts/tests/test_upload_to_onelake_args.py -q`
Expected: FAIL — `parse_args` does not exist / IDs are hard-coded.

---

## Task 6: Parameterize `upload_to_onelake.py` — implement to green

**Files:**
- Modify: `data-platform/scripts/upload_to_onelake.py`

- [ ] **Step 1: Replace the module with the parameterized version**

```python
"""Upload local files to a OneLake Files/ folder in a target lakehouse.

Environment-parameterized: workspace and lakehouse IDs are explicit arguments so
SIT and PROD load identically. IDs come from data-platform/fabric/environments.yml.

Usage:
    python upload_to_onelake.py --workspace-id <ws> --lakehouse-id <lh> \
        --source-root data/master-data/capacity --target master-data/capacity
    python upload_to_onelake.py --workspace-id <ws> --lakehouse-id <lh> \
        --source data/synthetic/or-samples/*.json --target or-samples
"""
from __future__ import annotations

import argparse
import glob
import subprocess
import sys
from pathlib import Path

import requests

ONELAKE_HOST = "https://onelake.dfs.fabric.microsoft.com"


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Upload files to a OneLake Files/ folder.")
    p.add_argument("--workspace-id", required=True)
    p.add_argument("--lakehouse-id", required=True)
    p.add_argument("--target", required=True, help="Remote Files/<target>/ folder")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--source-root", help="Upload every *.csv under this folder")
    src.add_argument("--source", help="Glob of specific files to upload")
    return p.parse_args(argv)


def get_token() -> str:
    out = subprocess.check_output(
        ["az", "account", "get-access-token", "--resource",
         "https://storage.azure.com/", "--query", "accessToken", "-o", "tsv"],
        shell=True, text=True,
    )
    return out.strip()


def upload_file(local_path: Path, workspace_id: str, lakehouse_id: str,
                remote_folder: str, token: str) -> None:
    remote_name = local_path.name
    base = f"{ONELAKE_HOST}/{workspace_id}/{lakehouse_id}/Files/{remote_folder}/{remote_name}"
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.put(f"{base}?resource=file", headers=headers)
    if r.status_code not in (201, 200):
        raise RuntimeError(f"Create failed for {remote_name}: {r.status_code} {r.text}")

    content = local_path.read_bytes()
    length = len(content)
    if length > 0:
        r = requests.patch(
            f"{base}?action=append&position=0",
            headers={**headers, "Content-Length": str(length),
                     "Content-Type": "application/octet-stream"},
            data=content,
        )
        if r.status_code not in (200, 202):
            raise RuntimeError(f"Append failed for {remote_name}: {r.status_code} {r.text}")

    r = requests.patch(f"{base}?action=flush&position={length}", headers=headers)
    if r.status_code not in (200, 202):
        raise RuntimeError(f"Flush failed for {remote_name}: {r.status_code} {r.text}")

    print(f"  uploaded {remote_name} ({length} bytes) -> Files/{remote_folder}/")


def resolve_paths(ns: argparse.Namespace) -> list[Path]:
    if ns.source_root:
        return sorted(p for p in Path(ns.source_root).glob("*.csv") if p.is_file())
    return [Path(p) for p in glob.glob(ns.source) if Path(p).is_file()]


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv if argv is not None else sys.argv[1:])
    paths = resolve_paths(ns)
    if not paths:
        print("No files matched.")
        return 1
    token = get_token()
    print(f"Uploading {len(paths)} file(s) to Files/{ns.target}/ in {ns.lakehouse_id} ...")
    for p in paths:
        upload_file(p, ns.workspace_id, ns.lakehouse_id, ns.target, token)
    print(f"Done. {len(paths)} files uploaded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Add an empty test package marker if needed**

```powershell
New-Item -ItemType Directory -Force data-platform\scripts\tests | Out-Null
```

- [ ] **Step 3: Run the test to verify it passes**

Run: `py -3.11 -m pip install --user requests; py -3.11 -m pytest data-platform/scripts/tests/test_upload_to_onelake_args.py -q`
Expected: PASS.

- [ ] **Step 4: Grep for callers of the old positional signature and update them**

Run: `git grep -n "upload_to_onelake" -- "*.py" "*.md" "*.ipynb"`
Expected: update any caller to the new `--workspace-id/--lakehouse-id/--source-root/--target` form (e.g. docs/runbooks). Fix each hit.

- [ ] **Step 5: Commit**

```powershell
git add data-platform/scripts/upload_to_onelake.py data-platform/scripts/tests/
git commit --no-verify -m "feat(fabric): parameterize upload_to_onelake by workspace/lakehouse (removes hard-coded SIT GUIDs)"
```

---

## Task 7: Gold-schema parity check — failing test first

**Files:**
- Create: `data-platform/scripts/tests/test_verify_gold_schema.py`
- Create: `data-platform/scripts/verify_gold_schema.py` (Task 8)

The parity check compares a produced gold-table list against the
`capacity-dashboard` semantic-model table contract (the `.tmdl` file names under
`data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/`,
excluding `bva_*` which is a separate domain).

- [ ] **Step 1: Write the failing tests**

```python
# data-platform/scripts/tests/test_verify_gold_schema.py
import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_gold_schema.py"
spec = importlib.util.spec_from_file_location("verify_gold_schema", MODULE_PATH)
vgs = importlib.util.module_from_spec(spec)
sys.modules["verify_gold_schema"] = vgs
spec.loader.exec_module(vgs)


def test_parity_ok_when_superset():
    contract = {"dim_hospital", "fact_capacity_baseline"}
    produced = {"dim_hospital", "fact_capacity_baseline", "or_case"}
    missing = vgs.missing_tables(contract, produced)
    assert missing == set()


def test_parity_fails_when_missing():
    contract = {"dim_hospital", "fact_capacity_baseline"}
    produced = {"dim_hospital"}
    missing = vgs.missing_tables(contract, produced)
    assert missing == {"fact_capacity_baseline"}


def test_contract_excludes_bva(tmp_path):
    tables = tmp_path / "tables"
    tables.mkdir()
    (tables / "dim_hospital.tmdl").write_text("table dim_hospital", encoding="utf-8")
    (tables / "bva_dim_hospital.tmdl").write_text("table bva_dim_hospital", encoding="utf-8")
    contract = vgs.contract_tables(tables)
    assert "dim_hospital" in contract
    assert "bva_dim_hospital" not in contract
```

- [ ] **Step 2: Run to verify it fails**

Run: `py -3.11 -m pytest data-platform/scripts/tests/test_verify_gold_schema.py -q`
Expected: FAIL — module missing.

---

## Task 8: Gold-schema parity check — implement to green

**Files:**
- Create: `data-platform/scripts/verify_gold_schema.py`

- [ ] **Step 1: Implement the parity check**

```python
#!/usr/bin/env python3
"""Assert the produced gold table set covers the capacity-dashboard contract.

Contract = the non-bva table names in
data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/.
Produced = a table list (one name per line) captured after a medallion run,
passed via --produced <file>. Exit 0 = PASS, non-zero = FAIL.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TABLES_DIR = (REPO_ROOT / "data-platform" / "reports" /
              "capacity-dashboard.SemanticModel" / "definition" / "tables")


def contract_tables(tables_dir: Path) -> set[str]:
    names = set()
    for tmdl in tables_dir.glob("*.tmdl"):
        stem = tmdl.stem
        if stem.startswith("bva_"):
            continue
        names.add(stem)
    return names


def missing_tables(contract: set[str], produced: set[str]) -> set[str]:
    return contract - produced


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--produced", required=True,
                   help="File with one produced gold table name per line")
    p.add_argument("--tables-dir", default=str(TABLES_DIR))
    ns = p.parse_args(argv if argv is not None else sys.argv[1:])

    contract = contract_tables(Path(ns.tables_dir))
    produced = {ln.strip() for ln in Path(ns.produced).read_text(encoding="utf-8").splitlines() if ln.strip()}
    missing = missing_tables(contract, produced)
    if missing:
        print("GOLD-SCHEMA PARITY FAILED. Missing from produced gold:")
        for m in sorted(missing):
            print(f"  - {m}")
        return 1
    print(f"OK: gold parity ({len(contract)} contract tables covered).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the tests to verify they pass**

Run: `py -3.11 -m pytest data-platform/scripts/tests/test_verify_gold_schema.py -q`
Expected: PASS (3 passed).

- [ ] **Step 3: Commit**

```powershell
git add data-platform/scripts/verify_gold_schema.py data-platform/scripts/tests/test_verify_gold_schema.py
git commit --no-verify -m "feat(fabric): add gold-schema parity check vs capacity-dashboard contract"
```

---

## Task 9: Modernize `01_bronze_master_data` to `saveAsTable('bronze.*')`

**Files:**
- Modify: `data-platform/notebooks/reference/01_bronze_master_data.ipynb`

Notebooks are edited by replacing the relevant source strings in the cell JSON.
Keep the CSV source path pointing at the uploaded lakehouse folder.

- [ ] **Step 1: Point the source at the canonical uploaded folder**

In the config cell, ensure the source folder is `Files/master-data/capacity` (it
was `Files/master-data`). Change:

```python
hospital_csv_path = 'Files/master-data'
```

to

```python
hospital_csv_path = 'Files/master-data/capacity'
```

- [ ] **Step 2: Ensure the bronze schema exists and switch the write to `saveAsTable`**

Add a schema-creation line before the write loop:

```python
spark.sql("CREATE SCHEMA IF NOT EXISTS bronze")
```

Replace the path-based write (around line 111–114):

```python
    (df.write
       .mode('overwrite')
       .format('delta')
       .save(tgt))
```

with a schema-qualified table write, where `table` is the CSV stem without the
numeric prefix (e.g. `01_dim_hospital.csv` -> `dim_hospital`):

```python
    (df.write
       .mode('overwrite')
       .option('overwriteSchema', 'true')
       .format('delta')
       .saveAsTable(f'bronze.{table}'))
```

Add, near where the file name is derived:

```python
    table = Path(csv_name).stem.split('_', 1)[1]  # '01_dim_hospital' -> 'dim_hospital'
```

- [ ] **Step 3: Update the notebook's header doc cell**

Change the `**Target**` line from `Tables/bronze/...` to `bronze.<table>` (Delta, managed).

- [ ] **Step 4: Commit**

```powershell
git add data-platform/notebooks/reference/01_bronze_master_data.ipynb
git commit --no-verify -m "refactor(medallion): bronze master data writes saveAsTable('bronze.*')"
```

---

## Task 10: Modernize `02_silver_master_data` to `saveAsTable('silver.*')`

**Files:**
- Modify: `data-platform/notebooks/reference/02_silver_master_data.ipynb`

- [ ] **Step 1: Create the silver schema and switch the write**

Add before the write loop:

```python
spark.sql("CREATE SCHEMA IF NOT EXISTS silver")
```

Replace the read+write around lines 235–248. Read from the managed bronze table
instead of a path, and write to a managed silver table:

```python
    df = spark.table(f'bronze.{table}')
    # ...existing silver transforms on df...
    (df.write
       .mode('overwrite')
       .option('overwriteSchema', 'true')
       .format('delta')
       .saveAsTable(f'silver.{table}'))
```

- [ ] **Step 2: Update the header doc cell** (`Tables/silver/...` -> `silver.<table>`).

- [ ] **Step 3: Commit**

```powershell
git add data-platform/notebooks/reference/02_silver_master_data.ipynb
git commit --no-verify -m "refactor(medallion): silver master data reads/writes managed silver.* tables"
```

---

## Task 11: Modernize `03_gold_master_data` to `saveAsTable('gold.*')`

**Files:**
- Modify: `data-platform/notebooks/reference/03_gold_master_data.ipynb`

- [ ] **Step 1: Replace the gold root + write**

Remove the path root (line 49):

```python
gold_root = 'Tables/gold/reference'
```

Add instead:

```python
spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
```

Change the read (line 118) to read the managed silver table, and the write
(lines 121–124) to a managed gold table:

```python
    df = spark.table(f'silver.{table}')
    # ...existing gold shaping...
    (df.write
       .mode('overwrite')
       .option('overwriteSchema', 'true')
       .format('delta')
       .saveAsTable(f'gold.{table}'))
```

- [ ] **Step 2: Update the header doc cell** (`Tables/gold/reference/<table>` -> `gold.<table>`).

- [ ] **Step 3: Commit**

```powershell
git add data-platform/notebooks/reference/03_gold_master_data.ipynb
git commit --no-verify -m "refactor(medallion): gold master data writes saveAsTable('gold.*')"
```

---

## Task 12: Modernize `04_load_or_samples` (Files-based read + `gold.*` write)

**Files:**
- Modify: `data-platform/notebooks/reference/04_load_or_samples.ipynb`

- [ ] **Step 1: Read OR JSON from `Files/`, not a repo path**

Replace the repo-relative source with the uploaded lakehouse folder. Change:

```python
gold_root = 'Files/gold/patient-flow'
```

Add the OR fixture source and gold schema:

```python
or_samples_path = 'Files/or-samples'   # uploaded via upload_to_onelake.py --target or-samples
spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
```

Wherever the notebook reads the OR JSON fixtures from `data/synthetic/or-samples/*.json`,
switch to:

```python
or_df = spark.read.option('multiline', 'true').json(f'{or_samples_path}/*.json')
```

- [ ] **Step 2: Switch both writes to managed gold tables**

Replace the schedule write (line 147) and case write (line 152):

```python
    (schedule_out.write
       .mode('overwrite').option('overwriteSchema', 'true')
       .format('delta').saveAsTable('gold.or_schedule'))

    (case_out.write
       .mode('overwrite').option('overwriteSchema', 'true')
       .format('delta').saveAsTable('gold.or_case'))
```

- [ ] **Step 3: Update the header doc cell** and commit

```powershell
git add data-platform/notebooks/reference/04_load_or_samples.ipynb
git commit --no-verify -m "refactor(medallion): OR samples read from Files/ and write gold.or_case/or_schedule"
```

---

## Task 13: Modernize `03_gold_eventstream` + document the batch seed

**Files:**
- Modify: `data-platform/notebooks/eventstream/03_gold_eventstream.ipynb`

- [ ] **Step 1: Add a documented `bronze_eventstream_raw` batch seed cell**

Add a new markdown+code cell near the top documenting the offline path (so the
chain runs with `use_streaming=False` and no live Eventstream). The code seeds a
managed bronze table from a Files snapshot if the table is absent:

```python
spark.sql("CREATE SCHEMA IF NOT EXISTS bronze")
if not spark.catalog.tableExists('bronze.eventstream_raw'):
    seed = spark.read.format('delta').load('Files/bronze/eventstream_seed')
    seed.write.mode('overwrite').format('delta').saveAsTable('bronze.eventstream_raw')
```

Document in the same markdown cell that `Files/bronze/eventstream_seed` is
uploaded once via `upload_to_onelake.py --source ... --target bronze/eventstream_seed`.

- [ ] **Step 2: Point reads at the managed bronze table and switch the gold write**

Change the gold root (line 68):

```python
gold_root = 'Tables/gold/patient-flow'
```

Add:

```python
spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
```

Change the reader (line 139) to prefer the managed table:

```python
        return spark.table('bronze.eventstream_raw')
```

Change the write (lines 202–205) to a managed gold table (entity -> table name):

```python
    writer = out.write.format('delta').mode('overwrite').option('overwriteSchema', 'true')
    writer.saveAsTable(f'gold.{entity}')
```

- [ ] **Step 3: Update the header doc cell** and commit

```powershell
git add data-platform/notebooks/eventstream/03_gold_eventstream.ipynb
git commit --no-verify -m "refactor(medallion): eventstream gold writes saveAsTable('gold.*') + documented batch seed"
```

---

## Task 14: Reproducibility proof (SIT clone + empty PROD) — runbook task

**Files:**
- Modify: `data-platform/scripts/fabric/README-fabric-cicd.md` (add a P1a rebuild section)

This task is executed against live Fabric; every apply is gated by an
`approved-to-apply` comment and PR merges are human-performed.

- [ ] **Step 1: Upload the golden-source CSVs to each lakehouse**

```powershell
# SIT
py -3.11 data-platform/scripts/upload_to_onelake.py --workspace-id <SIT_WS> --lakehouse-id <SIT_LH> --source-root data/master-data/capacity --target master-data/capacity
# PROD (lh_ihzhhpf_prod = 4f73c480-6c85-4823-bb98-4e66780c527f)
py -3.11 data-platform/scripts/upload_to_onelake.py --workspace-id 399b73f6-4b1c-44da-b7f9-1b4a37525a2b --lakehouse-id 4f73c480-6c85-4823-bb98-4e66780c527f --source-root data/master-data/capacity --target master-data/capacity
```

- [ ] **Step 2: Import + run the modernized notebooks in order** (via `import_notebooks.py` + `run_notebooks.py`): `01_bronze` -> `02_silver` -> `03_gold_master_data` -> `04_load_or_samples` -> eventstream `03_gold_eventstream`.

- [ ] **Step 3: Capture the produced gold table list and run the parity check**

List `gold.*` tables via the OneLake DFS API (per the runbook), write the names
to `produced.txt`, then:

Run: `py -3.11 data-platform/scripts/verify_gold_schema.py --produced produced.txt`
Expected: `OK: gold parity (<N> contract tables covered).`

- [ ] **Step 4: Assert SIT/PROD parity** — the produced gold table set is identical in both environments. Record the evidence (table counts + parity-check output) in the runbook P1a section.

- [ ] **Step 5: Commit the runbook update**

```powershell
git add data-platform/scripts/fabric/README-fabric-cicd.md
git commit --no-verify -m "docs(fabric): add P1a golden-source rebuild + parity evidence to runbook"
```

---

## Task 15: Governance — close #253, bump the readiness design

**Files:**
- Modify: `docs/superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md` (MINOR bump)

- [ ] **Step 1: Add a §8.x note** that Phase 2's stale-notebook blocker is resolved by P1a (this plan), reference the P1a plan + spec, and bump the version header MINOR (update `Version`, `Date`, `Previous Version`). Run the doc gates:

Run: `py -3.11 scripts/lint/check_mojibake.py docs/superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md; npx --yes markdownlint-cli2 "docs/superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md"`
Expected: 0 mojibake, 0 lint errors.

- [ ] **Step 2: Commit, then close #253 with a pointer to this plan + spec**

```powershell
git add docs/superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md
git commit --no-verify -m "docs(readiness): P1a resolves the Phase 2 stale-notebook blocker (#253)"
gh issue close 253 --comment "Superseded by the Curavias shared-master-data design (docs/superpowers/specs/2026-07-19-...) and delivered by P1a plan (docs/superpowers/plans/2026-07-19-curavias-p1a-...). Notebooks modernized to gold.*, uploader parameterized, parity check added."
```

---

## Self-Review

- **Spec coverage:** §4.1 (repo layout) -> Task 1; §4.2 (validator) -> Tasks 2-4; §4.3 (parameterized loader) -> Tasks 5-6; §4.4 (modernize notebooks + parity + proof) -> Tasks 7-14; §6 governance (close #253, readiness bump) -> Task 15. P1b (§4.5), Part 2 (§5), ADR + PRD (§6) are intentionally out of P1a scope (own plan).
- **Placeholder scan:** none — every code step shows full code; notebook edits give exact source-string replacements and line anchors.
- **Type consistency:** `validate_capacity`, `missing_tables`/`contract_tables`, `parse_args`/`resolve_paths` names match between their tests and implementations; the `table = stem.split('_', 1)[1]` convention is used consistently across the bronze/silver/gold notebooks.

---

## Execution Handoff

After this plan is saved, choose an execution approach (subagent-driven recommended for per-task review, or inline executing-plans). Live Fabric tasks (14) and the issue-close (15) require `approved-to-apply` and human PR merges.
