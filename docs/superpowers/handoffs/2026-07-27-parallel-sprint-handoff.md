# Parallel-Sprint Session Handoff — 2026-07-27

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-27 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | — (supersedes the 2026-07-26 snapshot) |

> **Purpose**: End-of-day point-in-time snapshot to pause and later resume the
> coordinator session **and** the parallel sprint sessions from a documented
> state. Not a durable contract — regenerate/replace on the next break. The
> durable how-to lives in [`parallel-session-runbook.md`](parallel-session-runbook.md).

## 1. Baseline

- `main` HEAD at snapshot: **`80c4826`** (PR #431) — app CI green
  (`ci`, `app-a11y`, `app-e2e`, `app-build`, `ci-build-app-fluent` all success).
- **Infra deploys both GREEN**: last `cd-infra-deploy-sit` and
  `cd-infra-deploy-prod` succeeded on `4ba8485` (SIT 14:44, PROD 17:40 on
  2026-07-26). The app-only PRs after that (`#430`, `#431`) do not trigger the
  infra lane.
- **Zero open PRs.** 18 PRs merged this cycle (`#413`–`#431`; see §4).
- Trunk-based, short-lived branches; **a human reviews and merges every PR**
  (agents never self-merge). Wait for green **required** checks before merging;
  never admin-merge a red PR.
- Windows quirks: use `python` (not `python3`); the pre-commit mojibake hook
  false-fails — verify with `python scripts/lint/check_mojibake.py` then commit
  with `git -c core.hooksPath=/dev/null commit`. Windows Terminal treats `;` as a
  tab separator even inside a passed `-Command`; spawn sessions via a wrapper
  `.ps1` + `-File`.

## 2. Main-health pins (coordinator-owned — DO NOT re-flip in sprint PRs)

State on `main` as verified this snapshot. Sprint streams may rebase onto these
but must not change them:

- `sit.bicepparam`: `poAgentOpenAiLocation = 'eastus2'`,
  `enablePoAgentRuntimeModule = true`. **Changed since 2026-07-26** — the SIT
  PO-Agent runtime was re-enabled (`false` → `true`) once the
  **gpt-5 / 2025-08-07 / GlobalStandard** model config settled; eastus2 has the
  OpenAI GlobalStandard gpt-5 quota, `westus2` does not.
- `prod-swn.bicepparam`: `enablePoAgentRuntimeModule = true`.
- `prod.bicepparam`: `enablePoAgentRuntimeModule = false`.
- **PO-Agent model on `main`**: gpt-5 / 2025-08-07 / GlobalStandard — do not
  reintroduce gpt-4o or a `westus2` OpenAI location.
- **Public website decommissioned**: the `curavias-web` infra module and its
  `enableCuraviasWebModule` toggle have been **removed entirely** (supersedes the
  2026-07-26 `enableCuraviasWebModule = false` pin). Only the Curavias app
  remains. Aligns with ADR-0044 / issue #268.

## 3. Open PRs

**None.** All parallel-stream PRs from this cycle are merged. The coordinator
review queue is clear.

## 4. What merged this cycle (`#413`–`#431`)

| Sprint / lane | PRs merged | Landed slice |
|---------------|-----------|--------------|
| **Sprint 29** (#399, context architecture) | #413 (M1 conversation scope), #416 (M2 default board), #418 (M3 envelope propagation), #420 (M4 Foundry thread-per-user×agent), #421 (M5 OBO/RLS contract + ADR-0052), #423 (M6 FR/NFR-CTX in PRD) | **Complete through m6-closeout.** Live-SIT lift tracked as follow-up #424. |
| **Sprint 23** (#255, org/skills spine) | #415 (CustomEndpoint SAS publisher), #419 (Container Apps sim job), #425 (SIT↔PROD bicepparam parity harness), #428 (accept ADR-0050) | Active. |
| **Sprint 26** (#335, decision ontology) | #417 (target Foundry Agent Service /agents API), #422 (pin decision-apply image), #429 (seed_live idempotency runbook fix) | Active. |
| **Sprint 27** (#365, Curavias UX polish) | #426 (SIT-test intermediate), #430 (ORSA + SBA two-lane redesign), #431 (DCA two-lane redesign) | Active. |
| **Governance** (#378) | #414 (renumber ADR-0040→0050, ADR-0021→0051) | Partial; ADR-0043 collision deferred (see §6). |

## 5. Active worktrees / sessions

From `git worktree list`. Each session owns its slice and its own `plan.md`.
**All streams: rebase/merge `main` (`80c4826`) before pushing.**

| Worktree | Branch | Next step |
|----------|--------|-----------|
| `SwissHospitalCapacityPlatform` (main workdir) | coordinator | Main-health, review triage, spinning streams up/down. |
| `wt/sprint-23-org-skills-refactor` | `sprint-23/accept-adr-0050` | Remaining #255 items. |
| `wt/sprint-26-decision-ontology` | `sprint-26/ws-b-barrier-gold` | Sprint 26 WS-B barrier/gold slice. Issue #335. |
| `wt/sprint-27-curavias-ux-polish` | `sprint-27/curavias-ux-polish` | Continue Curavias app UX polish; route visual/a11y via `ux-design-agent`. Issue #365. |
| `wt/sprint-28-product-owner-agent` | `sprint-28/enable-sit-po-runtime` | PO-Agent SIT runtime enablement. Next: publish the real PO-Agent container image (#427). Issue #377. |
| `wt/sprint-29-foundry-iq-context` | `sprint-29/m6-closeout` | Sprint 29 delivered; close out and hand the live-SIT lift to #424. Issue #399. |
| `wt/runbook-autoapprove` | `docs/runbook-per-worktree-autoapproval` | Per-worktree auto-approval runbook doc. |

## 6. Open issues (carried into tomorrow)

**Sprint trackers (active):**

- `#399` Sprint 29 context architecture — code complete (m6); close after #424 is
  scoped.
- `#377` Sprint 28 PO Agent · `#365` Sprint 27 UX polish · `#335` Sprint 26
  decision ontology · `#255` Sprint 23 org/skills spine.

**New follow-ups opened this cycle:**

- `#427` Publish the real PO-Agent container image (replace SIT + PROD
  placeholder).
- `#424` Sprint 29 follow-up: lift context architecture to live SIT (envelope
  send path, Foundry threads, Fabric RLS, OBO).
- `#407` Wire PROD Fabric Data Agent grounding (`ca-agent-host-ihzhhpf-prod`).

**Governance / carried:**

- `#378` ADR-number collisions — **partial-resolved** (0040 + 0021 done). Left
  **open** for the deferred **ADR-0043** collision
  (`0043-preview-tier-...` vs `0043-product-owner-agent-...`): its refs touch the
  governance-protected `AGENTS.md` and the live Sprint 23 (#255) / Sprint 28
  (#377) branches. Follow-up hygiene PR once those land — reserved 0045–0049 stay
  free until then.
- `#296` CsaView golden-source divergence (folded into Sprint 29, `lane:experience`).
- `#290` External signal triage handoff (poller bridge) — coordinator triaged;
  awaiting a close-vs-keep decision.
- `#270` PROD Fabric IQ ontology creation blocked (`FeatureNotAvailable` on PROD
  capacity) — **blocked**, external Azure gate, monitor only.

## 7. Standing protocol for every stream

1. **Sync first.** Before pushing or marking ready:
   `git fetch origin && git merge origin/main`. Resolve conflicts toward the
   config on `main` (see §2 pins).
2. **Green before ready.** Mark a PR *Ready for review* only when all required
   checks pass. A red draft stays draft.
3. **Human merges.** Never self-merge or admin-merge. The coordinator triages
   ready+green PRs and hands them to the human.
4. **One issue → one branch → one squash-merge PR → delete branch/worktree.**
   No stacks; base every branch on `main`.
5. **Deploy/delete is hard-gated** by `approved-to-apply` + human execution
   (AGENTS.md §4).
6. **Don't touch coordinator-owned main-health pins** (§2).

## 8. How to resume tomorrow

Coordinator start: read this handoff, then run `git worktree list`,
`gh pr list --state open`, `gh issue list --state open` to refresh live state.

Per-stream resume: see
[`parallel-session-runbook.md`](parallel-session-runbook.md) §3 (START) and §5
(establish a new stream).
