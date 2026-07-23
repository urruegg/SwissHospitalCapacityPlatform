# Curavias Organisation + Skills Master Data

Git-owned, synthetic (no-PHI) master data for the unified Curavias organisation
spine and the workforce skills-evidence domain. Loaded on demand into the
medallion (Bronze → Silver → Gold) per the Sprint 23 refactor design
([`2026-07-23-sprint-23-org-skills-refactor-design.md`](../../../docs/superpowers/specs/2026-07-23-sprint-23-org-skills-refactor-design.md), D1).

## Contents

- `generate_master_data.py` — deterministic (`random.seed(42)`, ref date
  2026-07-19, Python 3 stdlib only) synthetic generator. Writes the 20 CSVs
  into this folder.
- 20 `*.csv` — the generated org/skills tables (tenant, org unit, department,
  employee, skill, assertion, demand, gap, eligibility, crosswalk, …).

## Provenance

Authored in the idea pack
[`unified-curavias-organisation-and-skills-ontology/`](../../../docs/superpowers/ideas/unified-curavias-organisation-and-skills-ontology/)
(Steps 1–4). Relocated here as the git-owned home so the generator + data are
version-controlled and reproducible (design D1). The generator's output path was
changed from `./master-data/` to its own directory to match the
`data/master-data/capacity/` layout convention; content is unchanged.

## Regenerate

```bash
cd data/master-data/curavias-org-skills
python generate_master_data.py
```

Output is byte-identical to the committed CSVs (deterministic seed). Any diff
after regeneration is a reproducibility regression and must be investigated.

## Constraints

- **Synthetic / no-PHI only** (ADR-0013 / ADR-0016). Employee names are
  fabricated; organisation structure is realistic but not a real workforce.
- Validated at the silver gate (PK/FK, GLN mod-10, enum domains, load order) —
  see `data/master-data/validate_master_data.py` (extended in WS-B4).
