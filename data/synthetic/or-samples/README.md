# OR sample data fixtures (T5.4)

Deterministic synthetic operating-room fixtures for Sprint 09 v2.0.0
(design spec §6.2 dashboard OR page, §5.4 OR-Steering Agent).

## Files

| File | Contract | Purpose |
| ---- | -------- | ------- |
| `or_schedule.json` | [DC-OR-SCHEDULE-v1](../schema/dc-or-schedule-v1.schema.json) | Planned OR slots across 3 hospitals × 5 theatres × 3 months |
| `or_case.json` | [DC-OR-CASE-v1](../schema/dc-or-case-v1.schema.json) | Intra-day case event stream (start / overrun / cancellation / turnover) |
| `generate.py` | — | Deterministic generator (`seed=42`) |

## Hospitals

Encoded into `orSlotId` / `theatreId` prefixes; not a top-level record field
(the contract has no `hospitalId` — hospital identity is derived from the ID
prefix at the loader). All three hospitals resolve to
`dataResidencyRegion = switzerlandnorth`.

| Short code | Hospital |
| ---------- | -------- |
| `USZ`      | UniversitätsSpital Zürich |
| `LUKS`     | Luzerner Kantonsspital |
| `SZB`      | Spital Zollikerberg (Bezirk) |

## Guarantees

- **Deterministic** — `python generate.py` with `seed=42` produces byte-identical
  JSON on every run.
- **No PHI** — encounter IDs are sequential opaque tokens (`ENC-2027-000001`),
  surgeon references are role IDs (`ROLE-SURG-USZ-01`), no names / DOBs / free
  text. Every record carries `_pseudonymisation_flag: true` at the loader
  (T5.5).
- **Volume** — ≥ 1 000 slots + ≥ 500 unique cases per plan §T5.4. Cases emit
  multi-event streams so the case-event record count is several thousand.
- **Realism** — acuity mix and cancellation rates loosely mirror hospital
  presets from T3.1 (specialty distribution weighted toward orthopedics /
  general surgery).

## Regenerate

```powershell
python data/synthetic/or-samples/generate.py
```

Re-run must show identical byte counts and identical file hashes:

```powershell
Get-FileHash data/synthetic/or-samples/or_schedule.json, data/synthetic/or-samples/or_case.json
```

## Validate against schemas

```powershell
python -c "import json, jsonschema; s=json.load(open('data/synthetic/or-samples/or_schedule.json')); v=json.load(open('data/synthetic/schema/dc-or-schedule-v1.schema.json')); jsonschema.validate(instance=s, schema=v); print('SCHEDULE OK')"
python -c "import json, jsonschema; s=json.load(open('data/synthetic/or-samples/or_case.json')); v=json.load(open('data/synthetic/schema/dc-or-case-v1.schema.json')); jsonschema.validate(instance=s, schema=v); print('CASE OK')"
```

## Live ingestion

Live OR ingestion lands in Sprint 10 (see plan §T5.4 and design spec §6.2).
This fixture exists only to give the semantic model (T4.1) and dashboard (T5.1)
concrete rows during Sprint 09 development.
