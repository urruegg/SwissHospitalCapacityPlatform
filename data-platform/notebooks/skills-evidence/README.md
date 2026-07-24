# Skills-evidence + Curavias org-spine medallion (Sprint 23, #255)

Fabric Spark transforms that land the Curavias organisation spine and the
workforce skills-evidence domain onto the `gold.*` layer, and **fold the legacy
real-hospital `dim_hospital` into the Curavias demo identity**.

## Why the re-brand

The demo must present **Curavias** entities (CuraNova / Curalp / Vialta), never
the real hospitals the synthetic data was grounded on. The Curavias master data
(`data/master-data/curavias-org-skills/`) was authored to shadow three real
hospitals **1:1** (beds/FTE grounded):

| Curavias tenant | Legacy hospital | Grounding |
| --- | --- | --- |
| `CN` Uniklinik CuraNova | `H_USZ` | ~900 beds / 8600 FTE |
| `CP` Kantonsspital Curalp | `H_LUKS` | ~840 / 8600 (LUKS 839 / 8628) |
| `VT` Spital Vialta | `H_SZB` | 174 / 1200 (exact) |
| — | `H_HSL` (Hirslanden) | **no tenant -> dropped/parked** |

Because `H_HSL` is dropped from `dim_hospital`, `run()` also prunes its rows
from the hospital-keyed capacity gold tables (`dim_specialty`,
`dim_hospital_service`, `dim_ward_capacityunit`, `fact_capacity_baseline`,
`map_disease_treatment_specialty_service`) and the eventstream seed
(`gen_eventstream_seed.py`) drops `H_HSL`, so no fact orphans under the
Direct-Lake `(Blank)` member (issue #349).

## Files

| File | Layer | Purpose |
| --- | --- | --- |
| `build_gold_org_spine.py` | Gold | Pure transforms: `rebrand_hospital_dimension` (1:1 fold, drop H_HSL, strip real geography, keep `hospital_id` as PK), org-spine projections that strip real-name provenance (`grounded_on`), and `prune_orphan_hospital_rows` (drop dropped-hospital rows from the capacity gold tables, issue #349). `build_org_spine_gold()` assembles the four org-spine gold tables; `run()` is the Fabric entrypoint (org spine + capacity prune). |
| `tests/test_build_gold_org_spine.py` | — | Spark-free unit tests over the real relocated CSVs asserting no real name/geography leaks, a clean tenant<->hospital 1:1, and the `build_org_spine_gold()` table set + row counts. |
| `build_gold_skills.py` | Gold | Pure transforms for the skills domain: supply / demand / gap / eligibility projections, `source_mode` (live vs simulated) validation, and the bed-vs-ops `care_setting` split. `build_skills_gold()` assembles the eight skills gold tables; `run()` is the Fabric entrypoint. |
| `tests/test_build_gold_skills.py` | — | Spark-free unit tests over the real skills CSVs asserting domain validation, the care-setting split, demand/gap consistency, the source-mode badge flag, and the `build_skills_gold()` table set + row counts. |
| `_fabric_gold_io.py` | Gold | Deploy-class Spark I/O helpers shared by both `run()`s: read a Files-mount CSV / an existing Delta table into `list[dict]`, and write `gold.<name>` Delta with the sprint-09 seven-column governance stamp. Fabric-runtime only. |
| `05_gold_org_skills.ipynb` | Gold | Thin Fabric notebook that imports the three modules from the `Files/skills-evidence/` mount and calls `build_gold_org_spine.run()` then `build_gold_skills.run()`. Wired into `run_medallion.py` after `03_gold_master_data`. |

## Skills care-setting split + live-vs-simulated badge (WS-C2)

* `care_setting` (`bed` = Pflegepersonal/nursing, `ops` = Doctors + specialised)
  is **explicit** on `fact_skill_demand` / `fact_skill_gap` because those facts
  are skill-grained (no occupation), so cross-cutting skills (`SK-BLS`,
  `SK-IPC`, ...) cannot be attributed by derivation.
* For the **occupation-grained** tables (`dim_occupation_role`,
  `bridge_role_skill_demand_template`) the care setting is **derived** from the
  ISCO-08 code (`derive_occupation_care_setting`), so supply/eligibility split
  by care setting without hand-authored data. Derivation fails fast on any
  unclassified ISCO code.
* `source_mode` (`live` | `simulated`) is preserved on demand / gap / assertion
  so the badge measure reads a real flag and is never invented.

## Conventions

* Pure functions are unit-tested without Spark (external-signals / CSA pattern);
  `run()` executes only inside the Fabric Spark runtime.
* `hospital_id` stays the primary key so every downstream fact, relationship and
  RLS role keying on it keeps working — the re-brand only overrides display
  columns and adds Curavias tenant attributes.
* The capacity master-data CSVs carry a UTF-8 BOM; read them with `utf-8-sig`.
* Synthetic / no-PHI only (ADR-0013 / ADR-0016).

## Run locally

```bash
python -m pytest data-platform/notebooks/skills-evidence/tests -v
```

## Run in Fabric (end-to-end, `approved-to-apply` gated)

The gold build reads the Curavias CSVs and the three Python modules from the
lakehouse `Files/` mount, so upload both once per environment, then run the
medallion (which now includes `05_gold_org_skills` after `03_gold_master_data`):

```bash
# 1) upload the relocated Curavias master-data CSVs
python data-platform/scripts/upload_to_onelake.py --workspace-id <ws> \
  --lakehouse-id <lh> --source-root data/master-data/curavias-org-skills \
  --target master-data/curavias-org-skills

# 2) upload the skills-evidence Python modules (build_gold_*.py + _fabric_gold_io.py)
python data-platform/scripts/upload_to_onelake.py --workspace-id <ws> \
  --lakehouse-id <lh> --source "data-platform/notebooks/skills-evidence/*.py" \
  --target skills-evidence

# 3) plan, then apply (deploy gate: needs an approved-to-apply comment)
python data-platform/scripts/fabric/run_medallion.py --environment SIT
python data-platform/scripts/fabric/run_medallion.py --environment SIT --apply
```

The end-to-end Fabric pipeline run needs the WS-A landing zone + `approved-to-apply`;
capture that evidence in a follow-up comment (per the plan acceptance gate).
