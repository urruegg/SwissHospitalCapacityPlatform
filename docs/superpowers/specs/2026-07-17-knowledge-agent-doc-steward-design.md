# Knowledge Agent — Documentation Steward — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-17 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | n/a (new — approved via issue #242) |
| **Approval issue** | [#242](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/242) |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution (ADR-0002) |

---

## 1. Goal and desired end state

Guarantee that **every Markdown document create/update in this repository is
encoding-clean, markdownlint-clean, correctly version-bumped, FR/NFR-traceable,
status-accurate, and link-valid — before it is saved or committed.**

Desired end state:

* A deterministic mojibake detector + repairer, unit-tested, wired into a
  pre-commit hook and CI.
* A judgment-focused `document-authoring` workspace skill.
* A governed `knowledge-agent` pack (prompt + manifest + golden tasks).
* All pre-existing mojibake in the repo remediated to zero.

## 2. Context and problem statement

Recurring CI failures were caused by (a) double-encoded UTF-8 (mojibake) leaking
into docs when content passed through a cp1252 console, and (b) markdownlint
violations discovered only after commit. Doc version headers and status claims
also drifted from reality. The fix must move these checks **left of save**, not
rely on post-commit CI alone.

The Superpowers `writing-skills` guidance is explicit: *mechanical constraints
should be automated (regex/validation), and documentation reserved for judgment
calls*. So the encoding + lint guarantees are code (Layer C), while the skill
(Layer A) documents only judgment (version bump, traceability, status).

## 3. Scope

### In scope

* Encoding integrity automation (detector, repairer, tests).
* Pre-commit hook + CI job (enforced backstop).
* `document-authoring` skill (judgment).
* `knowledge-agent` pack + AGENTS.md registry row.
* Remediation of existing mojibake debt.

### Out of scope

* Changing document *content* semantics beyond encoding/lint/version/status.
* Editing protected governance files beyond the AGENTS.md registry row and the
  copilot-instructions reference authorised by issue #242.
* Any deploy/delete or Azure resource change.

## 4. Architecture — three layers

| Layer | Artefact | Responsibility |
|-------|----------|----------------|
| **A. Skill (judgment)** | `.github/skills/document-authoring/SKILL.md` | Version-bump level, FR/NFR traceability, status reconciliation, ordered pre-flight gate. |
| **B. Agent (governed actor)** | `agents/knowledge-agent/{AGENT.md,manifest.yaml,golden-tasks.md}` | Applies the skill under refusal rules + `write` ceiling; opens PRs with a steward summary. |
| **C. Automation (the guarantee)** | `scripts/lint/check_mojibake.py`, `fix_mojibake.py`, tests, `.githooks/pre-commit`, `ci.yml` `mojibake-scan` | Deterministic, enforced encoding + lint gates — the real backstop for every author, human or agent. |

The guarantee lives in Layer C; A and B raise quality and add judgment but are
not the enforcement mechanism.

## 5. Mojibake detection and repair (Layer C detail)

* **Detection**: read as UTF-8; a run starts at a lead codepoint
  (`Ã` U+00C3, `Â` U+00C2, `â` U+00E2, `ð` U+00F0) followed by a continuation
  codepoint (Latin-1 supplement range plus the cp1252 special mappings). The
  `â` family is kept strict to avoid false positives on legitimate French text.
* **Repair**: for each detected run apply the inverse
  `run.encode("cp1252").decode("utf-8")`. All three sequences observed in this
  repo (section-sign, em-dash, u-umlaut families) round-trip with zero residual.
* **Suppression**: a line carrying a `mojibake-allow` marker is skipped so docs
  can show literal examples.

## 6. Side-effect posture and approval gates

* `knowledge-agent` ceiling is `write` (github-mcp only, already allow-listed →
  no `.github/copilot/mcp.json` change). No `approved-to-apply` gate.
* Protected-file edits (AGENTS.md row + copilot-instructions reference) are
  authorised by human issue #242 and require CODEOWNERS (@urruegg) PR approval.

## 7. Risk register

| Risk | Mitigation |
|------|------------|
| False positives flag legitimate accented text | Strict `â`-family rule; 7 unit tests assert no false positives on `Rüegg`, em-dash, arrow, guillemets. |
| Pre-commit hook not enabled by a dev | CI `mojibake-scan` is the enforced backstop; hook is opt-in convenience. |
| Windows Store `python3` stub misfires the hook | Hook falls back to `python`; CI runs on ubuntu with real `python3`. |
| Repairer corrupts content | Deterministic cp1252→utf-8 inverse, EOL-neutral read, verified by clean git diff on 93 fixes. |

## 8. Definition of done

* [ ] Detector + repairer + 7 unit tests, all passing.
* [ ] Repo scans clean (0 mojibake across tracked text files).
* [ ] Pre-commit hook blocks on mojibake and passes on clean (proven).
* [ ] CI `mojibake-scan` job added.
* [ ] `document-authoring` skill authored + AGENTS.md skills-table row.
* [ ] `knowledge-agent` pack with >= 1 happy + >= 1 failure golden task.
* [ ] AGENTS.md registry row + copilot-instructions reference (CODEOWNERS PR).
* [ ] PR opened linking issue #242 with the full Superpowers contract.

## 9. References

* Approval issue [#242](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/242)
* [ADR-0002 — runtime is GitHub Copilot coding agent](../../adr/0002-runtime-is-github-copilot-coding-agent.md)
* [copilot-instructions §9 — Document Versioning](../../../.github/copilot-instructions.md)
* [`document-authoring` skill](../../../.github/skills/document-authoring/SKILL.md)
* [`knowledge-agent` pack](../../../agents/knowledge-agent/AGENT.md)
