# Knowledge Agent — Documentation Steward — Implementation Plan

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-17 |
| **Author** | Urs Rüegg |
| **Status** | In progress |
| **Previous Version** | n/a (new — approved via issue #242) |
| **Design spec** | [2026-07-17-knowledge-agent-doc-steward-design.md](../specs/2026-07-17-knowledge-agent-doc-steward-design.md) |
| **Approval issue** | [#242](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/242) |

---

## Execution model

Superpowers-first. Layer C (automation) is built test-first per
`test-driven-development` (RED: 93 mojibake found + failing unit tests; GREEN:
detector/repairer pass and repo scans clean). Layer A (skill) documents judgment
only, per `writing-skills`. `verification-before-completion` gates the PR.

## Phase 1 — Layer C automation (test-first)

* [x] `scripts/lint/tests/test_check_mojibake.py` — 7 tests written first (RED).
* [x] `scripts/lint/check_mojibake.py` — detector; tests pass (GREEN).
* [x] `scripts/lint/fix_mojibake.py` — deterministic repairer.
* [x] Remediate existing debt — 93 occurrences across 13 files → 0 residual.
* [x] `.githooks/pre-commit` — blocks on mojibake, auto-fixes + verifies
  markdownlint; proven RED (blocks) and GREEN (passes) end-to-end.
* [x] `.gitattributes` — pin the hook to LF so Git-for-Windows bash runs it.
* [x] `.github/workflows/ci.yml` — `mojibake-scan` job (scan + self-test).

## Phase 2 — Layer A skill

* [x] `.github/skills/document-authoring/SKILL.md` — judgment-focused;
  frontmatter description is triggers-only (no workflow summary).
* [ ] AGENTS.md workspace-skills table row (Phase 4, CODEOWNERS-gated).

## Phase 3 — Layer B agent pack

* [x] `agents/knowledge-agent/AGENT.md` — Identity, Scope, Tools, Refusal
  rules, Output contract, Confirmation rules.
* [x] `agents/knowledge-agent/manifest.yaml` — github-mcp only, ceiling
  `write`, approval issue #242.
* [x] `agents/knowledge-agent/golden-tasks.md` — 1 happy-path + 2 failure-mode
  fixtures, each referencing FR/NFR IDs.

## Phase 4 — Protected governance edits (CODEOWNERS-gated)

* [ ] AGENTS.md — §1 registry row for `knowledge-agent` + workspace-skills
  table row for `document-authoring`; bump the AGENTS.md version header.
* [ ] `.github/copilot-instructions.md` — reference the `document-authoring`
  skill for docs changes; bump its version header.

## Phase 5 — Verification and PR

* [ ] `python scripts/lint/check_mojibake.py` → `OK` across the repo.
* [ ] `python scripts/lint/tests/test_check_mojibake.py` → 7 pass.
* [ ] `markdownlint-cli2` on every new/edited `*.md` → 0 errors.
* [ ] Stage only knowledge-agent-related files (exclude unrelated noise).
* [ ] Commit (Conventional Commits + `Co-authored-by` trailer).
* [ ] Open PR linking issue #242 with the full Superpowers contract body;
  request @urruegg CODEOWNERS review.

## Verification commands

```bash
python scripts/lint/check_mojibake.py
python scripts/lint/tests/test_check_mojibake.py
npx --yes markdownlint-cli2 "agents/knowledge-agent/*.md" "docs/superpowers/**/2026-07-17-knowledge-agent-*.md"
```
