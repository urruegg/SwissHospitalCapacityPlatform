# Sprint 06 PR Evidence Checklist Template

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Define the per-phase PR evidence fields required for Sprint 06, covering FR, NFR,
and CH controls, gate outcomes, and residual risks. This is the Phase 0 control
artifact for Phase 0 task 3 of
[`sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`](../sprint-06-minimal-data-onboarding-and-capacity-specialty.md).
It extends — and does not replace — the repository
[`.github/PULL_REQUEST_TEMPLATE.md`](../../.github/PULL_REQUEST_TEMPLATE.md);
authors paste the block below into the PR description for every Sprint 06 phase PR.

## How to Use

1. **Open the PR as a draft first** (draft-PR-first execution contract), then fill
   the evidence block as work progresses.
2. Copy the [Evidence Block](#evidence-block) into the phase PR description.
3. Fill every field. Use `partial:` for requirements not fully verified by the PR.
4. Mark gate outcomes as `pass`, `fail`, `n/a`, or `pending`.
5. Link to the relevant rows in
   [`requires-validation-register.md`](requires-validation-register.md) that the
   PR closes or advances.
6. Confirm the gate order matches [`gate-sequence.md`](gate-sequence.md).

## Evidence Block

```markdown
### Sprint 06 Phase Evidence

#### Phase Context

- Phase issue: #<phase-issue>  (see sprints/sprint-06/phase-issue-map.md)
- Phase: <0|1|2|3|4>
- Onboarding lane(s): <patient-minimum|specialty-capacity|both>
- Provider scope: <none|hirslanden|zollikerberg|both>

#### FR Controls Impacted

- `FR-ONB-00x`: <one-line description> — <full|partial>

#### NFR Controls Impacted

- `NFR-...-00x`: <one-line description> — <full|partial>

#### CH Controls Impacted

| CH Control | Description | Owner role | Evidence link |
| ----- | ----- | ----- | ----- |
| `CH-C0x` | <control> | <ARCH|SEC|OPS|LEGAL> | <link> |

#### Requires-Validation Register Items

| RV ID | Action in this PR | New status |
| ----- | ----- | ----- |
| RV-06-0x | <closed|advanced|deferred> | <open|in-validation|validated|deferred> |

#### Commands / Checks Executed

- [ ] `npx --yes markdownlint-cli2 "**/*.md" "#node_modules"` — outcome: <pass|fail>
- [ ] `lychee docs/**/*.md sprints/*.md sprints/**/*.md .github/*.md AGENTS.md README.md` — outcome: <pass|fail>
- [ ] synthesized-data contract / schema validation (Phase 1+) — outcome: <pass|fail|n/a>
- [ ] onboarding policy / schema gate (Phase 2+) — outcome: <pass|fail|n/a>
- [ ] provider SIT dataset validation (Phase 3) — outcome: <pass|fail|n/a>

#### Gate Outcomes

| Gate | Required | Outcome | Evidence link |
| ----- | ----- | ----- | ----- |
| CI gate | yes | <pass|fail|pending> | <link> |
| SIT gate | yes | <pass|fail|n/a|pending> | <link> |
| PROD gate | <yes|no> | <pass|fail|n/a|pending> | <link> |
| Runtime gate | <yes|no> | <pass|fail|n/a|pending> | <link> |

#### Approvals (PROD promotion only)

| Role | Approver handle | Timestamp | Decision |
| ----- | ----- | ----- | ----- |
| ARCH | @ | | <approved|blocked> |
| SEC | @ | | <approved|blocked> |
| OPS | @ | | <approved|blocked> |
| LEGAL (re-identification / cantonal) | @ | | <approved|blocked|n/a> |

#### Residual Risks

| Risk | Severity | Owner role | Mitigation | Expiry | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| <risk> | <high|medium|low> | <ARCH|SEC|OPS|LEGAL> | <mitigation> | <YYYY-MM-DD> | <accepted|open> |

#### Definition of Done Confirmation

- [ ] Phase Definition of Done (sprint file) satisfied or explicitly deferred
- [ ] No unresolved high-severity register item for this phase left undocumented
- [ ] MVP Phase 1 scope kept locked to OOA/DCA/BMCA (optional agents deferred to Phase 3)
- [ ] Every edited doc has its Version header bumped (copilot-instructions §9)
```

## Field Rules

1. **FR / NFR / CH coverage is mandatory.** Every Sprint 06 PR must list at least
   one `FR-ONB` or `NFR` ID and map any compliance impact to a `CH-C0x` control,
   matching the traceability anchors in
   [`requires-validation-register.md`](requires-validation-register.md).
2. **Draft PR first.** Each phase opens its PR as a draft before evidence is
   collected; the PR is marked ready-for-review only when its gate row evidence
   is attached.
3. **Gate outcomes are mandatory and ordered.** No PROD gate row may read `pass`
   unless the SIT gate row for the same PR reads `pass` (see
   [`gate-sequence.md`](gate-sequence.md)).
4. **Minimum-sensitive-data is enforced.** Onboarding PRs must confirm minimized
   field sets and purpose tags; no PR introduces unminimized quasi-identifiers
   without a recorded `RV-06-04` re-identification assessment.
5. **Residual risks must be explicit.** Empty residual-risk tables are not allowed;
   use a single row stating `none` with severity `low` if there are genuinely no
   residual risks.
6. **Exceptions** carry an explicit expiry (max 90 days for critical governance
   exceptions).
7. **Approvals echo handle and timestamp** for any deploy/delete-ceiling action,
   per `AGENTS.md` §4.
