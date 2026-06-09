# Sprint 05 PR Evidence Checklist Template

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Define the per-phase PR evidence fields required for Sprint 05, covering FR, NFR,
and CH controls, gate outcomes, and residual risks. This is the Phase 0 control
artifact for Phase 0 task 3 of
[`sprints/sprint-05-caf-waf-mvp-sit-prod.md`](../sprint-05-caf-waf-mvp-sit-prod.md).
It extends — and does not replace — the repository
[`.github/PULL_REQUEST_TEMPLATE.md`](../../.github/PULL_REQUEST_TEMPLATE.md);
authors paste the block below into the PR description for every Sprint 05 phase PR.

## How to Use

1. Copy the [Evidence Block](#evidence-block) into the phase PR description.
2. Fill every field. Use `partial:` for requirements not fully verified by the PR.
3. Mark gate outcomes as `pass`, `fail`, `n/a`, or `pending`.
4. Link to the relevant rows in
   [`requires-validation-register.md`](requires-validation-register.md) that the
   PR closes or advances.
5. Confirm the gate order matches [`gate-sequence.md`](gate-sequence.md).

## Evidence Block

```markdown
### Sprint 05 Phase Evidence

#### Phase Context

- Phase issue: #<phase-issue>  (see sprints/sprint-05/phase-issue-map.md)
- Phase: <0|1|2|3|4>
- Work package(s): <WP-01..WP-06>
- Impacted architecture lanes: <governance|platform-control|infrastructure|data|ai|experience>

#### FR Controls Impacted

- `FR-...`: <one-line description> — <full|partial>

#### NFR Controls Impacted

- `NFR-...`: <one-line description> — <full|partial>

#### CH Controls Impacted

| CH Control | Description | Owner role | Evidence link |
| ----- | ----- | ----- | ----- |
| `CH-C0x` | <control> | <ARCH|SEC|OPS|LEGAL> | <link> |

#### Requires-Validation Register Items

| RV ID | Action in this PR | New status |
| ----- | ----- | ----- |
| RV-0x | <closed|advanced|deferred> | <open|in-validation|validated|deferred> |

#### Commands / Checks Executed

- [ ] `npx --yes markdownlint-cli2 "**/*.md" "#node_modules"` — outcome: <pass|fail>
- [ ] `lychee docs/**/*.md sprints/*.md sprints/**/*.md .github/*.md AGENTS.md README.md` — outcome: <pass|fail>
- [ ] policy / CI checks (Phase 2+) — outcome: <pass|fail|n/a>
- [ ] DR rehearsal / restore proof (Phase 3) — outcome: <pass|fail|n/a>
- [ ] golden-task replay (Phase 4 / agents changed) — outcome: <pass|fail|n/a>

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
| LEGAL (cantonal) | @ | | <approved|blocked|n/a> |

#### Residual Risks

| Risk | Severity | Owner role | Mitigation | Expiry | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| <risk> | <high|medium|low> | <ARCH|SEC|OPS|LEGAL> | <mitigation> | <YYYY-MM-DD> | <accepted|open> |

#### Definition of Done Confirmation

- [ ] Phase Definition of Done (sprint file) satisfied or explicitly deferred
- [ ] No unresolved high-severity register item for this phase left undocumented
- [ ] Every edited doc has its Version header bumped (copilot-instructions §9)
```

## Field Rules

1. **FR / NFR / CH coverage is mandatory.** Every Sprint 05 PR must list at least
   one FR or NFR ID and map any compliance impact to a `CH-C0x` control, matching
   the CAF/WAF review traceability matrix (§10) and the sprint Evidence Requirements.
2. **Gate outcomes are mandatory and ordered.** No PROD gate row may read `pass`
   unless the SIT gate row for the same PR reads `pass` (see
   [`gate-sequence.md`](gate-sequence.md)).
3. **Residual risks must be explicit.** Empty residual-risk tables are not allowed;
   use a single row stating `none` with severity `low` if there are genuinely no
   residual risks.
4. **Exceptions** carry an explicit expiry (max 90 days for critical governance
   exceptions) per the hardening delta exception-management baseline.
5. **Approvals echo handle and timestamp** for any deploy/delete-ceiling action,
   per `AGENTS.md` §4.
