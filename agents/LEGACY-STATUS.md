# Legacy Agent Compatibility Status

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-10 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (archived legacy packs and added active stubs) |

## Purpose

Track legacy per-agent prompt assets after archive decommission for the
Superpowers-first execution model.

These assets are no longer the default operating path. Canonical legacy content
is stored under `agents-archive/` and compatibility stubs remain under `agents/`.
Legacy assets are kept for:

1. Compatibility verification.
2. Controlled rollback.
3. Historical traceability.

## Default Execution Policy

1. New issues use execution mode `superpowers`.
2. Legacy-agent mode is only for compatibility tests or rollback.
3. Governance controls in `AGENTS.md` and `.github/copilot/mcp.json` remain
   mandatory in all modes.

## Compatibility Inventory

| Asset | Status | Default | Notes |
| ----- | ----- | ----- | ----- |
| `agents-archive/orchestrator/AGENT.md` | archived | no | Canonical legacy source |
| `agents-archive/spec-parser-agent/AGENT.md` | archived | no | Canonical legacy source |
| `agents-archive/solution-design-agent/AGENT.md` | archived | no | Canonical legacy source |
| `agents-archive/landing-zone-agent/AGENT.md` | archived | no | Canonical legacy source |
| `agents-archive/compliance-agent/AGENT.md` | archived | no | Canonical legacy source |
| `agents-archive/data-design-agent/AGENT.md` | archived | no | Canonical legacy source |
| `agents-archive/app-builder-agent/AGENT.md` | archived | no | Canonical legacy source |
| `agents-archive/test-verifier-agent/AGENT.md` | archived | no | Canonical legacy source |
| `agents-archive/review-session-agent/AGENT.md` | archived | no | Canonical legacy source |
| `agents-archive/drift-analyzer/AGENT.md` | archived | no | Canonical legacy source |
| `agents/*/AGENT.md` | stub | no | Compatibility link only |
| `agents/*/golden-tasks.md` | stub | no | Compatibility link only |

## Decommission Preconditions

Before removing legacy assets:

1. One full sprint completed in Superpowers mode.
2. No critical governance regressions.
3. No open rollback blockers.
4. Explicit owner approval recorded in PR.
