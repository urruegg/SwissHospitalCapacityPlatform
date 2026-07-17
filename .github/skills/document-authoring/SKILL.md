---
name: document-authoring
description: >
  Use when creating or updating any Markdown document in this repository
  (docs/, docs/sprints/, docs/superpowers/, docs/adr/, .github/, AGENTS.md,
  README.md, sprint/spec/plan/design files) and before saving or committing
  that document. Use when a doc edit could touch the version header, FR/NFR
  traceability, recorded status, cross-doc links, or could introduce
  double-encoded UTF-8 (mojibake) or markdownlint failures. Triggers:
  "create a doc", "update the PRD", "write a sprint plan", "bump the doc
  version", "fix markdownlint", "fix mojibake", "is this doc traceable",
  "is the status accurate".
---

# Document Authoring (doc steward)

## Overview

Every document in this repo must be **encoding-clean, lint-clean,
correctly version-bumped, FR/NFR-traceable, status-accurate, and
link-valid — before it is saved**. The mechanical guarantees (mojibake,
markdown lint) are *automated* and are the real backstop; this skill
covers the **judgment** the automation cannot make.

* Mechanical guarantee (automated): `scripts/lint/check_mojibake.py`,
  `scripts/lint/fix_mojibake.py`, the `.githooks/pre-commit` gate, and the
  CI jobs `mojibake-scan` + `markdown-lint`.
* Judgment (this skill): which version component to bump, which FR/NFR IDs
  a change advances, whether recorded status still reflects reality, and
  when to update the PRD traceability matrix.

## When to use

* Authoring or editing any `*.md` under `docs/`, `.github/`, or the repo root.
* Bumping a document version header.
* Reconciling a doc's `Status` / progress claims with the real repo state.
* Deciding whether a change needs a new FR/NFR or a PRD §7 matrix update.

When **not** to use: pure code changes with no doc impact; generated files.

## Pre-flight gate (run in order, every time)

1. **Enable the local gate once per clone:** `git config core.hooksPath .githooks`.
2. **Encoding:** run `python scripts/lint/check_mojibake.py <files>`; if it
   reports findings, repair with `python scripts/lint/fix_mojibake.py <files>`.
   A line that must display a literal corrupt example carries a
   `mojibake-allow` marker.
3. **Lint:** run `npx --yes markdownlint-cli2 "<files>"` and fix residual
   errors. Common repo rules: MD004 bullets must be `*` (asterisk), MD040
   fenced blocks need a language, MD047 single trailing newline.
4. **Judgment checks (below):** version, traceability, status, links.
5. Only then stage and commit (Conventional Commits + `Co-authored-by` trailer).

## Version-bump judgment (copilot-instructions §9)

Bump the highest applicable level across all changes in the edit. Use the
three-component form; update `Version`, `Previous Version` (with a short
hint), and `Date` together.

| Level | Choose when the edit… |
| ----- | --------------------- |
| MAJOR `X.0.0` | renames/removes an ID other docs cite, reverses a recorded decision, or breaks an anchor/contract. **Requires an ADR.** |
| MINOR `x.Y.0` | adds sections/requirements/rows or changes meaning without breaking IDs or anchors. |
| PATCH `x.y.Z` | is editorial only: typos, formatting, lint/encoding fixes, reflow with no semantic change. |

New documents start at `1.0.0` with `Previous Version: n/a`.

## Traceability judgment

* If the change implements or advances behaviour, list the exact `FR-*` /
  `NFR-*` IDs from `docs/PRD.md` it touches.
* If it introduces a new requirement or shifts scope, add/adjust the row in
  `docs/PRD.md` §7 in the **same** edit (that is itself a MINOR PRD bump).
* Golden-task fixtures reference the requirement ID(s) they verify via the
  front-matter `requirement:` key.

## Status-accuracy judgment

Before writing "done", "complete", "deployed", or a checklist tick, confirm
it against reality (git state, CI result, resource evidence). If unverified,
write `partial:` or state the open item. Never let a `Status` header assert
more than the evidence supports.

## Quick reference

| Need | Command |
| ---- | ------- |
| Detect mojibake | `python scripts/lint/check_mojibake.py <files>` |
| Repair mojibake | `python scripts/lint/fix_mojibake.py <files>` |
| Lint (fix safe) | `npx --yes markdownlint-cli2 --fix "<files>"` |
| Lint (verify) | `npx --yes markdownlint-cli2 "<files>"` |
| Enable local gate | `git config core.hooksPath .githooks` |

## Common mistakes

* Editing a doc without bumping its version header (breaks the versioning
  contract in the PR gate).
* Marking status "done" from intent rather than verified evidence.
* Pasting content copied through a cp1252 console, reintroducing mojibake —
  always re-run the checker before saving.
* Using `-` bullets (MD004 wants `*`) or untagged code fences (MD040).
* Adding a requirement in prose but forgetting the PRD §7 matrix row.
