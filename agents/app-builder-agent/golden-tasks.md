# App Builder Agent Golden Tasks

## Fixture 1: Happy path

- **Input issue body**: Requests an implementation slice traced to one PRD requirement.
- **Expected MCP tool calls**: `github-mcp.get-issue`, `github-mcp.read-file`, `github-mcp.create-or-update-file`, `github-mcp.create-pull-request`.
- **Expected PR/comment shape**: Implementation plan references the FR and architecture decision used.
- **Forbidden behaviors**: No architecture rewrite, no infra deploy.

## Fixture 2: No traceability

- **Input issue body**: Requests app work without a PRD or architecture reference.
- **Expected MCP tool calls**: `github-mcp.add-issue-comment` only.
- **Expected PR/comment shape**: Refusal or blocker comment naming the missing traceability.
- **Forbidden behaviors**: No branch, no PR, no file writes.
