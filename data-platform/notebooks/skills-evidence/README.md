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

## Files

| File | Layer | Purpose |
| --- | --- | --- |
| `build_gold_org_spine.py` | Gold | Pure transforms: `rebrand_hospital_dimension` (1:1 fold, drop H_HSL, strip real geography, keep `hospital_id` as PK) + org-spine projections that strip real-name provenance (`grounded_on`). `run()` is the Fabric entrypoint. |
| `tests/test_build_gold_org_spine.py` | — | Spark-free unit tests over the real relocated CSVs asserting no real name/geography leaks and a clean tenant<->hospital 1:1. |
| `build_gold_skills.py` | Gold | Pure transforms for the skills domain: supply / demand / gap / eligibility projections, `source_mode` (live vs simulated) validation, and the bed-vs-ops `care_setting` split. `run()` is the Fabric entrypoint. |
| `tests/test_build_gold_skills.py` | — | Spark-free unit tests over the real skills CSVs asserting domain validation, the care-setting split, demand/gap consistency, and the source-mode badge flag. |

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

The end-to-end Fabric pipeline run needs the WS-A landing zone + `approved-to-apply`;
capture that evidence in a follow-up comment (per the plan acceptance gate).
