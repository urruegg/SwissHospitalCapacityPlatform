# Agents Folder — Structure Status

| Field | Value |
| ----- | ----- |
| **Version** | 2.0.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.1.0 (archived legacy packs and added active stubs; superseded by the 2.0.0 restructure) |

## Purpose

Document the state of the `agents/` folder after the 2.0.0 folder restructure
(2026-07-09). Retained for anyone tracing the history of the old
`agents-archive/` folder.

## Current state (2.0.0 restructure)

All agent packs live directly under `agents/<name>/` as the **single source
of truth**. Each pack contains:

- `AGENT.md` — the canonical prompt (8 sections per the Sprint 11 template).
- `manifest.yaml` — the runtime manifest loaded by the Sprint 13 Container
  Apps agent-host (Sprint 11 packs) or consumed by the GitHub Copilot coding
  agent (platform-control-plane packs).
- `golden-tasks.md` — acceptance fixtures replayed by
  [`.github/workflows/eval-goldens.yml`](../.github/workflows/eval-goldens.yml).

**Note**: `fabric-data-agent` (Sprint 09 v2 read-only ontology query surface)
is retained without a Sprint 11-shape `manifest.yaml` / `golden-tasks.md`
pending a separate ADR-0008 posture reconciliation.

## What changed in 2.0.0

1. **Retired `agents-archive/`** — all 18 packs consolidated into `agents/`.
2. **Deleted 17 compatibility stubs** — the pointer-only `agents/<name>/AGENT.md`
   files that previously redirected to `agents-archive/`.
3. **Superseded 2 Sprint 09 legacy bodies**:
   - `agents/bm-copilot/` — replaced by the application-hosted `bmca-agent`
     (Sprint 11 per ADR-0008).
   - `agents/csa-agent/` (Sprint 09 v2 body) — replaced by the Sprint 11
     scaffold (full body lands in Sprint 16).
4. **MAJOR bump on `AGENTS.md`** (1.15.0 → 2.0.0) — registry link anchors
   change from `agents-archive/<name>/...` to `agents/<name>/...`; any external
   consumer that hard-linked to the archive paths must update.

## Historical bodies (accessible via git log)

The following files existed under `agents-archive/` prior to the 2.0.0
restructure and can be recovered from git history:

1. `agents-archive/orchestrator/AGENT.md` and 9 other platform-control-plane
   packs — now at `agents/<name>/AGENT.md`.
2. `agents-archive/{bmca,ooa,dca,orsa,sba,csa,data-quality,onboarding}-agent/`
   Sprint 11 packs — now at `agents/<name>/`.

The following files were retired and are only available via git log:

1. `agents/bm-copilot/AGENT.md` and `golden-tasks.md` (Sprint 09 v2 T4.2
   Foundry-hosted BM-Copilot; replaced by `agents/bmca-agent/`).
2. `agents/csa-agent/AGENT.md` and `golden-tasks.md` (Sprint 09 v2 T4.4
   Foundry-hosted CSA; replaced by `agents/csa-agent/` Sprint 11 scaffold).

## Default Execution Policy

1. New issues use execution mode `superpowers`.
2. Legacy per-agent invocation via `@<agent-name>` mentions or issue templates
   remains supported for compatibility tests or rollback.
3. Governance controls in [`AGENTS.md`](../AGENTS.md) and
   [`.github/copilot/mcp.json`](../.github/copilot/mcp.json) remain mandatory
   in all modes.
