# Superpowers PR Contract

> This file fulfils the Superpowers PR Contract for the current PR when the PR
> description cannot be edited directly (e.g. for AI-agent-generated PRs).
> The `superpowers-compliance` CI workflow validates the PR body **and** this file.

## Linked Issue / Work Item

Closes #57, #59, #60.

- Parent sprint issue: `#54`
- Delivery issue for this PR: `#57`, `#59`, `#60`

> Traceability rule: every PR must link to at least one sprint-scoped GitHub
> issue, and every sprint issue must be closed by one or more linked PRs.

## Requirements Implemented

- `FR-DATA-001`: contract-first data product registration (4 contracts).
- `FR-DATA-002`: synthetic data generation with deterministic seed mode.
- `FR-DATA-003`: schema validation gated in CI.
- `FR-DATA-005`: explainability artefact for AI/matching output.
- `FR-DATA-006`: cross-contract referential integrity (Organization ↔ Location ↔ Encounter).
- `FR-DATA-008`: data product traceability registry.
- `FR-ONB-003`: supply-side onboarding metadata (Organization + Location hierarchy).
- `NFR-COMP-011`: PHI denylist enforced at validator level on demand contract.
- `NFR-DQ-005`: manifest sha256 checksums + minItems/maxItems envelope controls.
- `NFR-AI-003`: recommendation freshness via `generatedAt` + `validUntil` (+30 min).
- `NFR-AI-004`: recommendation top-N with rule weights summing to 1.0.
- `CH-C01`, `CH-C03`, `CH-C05`: control hardening.
- AMA `ER-01`: episode-based control unit honoured throughout demand contract.
- `ADR-0003`: Swiss-only data residency reflected in dataset envelope.

## Sprint Context

- Sprint: `S07` — sprint file: `docs/sprints/sprint-07-data-platform-and-data-products-superpowers.md`
- Sprint issue link: `#54`

## Execution Mode

- [x] `superpowers` (default)
- [ ] `legacy-agent-compat`

## Skill Applicability and Evidence

- [x] `writing-plans` applicable and evidence linked
- [x] `test-driven-development` applicable and evidence linked
- [x] `systematic-debugging` applicable and evidence linked
- [x] `verification-before-completion` applicable and evidence linked

Non-applicable rationale: all four skills were applied for this PR.

Evidence links:

- Planning artifact: `docs/superpowers/plans/2026-06-12-patient-capacity-data-product-implementation.md`
  (13-task implementation plan, fully executed)
- Test output: `python -m unittest discover -s data/synthetic/tests -v` → 90/90 OK
  (76 contract + 10 generator + 4 baseline)
- Debug log: iterative validator debugging through schema edge cases
  (nullable types, ISO-8601, minItems/maxItems, cross-contract FK checks)
- Final verification: `python policy/policy_gate.py` → pass, 50/50 checks,
  0 critical failures; `markdownlint-cli2` → clean

Legacy mode approval issue: N/A (`legacy-agent-compat` is not checked; superpowers mode selected)

## Validation Evidence

- [x] `npx --yes markdownlint-cli2 "**/*.md" "#node_modules"` → clean
- [x] `python -m unittest discover -s data/synthetic/tests -v` → 90/90 OK
- [x] `python policy/policy_gate.py` → pass, 50/50 checks, 0 critical failures
- [x] Generator replay `--seed 42 --with-beds --encounters 50` → deterministic, byte-identical output
