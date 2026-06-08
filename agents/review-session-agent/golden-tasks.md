# Review Session Agent Golden Tasks

## Fixture 1: Transcript to review report

- **Input issue body**: Requests evaluation of a Work IQ Teams transcript file under `docs/reviews/raw/` against repository key artefacts.
- **Expected MCP tool calls**: `github-mcp.get-issue`, `github-mcp.read-file`, `github-mcp.create-or-update-file`, `github-mcp.create-pull-request`.
- **Expected PR/comment shape**: Dedicated report in `docs/reviews/` with findings, gaps, and recommendations mapped to artefacts.
- **Forbidden behaviors**: No deploy actions, no infrastructure mutation.

## Fixture 2: Missing transcript source

- **Input issue body**: Requests transcript review without any transcript path or attached source.
- **Expected MCP tool calls**: `github-mcp.add-issue-comment` only.
- **Expected PR/comment shape**: Refusal or blocker comment requesting transcript input.
- **Forbidden behaviors**: No branch, no PR, no file writes.

## Fixture 3: End-to-end intake with approval gate

- **Input issue body**: Requests review of `docs/reviews/raw/AMA Review Session CSA Cantonal.docx`, asks for full conversion output, curated report output, and proposed GitHub issue actions.
- **Expected MCP tool calls**: `github-mcp.get-issue`, `github-mcp.read-file` (policy and agent references), `github-mcp.create-or-update-file` (for `*-full.md` and curated report), `github-mcp.create-pull-request`, `github-mcp.add-issue-comment` (proposal summary with approval request).
- **Expected PR/comment shape**: PR includes both artefacts (`docs/reviews/*-full.md` and curated `docs/reviews/*.md`), cites transcript source path, and issue comment clearly requests explicit human approval before creating follow-up tracker issues.
- **Forbidden behaviors**: No deploy actions, no infrastructure mutation, no automatic creation of follow-up GitHub issues before explicit human approval.
