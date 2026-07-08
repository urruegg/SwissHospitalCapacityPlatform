# Sprint 10 M4-A — Verifier Extension + CI Workflows Evidence

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-08 |
| **Author** | Urs Rüegg |
| **Status** | PASS |
| **Previous Version** | n/a (initial) |

**Milestone:** M4-A of the [Sprint 10 completion strategy](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md#m4--tooling--close-out--t7-hygiene).
**Charter deliverables:** S10.11 (verifier extension), T7 H3 (lifecycle workflow OIDC fix), T7 H4 (sim-capacity CI).

## Outcome

**PASS.** Three pure-additive tooling changes shipped in one PR — no approvals required, no destructive actions. Verifier extension asserts measure + role counts (would have caught Sprint 09's silent role drop); lifecycle workflow's OIDC bug fixed by mirroring PR #130 pattern; sim-capacity image build workflow closes the ADR-0019 follow-up gap where local `docker build` was the only path.

## 1. S10.11 — Verifier extension for measures + roles

Extended [`data-platform/scripts/export_semantic_model_tmdl.ps1`](../../../../data-platform/scripts/export_semantic_model_tmdl.ps1) with a new `Test-MeasureAndRoleContract` function that counts:

- **Measure blocks** across `definition/tables/*.tmdl` (via `^\s*measure\s+` pattern)
- **Role files** under `definition/roles/*.tmdl` (one role per file per TMDL convention)

Then asserts against expected constants:

```powershell
$script:ExpectedTotal    = 16    # Sprint 09: 14; +2 from M2 (encounter/bed_assignment → dim_hospital)
$script:ExpectedInactive = 2
$script:ExpectedMeasures = 11
$script:ExpectedRoles    = 4
```

Existing relationship contract (14 → **16**) was also bumped for the 2 new M2 relationships.

Verifier run locally (`./export_semantic_model_tmdl.ps1 -VerifyOnly`):

```text
Verifying relationship contract under: ./data-platform/reports/capacity-dashboard.SemanticModel
  Total:    16  (expected 16)
  Active:   14
  Inactive: 2  (expected 2)
OK: 16/14-Active/2-Inactive contract holds.

Verifying measure + role contract under: ./data-platform/reports/capacity-dashboard.SemanticModel
  Measures: 11  (expected 11)
  Roles:    4  (expected 4)
OK: 11 measures + 4 roles contract holds.
```

**Why this matters:** Sprint 09's portal round-trip silently dropped 4 role scaffolds. If this verifier had been in place, the CI merge gate would have caught `Role count 0 != expected 4` and blocked the commit. M4-A ships the verifier; **M4-C** adds the CI workflow (S10.12) that runs it as a required check.

**Measure inventory** (11 total across 5 tables):

- `dim_ward_capacityunit`: Beds Total
- `or_case`: Over-Run Minutes, OR Utilization %, Data Quality Score (Cases)
- `or_schedule`: Idle-Slot Minutes
- `encounter`: Active Encounters, Admissions, Discharged, Currently In Hospital
- `bed_assignment`: Currently Assigned Beds, Occupancy %

**Role inventory** (4 total under `definition/roles/`): BedOps, ORPlanner, Analyst, SemanticOwner.

## 2. T7 H3 — Fix `fabric-capacity-lifecycle.yml` OIDC

Mirrored the [PR #130](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/130) fix pattern applied to `fabric-sit-keepalive.yml`:

| Change | Before | After |
| ------ | ------ | ----- |
| Job-level `environment:` scope | absent (job had no env context) | `environment: name: ${{ inputs.environment }}` |
| `tenant-id` source | `${{ secrets.AZURE_TENANT_ID }}` | `${{ vars.AZURE_TENANT_ID }}` |
| `subscription-id` source | `${{ secrets.AZURE_SUBSCRIPTION_ID }}` | `${{ vars.AZURE_SUBSCRIPTION_ID }}` |
| `client-id` source | `${{ secrets.AZURE_CLIENT_ID }}` | unchanged (client-id stays as secret) |

Without the env scope, GitHub Actions couldn't resolve environment-scoped variables (`vars.AZURE_TENANT_ID`, `vars.AZURE_SUBSCRIPTION_ID`) — the workflow would fail at the `az login` step. Also, `tenant-id`/`subscription-id` are non-sensitive identifiers configured as environment `vars`, not `secrets`; the previous config mismatched the actual GitHub environment setup.

Change is targeted at the `azure/login` step — the `Ensure PowerShell available` and `Invoke ...` steps are unchanged.

## 3. T7 H4 — `ci-build-sim-capacity.yml` workflow

Added [`.github/workflows/ci-build-sim-capacity.yml`](../../../../.github/workflows/ci-build-sim-capacity.yml) — rebuilds + pushes the sim-capacity container image on `apps/sim-capacity/**` changes.

**Trigger:** `push` to `main` filtered to `apps/sim-capacity/**` + `workflow_dispatch` for manual re-builds.

**Job:** `build-and-push` in `sit` environment, uses SIT OIDC (same SP that already has AcrPush via Contributor scope on `rg-ihzhhpf-sit`).

**Image tags pushed:**

- `cri75lbu5sj4hza.azurecr.io/sim-capacity:<short-sha>` — immutable, git-traceable
- `cri75lbu5sj4hza.azurecr.io/sim-capacity:latest` — mutable, convenience

**Scope decision (documented in workflow comments):** builds + pushes only. Does **not** bump `simCapacityContainerImage` in `infra/environments/sit.bicepparam` — image tag bumps are a deliberate manual review step. The workflow summary tells the operator exactly which tag to use in the Bicep bump.

**Why this matters:** Before M4-A, the only path to update sim-capacity was `docker build` locally + `docker push`. That worked but was error-prone (wrong tag, wrong registry). CI now guarantees every merged code change has a corresponding image build without human intervention.

## Verification

- Verifier: local run passes both contracts (relationship + measure/role) — output captured above
- Lifecycle workflow: static diff review against PR #130 pattern — no manual dispatch executed to avoid touching capacity SKU without approval
- Sim-capacity workflow: syntax validated by GitHub Actions parser at commit time; **first run will happen on the merge itself** (M4-A touches `.github/workflows/` not `apps/sim-capacity/`, so the workflow won't fire on this PR — that's correct behavior)

## Sprint 10 M4-A exit criteria

- [x] `export_semantic_model_tmdl.ps1` extended with measure + role count assertions (S10.11)
- [x] Local verify passes both contracts
- [x] `fabric-capacity-lifecycle.yml` OIDC bug fixed (T7 H3)
- [x] `ci-build-sim-capacity.yml` workflow added with SIT OIDC + ACR push (T7 H4)
- [x] No approvals required (all changes are pure-additive tooling)
- [x] Evidence report v1.0.0 committed

## Rollback

- Revert this branch's merge commit — all three files revert to their pre-M4-A state
- No lakehouse data, semantic model, or Azure resource impact

## Follow-ups (M4-B, M4-C)

- **M4-B**: destructive T7 items — H1 (delete stale branch), H2 (sunset keep-alive + close #126), H5 (vestigial EH decision), H6 (F16→F2 downscale). Each needs `approved-to-apply`.
- **M4-C**: S10.12 `verify-semantic-model.yml` CI merge gate wiring the S10.11 verifier + T6 sprint retrospective + evidence pack close-out.

## References

- [Sprint 10 completion strategy §M4 + §T7](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md#m4--tooling--close-out--t7-hygiene)
- [PR #130](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/130) — original OIDC fix for keep-alive workflow (T7 H3 pattern source)
- [ADR-0019](../../../adr/0019-fabric-custom-endpoint-eventstream-ingestion.md) — Custom Endpoint pivot that introduced the sim-capacity container (T7 H4 origin)
- [M3-A evidence](m3-a-rls-roles.md) — 4 roles now assertable via verifier extension
