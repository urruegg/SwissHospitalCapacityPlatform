# Sprint 10 M4-B — T7 Hygiene Recommendations & Actions

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-08 |
| **Author** | Urs Rüegg |
| **Status** | PASS (H1/H2/H6 executed with approval, H5 deferred with Sprint 11 tracking issue recommendation) |
| **Previous Version** | n/a (initial) |

**Milestone:** M4-B of the [Sprint 10 completion strategy](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md#5-t7-hygiene-track-new).

## Outcome

**PASS.** 3 of 4 destructive T7 items executed with explicit `approved-to-apply`:

- **T7 H6** — Fabric capacity F16 → **F4** (user chose F4 over F2 for CU headroom). Silver notebook validated on F4 in 102s (vs 92s on F16 — +10s / +11% negligible).
- **T7 H2** — Keep-alive workflow `.github/workflows/fabric-sit-keepalive.yml` deleted; issue #126 closed with pointer to this evidence.
- **T7 H1** — Stale branch `sprint-10/t1-s10.1-eventstream-deploy` (dangling commits `40cfc61` + `d35ce00`, superseded by PR #129) deleted from origin.
- **T7 H5** — Vestigial Azure Event Hub — **deferred to Sprint 11 with tracking issue** per ADR-0019's 30-day observation criterion (see §H5 recommendation below).

## T7 H6 — Fabric F16 → F4 downscale

**Executed:** `az fabric capacity update -g rg-ihzhhpf-sit -n fabricihzhhpfsit --sku "{name:F4,tier:Fabric}"` → `provisioningState=Succeeded`, `state=Active`, new SKU F4.

**Validation:** re-ran the silver notebook (job `6c66ac0c-9989-4807-8b17-c418bdf8ff86`) — completed in **102s** vs the F16 baseline of 92s (M1.5). No queueing, no CU-exhaustion errors, all 3791 rows promoted.

**Cost impact (list price, pay-as-you-go, westus2):**

| SKU | CU | Monthly (24×7) | Saving vs F16 |
| --- | -- | -------------- | ------------- |
| F16 | 16 | ~USD 1,730 | baseline |
| F4  |  4 | ~USD 432   | **~USD 1,300/mo** |
| F2  |  2 | ~USD 216   | ~USD 1,514/mo (not chosen — thin CU margin for silver) |

F4 chosen (not F2) per user preference for CU headroom that keeps notebook queueing risk low.

**Rollback:** `az fabric capacity update -g rg-ihzhhpf-sit -n fabricihzhhpfsit --sku "{name:F16,tier:Fabric}"` — instant, reversible.

## T7 H2 — Keep-alive workflow sunset

**Executed:** `Remove-Item .github/workflows/fabric-sit-keepalive.yml` (in this branch).

The keep-alive was Sprint 10 T1's mid-session override that resumed the F2 capacity every 15 min if paused. Sprint 10 T1 is complete (M1..M4-A shipped, capacity is `Active` and staying that way on F4). Keep-alive is no longer needed.

**Issue #126** (`Sprint 10 T1 close: remove Fabric SIT keep-alive workflow`) will be closed on this PR merge with `Closed by PR #<n>` reference.

**Rollback:** revert this PR's commit — the file returns and the schedule resumes.

## T7 H1 — Stale branch deletion

**Executed:** `git push origin --delete sprint-10/t1-s10.1-eventstream-deploy` → `[deleted]`.

Branch tip was `d35ce00f` (workflow-issue mid-session commit) — superseded by PR #129 which took the Bicep-deploy path instead. No dangling PRs referenced it.

**Rollback:** `git push origin d35ce00f:refs/heads/sprint-10/t1-s10.1-eventstream-deploy` if we somehow need it back — the ref history is preserved locally in reflog and remotely in Actions logs.

## T7 H5 — Vestigial Event Hub recommendation

**Not executed (recommendation only).** Recommend **Sprint 11 tracking issue** with the 30-day observation criterion from ADR-0019.

### Context

`evh-ihzhhpf-sit-y26y` (Event Hub namespace) and its child hub + 4 consumer groups + `id-sim-capacity-eh-sender-sit` MI role assignments were provisioned pre-ADR-0019 for the original Azure Event Hub ingestion path. After ADR-0019 pivoted ingestion to Fabric Custom Endpoint, the EH namespace has been idle (verified: 0 incoming messages since 2026-07-08 08:00Z per Azure Monitor).

Cost: Basic tier EH namespace ≈ USD 11/mo — negligible, but not zero.

### Recommendation: Sprint 11 issue with 30-day watch period

**Rationale:**

1. **ADR-0019 sunset criterion** — the ADR explicitly says vestigial Azure infra stays for a "30-day observation period" after Custom Endpoint go-live to allow rollback if the pivot proves unreliable
2. **Custom Endpoint has ~8 hours of observation** — well under the 30-day threshold
3. **Fabric preview stability risk (OPS-RISK-03)** — Direct Lake + Custom Endpoint are still preview features. Keeping the EH warm-standby costs USD 3 for the observation window ($11/mo × 8 days / 30) — cheap insurance
4. **Deletion is fully non-reversible** — recreating an EH namespace with the same DNS name is not guaranteed (Azure may recycle the name)

### Concrete recommended action for Sprint 11

Open a Sprint 11 tracking issue with body:

```
Title: T7 H5 sunset — delete evh-ihzhhpf-sit-y26y after ADR-0019 30-day observation

Body:
- ADR-0019 go-live: 2026-07-08
- Delete-ready date: 2026-08-07 (D+30)
- Pre-delete verification checklist:
  - [ ] Custom Endpoint ingestion has zero downtime events in Azure Monitor since D+0
  - [ ] Fabric Eventstream `es-capacity-events-sit` has produced non-zero rows in `dbo.bronze_eventstream_raw` daily for 30 days
  - [ ] No consumer or app is reading from `evh-ihzhhpf-sit-y26y/eh` (Azure Monitor `IncomingMessages` = 0)
- Delete command (approved-to-apply gate):
    az eventhubs namespace delete -g rg-ihzhhpf-sit -n evh-ihzhhpf-sit-y26y
- Bicep param cleanup:
    - infra/environments/sit.bicepparam — remove any `eventHubNamespace/hub/consumerGroup` params if still referenced
    - infra/modules/*.bicep — remove the vestigial module includes
- Role assignment cleanup:
    - id-sim-capacity-eh-sender-sit MI — remove Azure Event Hubs Data Sender role assignment
    - Delete the MI itself if not used elsewhere
```

Estimated Sprint 11 effort: 1 hour (verification + `approved-to-apply` + destructive az calls + Bicep cleanup + PR).

### Alternative (rejected)

Delete now to save USD 11 × 1 month = USD 11 in observation-period cost. Rejected because (a) the 30-day window is an ADR gate we shouldn't bypass, (b) preview-feature risk is real (OPS-RISK-03), (c) $11 is negligible.

## Sprint 10 M4-B exit criteria

- [x] T7 H6 F16→F4 downscale executed + validated (silver 102s)
- [x] T7 H2 keep-alive workflow file deleted (issue #126 closed on merge)
- [x] T7 H1 stale branch deleted from origin
- [x] T7 H5 recommendation authored (defer to Sprint 11 issue with 30-day watch)
- [x] Evidence report v1.0.0 committed

## Follow-ups (M4-C)

- S10.12 `verify-semantic-model.yml` CI merge gate wiring the S10.11 verifier
- T6 Sprint 10 retrospective + evidence pack + Sprint 09 v2 DoD final updates + sprint-close checklist

## References

- [Sprint 10 completion strategy §T7](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md#5-t7-hygiene-track-new)
- [ADR-0019](../../../adr/0019-fabric-custom-endpoint-eventstream-ingestion.md) — 30-day observation criterion for vestigial EH
- [M1.5 evidence](m1-5-silver-hardening.md) — F16 92s baseline for silver validation comparison
- [M4-A evidence](m4-a-verifier-and-ci.md) — the workflow OIDC fix pattern that PR #130 established (referenced by H2's keep-alive counterpart)
- Issue #126 — closed by this PR
