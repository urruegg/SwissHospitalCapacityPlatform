# Sprint 34 — Curavias Documentation Alignment — Plan 1 (WS-0 Foundations)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |
| **Design** | [Sprint 34 doc-alignment design](../specs/2026-07-28-sprint-34-doc-alignment-design.md) |
| **Work package** | [#506](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/506) (WS-0 foundations) |
| **Tracker** | [#505](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/505) |

> **Scope of this plan:** WS-0 only — the frozen foundations every other
> workstream builds against: the shared glossary, the customer-ready doc
> template, and the canonical mermaid diagram library. WS-1..4 (per-doc
> application by lane) are **separate follow-on plans** proposed after WS-0
> merges. Documentation-only: no code, no infra, no ADR change.

---

## Foundations

- **Design:** [`2026-07-28-sprint-34-doc-alignment-design.md`](../specs/2026-07-28-sprint-34-doc-alignment-design.md)
  — read §5 (WS-0), §6 (terminology), §7 (template), §8 (diagram library) before
  starting.
- **Precedent to mirror:** `docs/CURAVIAS-PRODUCT-STATUS.md` (Curavias anchor +
  product doctrine), `.github/copilot-instructions.md §9` (version bumps),
  the `document-authoring` skill (judgment layer).
- **Gates (run on every doc touched):**
  `python scripts\lint\check_mojibake.py <files>` then
  `npx --yes markdownlint-cli2 "<files>"` then
  `npx --yes markdown-link-check <files>`. All must pass.
- **Encoding rule:** author with the `create`/`edit` tools or UTF-8 no-BOM writes.
  Do NOT use PowerShell `Set-Content`/`Get-Content` on non-ASCII content (it
  double-encodes em dashes / §). Commit with the doc-steward hook active; use
  `git -c core.hooksPath=/dev/null` only if the hook blocks a known-clean file.

## Definition of done (WS-0)

- `docs/GLOSSARY.md` exists: defines Curavias, Fabric IQ, Foundry IQ, Work IQ,
  Copilot IQ, Frontier Firm, agent boss, human-agent ratio, medallion,
  advisory-only; includes the reusable product-anchor line and the doc-template
  convention.
- `docs/architecture/diagram-library.md` exists: the 5 canonical mermaid diagrams
  (system context, medallion data flow, agent topology/orchestration,
  deployment/region, key sequence), each with an `embed in: <docs>` note; every
  mermaid block renders (valid mermaid syntax).
- All new/edited docs pass mojibake + markdownlint + link-check.
- SemVer headers correct; commit messages follow Conventional Commits.

## Tasks

### Task 1 — Author `docs/GLOSSARY.md`

- **Test first:** write a tiny presence/format check (or a documented manual
  checklist in the PR) asserting the glossary defines each required term and
  contains the product-anchor line and the template convention. If a script is
  used, place it under `scripts/lint/` and keep it ASCII-only.
- Author the glossary per design §6: one approved definition per term; the
  one-line product anchor; the customer-ready template convention (§7).
- **Verify:** gates green; every required term present.

### Task 2 — Author `docs/architecture/diagram-library.md`

- Author the 5 canonical mermaid diagrams per design §8, each in its own fenced
  mermaid code block, each preceded by a short caption and followed by an
  `Embed in: <docs>` note.
- Keep diagrams factually consistent with ARCHITECTURE / INFRASTRUCTURE /
  CURAVIAS-PRODUCT-STATUS (as-deployed vs target-GA; ADR-0013/0032 regions).
- **Verify:** gates green; each mermaid block is valid (renders without syntax
  error — check via a mermaid linter or GitHub preview).

### Task 3 — Capture the customer-ready doc template

- Add the standardized template (title convention, version header, product-anchor
  blockquote, executive-summary convention) as a copy-pasteable block in
  `docs/GLOSSARY.md` (or a short `docs/DOC-TEMPLATE.md` if cleaner) so WS-1..4
  copy it verbatim.
- **Verify:** the block is self-contained and passes gates.

### Task 4 — WS-0 gate + PR

- Run all three gates across `docs/GLOSSARY.md`, `docs/architecture/diagram-library.md`,
  and any template doc; fix findings.
- Open ONE small squash PR (branch `sprint-34/ws-0-foundations`) linked to the
  WS-0 issue. Do not touch the 16 in-scope docs yet — that is WS-1..4.
- Never self-merge; wait for green required checks; a human merges.

## After WS-0 merges

Propose follow-on plans in sequence (design §12): WS-3 (README hero,
CURAVIAS-PRODUCT-STATUS, PRD, BVA, SD), then WS-2 (ARCHITECTURE, INFRASTRUCTURE,
DATA, ALM_PLAN), WS-1 (SECURITY, COMPLIANCE, AI), WS-4 (OPERATIONS, TEST,
DEV_WORKFLOW, AGENTS). Each is its own plan -> issue -> small squash PR. WS-3 also
adds the `NFR-DOC-001..004` rows to PRD §7.
