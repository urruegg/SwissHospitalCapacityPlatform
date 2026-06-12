<!-- markdownlint-disable MD041 -->
## Summary

<!-- 1–3 sentences: what changed and why. -->

## Linked Issue / Work Item

<!-- e.g., Closes #123 -->

- Parent sprint issue: `#...` (required)
- Delivery issue for this PR: `#...` (required)

> Traceability rule: every PR must link to at least one sprint-scoped GitHub
> issue, and every sprint issue must be closed by one or more linked PRs.

## Requirements Implemented

> **Required** by [NFR-GOV-006](../docs/PRD.md#55-governance--compliance-nfr-gov-).
> List every PRD requirement ID this PR advances. Use `partial:` if the
> requirement is not fully verified by this PR.

- `FR-...`: `<one-line description>`
- `NFR-...`: `<one-line description>`

## Sprint Context

- Sprint: `S<N>` — sprint file: `docs/sprints/sprint-<N>-<name>.md`
- User stories: `S<N>-<n>`, …
- Sprint issue link: `#...` (required)

## Execution Mode

<!-- Required during Superpowers cutover. -->

- [ ] `superpowers` (default)
- [ ] `legacy-agent-compat`

## Skill Applicability and Evidence

<!-- Required by Superpowers Skills System policy. -->

- [ ] `writing-plans` applicable and evidence linked
- [ ] `test-driven-development` applicable and evidence linked
- [ ] `systematic-debugging` applicable and evidence linked
- [ ] `verification-before-completion` applicable and evidence linked

Non-applicable rationale (required for every unchecked skill):

- `writing-plans`: ...
- `test-driven-development`: ...
- `systematic-debugging`: ...
- `verification-before-completion`: ...

Evidence links:

- Planning artifact or issue comment: ...
- Test or validation output: ...
- Debug log or incident analysis (if applicable): ...
- Final verification output: ...

Legacy mode approval issue: `#...` (required only if `legacy-agent-compat` is checked)

## Validation Evidence

<!-- Commands executed + outcomes. Paste tail of relevant output. -->
- [ ] `npx --yes markdownlint-cli2 "**/*.md" "#node_modules"` (markdown lint)
- [ ] `lychee docs/**/*.md docs/sprints/*.md .github/*.md AGENTS.md README.md` (link check; same scope as CI)
- [ ] `az bicep build --file infra/main.bicep` / `az deployment group what-if ...` (if `infra/**` changed — UC1 outputs)
- [ ] Superpowers execution evidence attached, or golden-task replay attached for legacy-agent compatibility mode

## Eval Impact

<!-- For prompt, agent-contract, or MCP allow-list changes only. -->
- Golden tasks affected: …
- Pass-rate before → after: …
- Replay log link (issue/PR comment or workflow run): …

## API Impact

<!-- New/changed MCP tool contracts, agent prompts, issue templates, or workflow_dispatch inputs. State "none" if none. -->

## Infrastructure Impact

<!-- Bicep modules added/changed under `infra/` (UC1 outputs); `what-if` summary. State "none" if none — the platform itself has no infra (per ADR-0002). -->

## Security Impact

<!-- New MCP servers added to `.github/copilot/mcp.json`, RBAC implied, secrets, network changes for UC1 outputs. State "none" if none. -->

## Data Impact

<!-- Cosmos DB containers, partition keys, retention, PII — applies only to UC1 outputs that include a customer-side data store; the platform itself stores nothing (per ADR-0002). State "none" if none. -->

## Documentation Updated

- [ ] `docs/PRD.md` (traceability matrix §7 updated if new requirement or scope change)
- [ ] `docs/<relevant>.md` (architecture, security, data, infra, AI, ALM)
- [ ] `docs/sprints/sprint-NN-*.md` (acceptance criteria reflected)
- [ ] `docs/adr/*.md` (if a cross-cutting decision was made)
- [ ] Runbooks (`docs/runbooks/*.md`) if operational behavior changed

## Residual Risks / Open Questions

<!-- Anything reviewers should look at first. -->

---

### Reviewer Checklist (carried from [.github/copilot-instructions.md §7](../.github/copilot-instructions.md#7-code-review-checklist))

- [ ] CI checks pass (markdown lint, link check, Bicep build/validate where applicable, security scan, golden-task replay where applicable)
- [ ] Where code exists, coverage ≥ 80 % on changed files; otherwise markdown lint + Bicep validate + golden-task replay satisfy the gate (per ADR-0002)
- [ ] No hard-coded secrets, subscription IDs, tenant IDs, URLs, or resource names
- [ ] Any new MCP server added to `.github/copilot/mcp.json` has CODEOWNERS approval and documented purpose + required permissions
- [ ] Commit messages follow Conventional Commits
- [ ] Requirements section above is complete and references valid PRD IDs
- [ ] Traceability matrix in `docs/PRD.md` §7 is consistent
- [ ] Every edited doc has its **Version** header bumped per [`.github/copilot-instructions.md` §9](../.github/copilot-instructions.md#9-document-versioning)
