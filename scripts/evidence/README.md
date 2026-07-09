# Evidence parsers — Showcase Evidence data product (Sprint 14 · T1)

Parse canonical repo sources into byte-stable JSON with provenance for the
[Showcase Evidence design spec](../../docs/superpowers/specs/2026-07-09-sprint-14-evidence-design.md).

## What it produces

| Parser | Source | Output(s) |
| --- | --- | --- |
| `prd_parser` | `docs/PRD.md` | `requirements.json` |
| `adr_parser` | `docs/adr/*.md` | `adrs.json` + `req_adr_map.json` |
| `bom_parser` | `docs/bom.yaml` | `bom.json` + `dependencies.json` |
| `region_availability_parser` | `docs/region-availability.yaml` | `region_availability.json` |
| `infra_parser` | `infra/**/*.bicep` | `deployed_bom.json` (stub — full ARG deferred, design spec §2.2) |

`publish.py` orchestrates all parsers and also merges the curated
`docs/adr-requirement-map.yaml` overlay into `req_adr_map.json`.

Output JSON is written under `data/evidence/` and validates against the JSON
Schemas in [`data/evidence/schema/`](../../data/evidence/schema/).

## Invariants

- **Byte-stable** — no wall-clock timestamps in output; keys sorted; rows sorted
  by a stable id. CI can diff parser output across runs.
- **Provenance on every row** — `sourcePath` + `sourceCommit`; availability facts
  additionally require `verifiedBy` + `asOf`.
- **Never merged into `main`** — the `evidence-publish` workflow commits output to
  the `evidence-latest` branch only (design spec §11 — avoid history bloat).

## Run locally

```bash
# From the repo root
python -m scripts.evidence.publish --repo-root . --out data/evidence

# Tests (dependency-free, stdlib unittest; also runs under pytest)
python -m unittest discover -s scripts/evidence/tests -t .
# or
cd scripts/evidence && pytest tests/
```

Runtime dependency: `PyYAML`. Test dependency: `jsonschema` (+ optional `pytest`).
