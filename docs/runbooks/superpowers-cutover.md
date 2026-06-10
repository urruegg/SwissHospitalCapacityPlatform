# Superpowers Cutover Runbook

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-10 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (completed legacy pack archival and stub rollout) |

## Purpose

Define the migration from repository-defined per-agent execution to a
Superpowers-first development workflow using GitHub Copilot CLI.

This runbook preserves governance controls already established in the
repository and only replaces the execution methodology.

## Scope

In scope:

1. Copilot CLI + Superpowers setup.
2. Issue and PR template updates for Superpowers-first operation.
3. Operational documentation updates.
4. Legacy agent artifact transition strategy.

Out of scope:

1. Removing approval gates for deploy/delete.
2. Relaxing MCP allow-list controls.
3. Changing compliance traceability requirements.

## Control Baseline (Must Keep)

The following controls remain authoritative after cutover:

1. MCP allow-list and permissions in [.github/copilot/mcp.json](../../.github/copilot/mcp.json).
2. Deploy and delete human approval phrase `approved-to-apply` in [AGENTS.md](../../AGENTS.md)
   and deployment workflows.
3. PR evidence and traceability contract in [.github/PULL_REQUEST_TEMPLATE.md](../../.github/PULL_REQUEST_TEMPLATE.md).
4. Quality gates in [docs/TEST.md](../TEST.md).
5. CODEOWNERS protections in [.github/CODEOWNERS](../../.github/CODEOWNERS).

## Target Operating Model

1. Superpowers is the default execution mode.
2. Legacy per-agent prompts are archived under `agents-archive/`; `agents/`
   now hosts compatibility stubs.
3. Governance and policy files remain repository-native and mandatory.

## Migration Phases

### Phase 1: Prepare

1. Confirm Copilot CLI version and plugin support.
2. Install Superpowers on developer workstations:

```bash
copilot plugin marketplace add obra/superpowers-marketplace
copilot plugin install superpowers@superpowers-marketplace
```

3. Confirm that issue/PR templates encode evidence and approval requirements.

### Phase 2: Enable

1. Update execution playbook to Superpowers-first.
2. Update issue templates to remove hard dependency on legacy agent routing
   labels and prompt text.
3. Add explicit execution mode selection with `superpowers` as default.

### Phase 3: Observe

1. Run one sprint with Superpowers as default for new work.
2. Track these indicators:
   - PR cycle time
   - Validation pass rate
   - Number of blocked runs due to missing evidence
   - Number of approval-gate violations (target: zero)

### Phase 4: Decommission Legacy Paths (completed)

1. Archive legacy per-agent prompt folders under `agents-archive/`.
2. Keep and retarget the golden-task structural workflow as legacy compatibility validation.
3. Maintain compatibility stubs under `agents/` to prevent broken references during transition.

## Exit Criteria

The cutover is complete when all are true:

1. New issues default to Superpowers execution mode.
2. No required process depends on per-agent routing labels.
3. Safety gates remain enforced and auditable.
4. One full sprint completes without governance regression.

## Rollback Plan

If governance or delivery quality regresses:

1. Switch issue templates back to legacy agent routing labels.
2. Restore legacy execution wording in [agents/README.md](../../agents/README.md).
3. Re-run validation workflow set and review blocked items.
4. Continue migration only after corrective actions are merged.

## Evidence Checklist

For each migration PR:

1. Requirements IDs listed.
2. Validation commands and outcomes attached.
3. Security/compliance impact statement provided.
4. Residual risk and rollback path documented.
