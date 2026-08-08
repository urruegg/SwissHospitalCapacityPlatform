---
Version: 1.1.0
Date: 2026-08-08
Author: Copilot coding agent (autopilot, delegated)
Status: Draft
Previous Version: 1.0.0 (corrected ST-3 mechanism from a hypothesised Bicep `Microsoft.Search/indexes` child resource to the repo's existing REST-script convention, found while grounding the implementation plan)
---

# Sprint 42 — Product Owner Agent SIT Root-Cause Remediation — Design

> Produced via the Superpowers `brainstorming` skill, following the Sprint 41
> WS-0 audit ([`2026-08-08-sprint-41-ws0-audit-findings.md`](2026-08-08-sprint-41-ws0-audit-findings.md)).
> User confirmed scope interactively (one combined design, all 3 root
> causes + a guardrail sub-task) after two rounds of real Q&A, not
> autopilot-approved.

## 1. Context

Sprint 41 shipped a real `po-agent-service`, deployed it to SIT, and proved
the wire contract end-to-end — but the live smoke-test correctly `refused`
every question, because the WS-0 audit found every one of the four
knowledge classes blocked by an environment gap, not a code gap:

| Class | Root cause |
| ----- | ---------- |
| A (corpus) | Corpus-refresh job (`caj-po-refresh-ihzhhpf-sit`) still runs the placeholder image; zero Search index documents exist. |
| B (live-proof) | MI has no subscription-scope `Reader` role for Resource Graph. |
| C (cost) | MI has no `Cost Management Reader` role. |
| D (ontology) | MI has no **Fabric workspace role** on `f3af9733-9503-4e92-98f9-a901d96f1c87` (the actual access gate for the published Fabric Data Agent endpoint — **not** an ARM role on a Cognitive Services account, a correction from the original audit). |
| (all) | The runtime container's env vars (`SEARCH_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`, ...) don't match what the Python code reads (`AZURE_SEARCH_ENDPOINT`, `AZURE_SUBSCRIPTION_ID`, `FABRIC_DATA_AGENT_ENDPOINT`, ...). |

This sprint closes every gap and adds a guardrail so the env-var class of
drift (silently broken for 13 days before anyone noticed) can't recur
unnoticed.

## 2. Goals

1. A real question against the SIT `po-agent-service` returns a genuinely
   grounded, cited answer (`refused: false`) for at least one class,
   ideally all four.
2. Every fix is **infra-as-code or scripted-and-idempotent** — no manual
   portal clicks, no untracked `az` commands run once and forgotten.
3. A regression test/CI check exists that would have caught the env-var
   mismatch before it shipped.

## 3. Non-goals

- PROD promotion — stays out of scope, needs its own separate
  `approved-to-apply` per Sprint 41's own risk callout.
- Changing the Python client code (`data-platform/scripts/po-agent/**`) —
  Sprint 41 already tested it against a frozen contract; this sprint makes
  the *environment* match that contract, not the other way around.
- Building a full Fabric-permissions management system — one narrow,
  reusable script for this one grant, not a general-purpose tool.

## 4. Sub-task designs

### ST-1 — Env-var contract fix (Bicep)

**File:** `infra/modules/experience-hosting/po-agent-runtime/main.bicep`

Add/rename the runtime container's `env` block entries:

| Current (wrong) | Fixed |
| ---------------- | ----- |
| `SEARCH_ENDPOINT` | `AZURE_SEARCH_ENDPOINT` |
| *(missing)* | `AZURE_SEARCH_INDEX` — new param `poAgentSearchIndexName`, default `po-agent-corpus` |
| *(missing)* | `AZURE_SUBSCRIPTION_ID` — `subscription().subscriptionId`, no new param needed |
| *(missing)* | `FABRIC_DATA_AGENT_ENDPOINT` / `FABRIC_WORKSPACE_ID` / `FABRIC_DATA_AGENT_ID` — new params, threaded from `sit.bicepparam`/`prod.bicepparam`'s **existing** `fabricDataAgentEndpoint`/`fabricDataAgentId` values (same ones `agent-host` already uses; workspace id is the path segment already embedded in the endpoint, e.g. `f3af9733-9503-4e92-98f9-a901d96f1c87`) |

`AZURE_OPENAI_ENDPOINT`, `COSMOS_ENDPOINT`, `KEY_VAULT_URI` stay as-is — the
orchestrator's own answer-synthesis/audit-store wiring, not part of the
Class A–D contract, no code reads a different name for these today.

### ST-2a — Class B + C: ARM RBAC (Bicep)

**File:** same module. Two new conditional role-assignment resources,
matching the existing `searchReaderRole`/`openAiUserRole` pattern exactly
(scoped, not wildcard):

- `Reader` (built-in role `acdd72a7-3385-48ef-bd42-f606fba81ae7`) at
  **subscription scope** — Resource Graph has no narrower scope.
- `Cost Management Reader` (built-in role
  `72fafb9e-0641-4937-9268-a91bfd8191a3`) at **subscription scope** — Cost
  Management is billing-scoped, same reasoning.

Both gated behind a new `bool` param (default `true`) so they can be
disabled per-environment if ever needed, mirroring `useAcrMiPull`'s
existing pattern in the same file.

### ST-2b — Class D: Fabric workspace role (script, not Bicep)

**New file:** `data-platform/scripts/fabric/grant_po_agent_workspace_role.py`

Fabric workspace role assignments are not ARM resources — they're a Fabric
REST API concept (`POST /v1/workspaces/{id}/roleAssignments`). Mirrors the
auth pattern already proven in
`data-platform/scripts/fabric/add_data_agent_source.py` (bearer token via
`DefaultAzureCredential`, `https://api.fabric.microsoft.com/.default`
scope). Idempotent: `GET` existing role assignments first, skip if the PO
agent's principal already has a role, otherwise `POST` a `Viewer` grant
(read-only, matches Class D's read-only design) for principal
`cf4a8863-f671-47f7-b25a-9ed63c86c8da` on workspace
`f3af9733-9503-4e92-98f9-a901d96f1c87`. Documented as a post-deploy step
(mirrors `infra/modules/data-platform/fabric/post-deploy/` convention) —
run manually after any Bicep apply that changes the PO agent's MI, not a
GitHub Actions push-time step (matches this repo's "Fabric REST access is
never a push-time gate" convention seen elsewhere).

### ST-3 — Class A pipeline

**Correction found while grounding the plan:** this repo already has a
documented convention for this exact resource
(`infra/modules/knowledge-layer/foundry-iq-knowledge-base/knowledge-base-rest.md`):
Azure AI Search indexes here are **REST-script-provisioned, not a Bicep
child resource** (no ARM sub-resource type is used for this in the
existing pattern). ST-3 turns that runbook's manual curl steps into an
idempotent script instead, rather than inventing a new Bicep resource.

**Files:**
- `data-platform/scripts/po-agent/corpus/create_search_index.py` (new) — a
  real, idempotent (`PUT` = create-or-update) script implementing the
  runbook's Step 1, with a field schema mirroring the frozen `GroundedChunk`
  contract (`data/synthetic/schema/grounded-chunk-v1.schema.json`) exactly,
  including a nested `citation` complex field so `search_client.py`'s
  `query_corpus` (already tested, unchanged) reads it back correctly.
- `data-platform/scripts/po-agent/corpus/refresh_job.py` (new) — the CLI
  entrypoint the Container Apps Job actually runs: reads the corpus landing
  storage via `snapshot.py`, tags via `chunk_tag.py`, PHI-gates + maps to
  `GroundedChunk` via `publish.py` (all pre-existing, tested), then uploads
  into the real index.
- `data-platform/scripts/po-agent/corpus/Dockerfile` +
  `.github/workflows/po-agent-corpus-build.yml` (mirrors
  `po-agent-runtime-build.yml` exactly).
- Bump `caj-po-refresh-ihzhhpf-sit`'s image the same **surgical**
  way Sprint 41 bumped the runtime service (`az containerapp job update`,
  not a full Bicep deploy) — same drift-avoidance reasoning applies.
- Trigger one manual run (`az containerapp job start`), re-check the index
  document count (Finding 2's query), confirm > 0.

### ST-4 — Guardrail

**New file:** `data-platform/scripts/po-agent/runtime/tests/test_env_contract.py`

A single source of truth: a `REQUIRED_ENV_VARS` list literal in `app.py`
(or a small sibling module) naming every env var `get_tools()` reads. The
guardrail test:

1. Parses `infra/modules/experience-hosting/po-agent-runtime/main.bicep`
   (via `az bicep build --stdout` to ARM JSON, already an available CLI
   step in this repo) and extracts the container's declared `env[].name`
   values.
2. Asserts every name in `REQUIRED_ENV_VARS` is present in that set.

Runs in the existing `python -m pytest data-platform/scripts/po-agent/`
sweep — no new CI workflow needed, it's a plain unit test that shells out
to `az bicep build` (offline, no Azure credentials required, since
`bicep build` only compiles the template, it doesn't query Azure).

## 5. Verification gates

- `python -m pytest data-platform/scripts/po-agent/ -v` — new + existing
  tests green (ST-2b's script gets its own unit tests with a fake HTTP
  client, same injectable pattern as everything else in this sprint).
- `az bicep build --file infra/modules/experience-hosting/po-agent-runtime/main.bicep`
  — compiles clean.
- `az deployment group what-if` on the **module scope only** (not the full
  `main.bicep`) where possible, else the same surgical
  `az containerapp update`/`az containerapp job update` approach Sprint 41
  used, to avoid re-absorbing the unrelated drift already documented.
- Live re-test: `POST /answer` against SIT returns `refused: false` with
  ≥ 1 real citation for at least Class D (closest to ready) after ST-1 +
  ST-2b land; full four-class success needs ST-2a + ST-3 too.
- `python scripts/lint/check_mojibake.py` + `markdownlint-cli2` on every
  doc touched.

## 6. Risks / open items

- **Assumption:** the PO agent's MI (`cf4a8863-...`) currently has zero
  Fabric workspace role — not directly confirmed (only `gh-oidc-ihzhhpf`,
  a different identity, was confirmed to have one). ST-2b's script checks
  this itself before granting (idempotent), so this is safe either way.
- **Assumption:** `Microsoft.Search/indexes` as a Bicep child resource is
  supported for this Search SKU/API version — needs a quick `az bicep`
  schema check at execution time; if unsupported, fall back to a
  deployment-script-based index creation (same idempotent-script pattern
  as ST-2b) rather than blocking the sprint.
- **Risk:** all of ST-1/2a/2b/3's fixes are additive/idempotent and
  SIT-only, but still touch a shared Bicep module and grant real
  permissions — each still needs the same `approved-to-apply` discipline
  Sprint 41 used, sub-task by sub-task, not a single blanket approval.

## 7. Traceability

- Supersedes the "Follow-up required" list in
  [`2026-08-08-sprint-41-ws0-audit-findings.md`](2026-08-08-sprint-41-ws0-audit-findings.md)
  — this design is the concrete remediation for every item there.
- No new `FR-*`/`NFR-*` IDs — this closes gaps against Sprint 28's existing
  `FR-POA-*`/`NFR-POA-*` families.
