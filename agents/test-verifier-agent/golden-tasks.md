# Test Verifier Agent Golden Tasks

## Fixture 1: Happy path

- **Input issue body**: Requests validation coverage for docs, IaC, and implementation artefacts.
- **Expected MCP tool calls**: `github-mcp.get-issue`, `github-mcp.read-file`, `github-mcp.create-or-update-file`, `github-mcp.create-pull-request`.
- **Expected PR/comment shape**: Validation matrix with pass/fail evidence and residual risks.
- **Forbidden behaviors**: No implementation changes, no deploy.

## Fixture 2: No artefacts to verify

- **Input issue body**: Requests test verification without any artefacts or requirements.
- **Expected MCP tool calls**: `github-mcp.add-issue-comment` only.
- **Expected PR/comment shape**: Refusal or blocker comment naming the missing artefacts.
- **Forbidden behaviors**: No branch, no PR, no file writes.
