# Design: Issue #571 — PROD Corpus Search Index Remediation

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-08-11 |
| **Author** | GitHub Copilot (autonomous session, user delegated design authority) |
| **Status** | Approved (autonomous — user unavailable for live review; see §7) |
| **Previous Version** | n/a (new document) |

## 1. Problem

PROD's Azure AI Search service (`srch-ihzhhpf-prod`) exists, but its index
(`idx-curavias-corpus-ihzhhpf-prod`) does not. This blocks
`caj-po-refresh-ihzhhpf-prod` — the daily Container Apps Job that snapshots
the repo, chunks/tags/publishes documents through the PHI gate, and uploads
`GroundedChunk` documents into the index. `refresh_job.py`'s `upload_chunks()`
POSTs to `.../indexes/idx-curavias-corpus-ihzhhpf-prod/docs/index` and 404s
because the index was never created. This is tracked as
[issue #571](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/571)
and is the top open item from the prior session
(`docs/superpowers/specs/2026-08-11-bva-evidence-sprint-design.md` §11).

## 2. Root cause

Azure AI Search indexes are **not** ARM/Bicep-managed resources — there is no
`Microsoft.Search/searchServices/indexes` ARM type; index schemas are created
imperatively via the Search data-plane REST API
(`PUT {endpoint}/indexes/{name}?api-version=...`). Bicep in this repo only
provisions the search **service** (`infra/modules/.../ai-search`); the index
itself is a separate, manual step.

`data-platform/scripts/po-agent/corpus/create_search_index.py` already exists
for exactly this purpose:

- `build_index_definition(index_name)` — pure function, returns the index
  schema (mirrors the frozen `GroundedChunk` v1 contract: `id`, `classId`,
  `text`, `citation.sourceRef`/`citation.anchor`, `asOf`, `liveness`,
  `status`, `confidence`, `language`).
- `put_index(endpoint, index_name, ...)` — PUTs that schema using AAD bearer
  auth (`DefaultAzureCredential`, scope `https://search.azure.com/.default`).
  A PUT to an existing index name updates it in place, so this is idempotent
  and safe to re-run.
- Already covered by `tests/test_create_search_index.py` (schema shape +
  REST call assertions).

SIT's index exists only because this script was run manually, once, during
the Sprint 42 remediation
(`docs/superpowers/plans/2026-08-08-sprint-42-po-agent-sit-remediation.md`).
That runbook step was never repeated for PROD, and **no CI workflow calls
this script for either environment today** (confirmed via repo-wide search —
the only reference to running it is a manual runbook instruction). This is a
process gap, not a code defect: the tool that fixes this already exists and
is already tested.

## 3. Approaches considered

**A. Manual one-time fix only.** Run `create_search_index.py` against PROD
now. Minimal effort, unblocks the job immediately. Leaves the same
silent-gap risk if PROD's search service is ever rebuilt (e.g. disaster
recovery, environment recreation) — nobody would find out until the refresh
job started failing again.

**B. Fix now + wire into CI permanently.** Same immediate fix, plus add an
idempotent "ensure corpus index exists" step to both
`cd-infra-deploy-sit.yml` and `cd-infra-deploy-prod.yml` so this class of bug
cannot silently recur. This requires granting the CI OIDC identity a new RBAC
role (`Search Service Contributor` or a narrower built-in/custom role) on
each search service — a security-relevant change to what a CI/CD service
principal is allowed to do, and by this repo's own operating rules that is
the kind of "modifies shared infrastructure" action that warrants explicit
human sign-off rather than an unsupervised grant.

**C. Detect-and-alert only.** Add a read-only check (e.g. to a future PROD
verify step) that flags a missing index without creating it. Rejected: it
doesn't actually fix the job, and the user explicitly asked for the problem
fixed with end-to-end evidence, not just better visibility into it.

## 4. Decision

Split the work by what is safe to do unsupervised versus what genuinely
needs a human decision, consistent with this repo's operational-safety rules
(RBAC/security-posture changes to shared CI infrastructure require
confirmation; running an already-tested idempotent script under my own
already-authorized session does not):

1. **Do now:** Run `create_search_index.py` against PROD using my own
   interactively-authenticated Azure session (no new permissions granted to
   any service principal — this uses access I already have). Then verify
   end-to-end (§5).
2. **Recommend, don't silently implement:** The CI-wiring half of Approach B
   (permanent regression-proofing) needs a new RBAC grant for the CI
   identity. I will document the exact change needed and open a follow-up
   GitHub issue for it, rather than run `az role assignment create` against
   a CI/CD service principal unsupervised. This keeps today's fix scoped to
   what issue #571 actually asks for, while leaving a clear, actionable trail
   for the systemic improvement.

## 5. Verification plan (end-to-end evidence)

1. `PUT` the index via `create_search_index.py` (`AZURE_SEARCH_ENDPOINT`,
   `AZURE_SEARCH_INDEX` pointed at PROD) → expect success (idempotent PUT).
2. `GET .../indexes/idx-curavias-corpus-ihzhhpf-prod` → confirm the schema
   matches SIT's index field-for-field.
3. `az containerapp job start` on `caj-po-refresh-ihzhhpf-prod` → poll the
   job execution to completion → expect a successful exit and
   `"refresh_job: uploaded N GroundedChunks"` in the logs (N > 0).
4. `GET .../indexes/.../docs/$count` → expect count > 0.
5. Live HTTP call against PROD's `po-agent-service` Class A query path →
   confirm a real grounded citation is returned instead of an empty/error
   result.
6. Post the evidence (index schema, job run id/log excerpt, doc count, live
   query result) as a comment on issue #571 and close it.

## 6. Out of scope

- CI/RBAC wiring implementation — tracked as a new follow-up issue, not
  implemented in this pass.
- Any change to the index's field schema (Class A keyword-only schema is
  unchanged and already approved per the Sprint 42 scope decision recorded
  in `create_search_index.py`'s module docstring).
- SIT (already working; not touched by this fix).

## 7. Approval note

The user is unavailable this turn and delegated: *"work autonomously and
make good decisions."* Per the brainstorming skill, a design must still be
presented and "approved" before implementation — here that approval is the
standing delegation applied to a narrowly-scoped, low-risk, reversible
action (running an existing idempotent script) plus a deliberately
conservative choice (not expanding CI/CD RBAC without a live human decision).
This document is committed for the user's review at the start of the next
session, per this repo's `document-authoring` conventions.
