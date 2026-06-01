# Compliance Agent Golden Tasks

## Fixture 1: Happy path

- **Input issue body**: Requests a compliance coverage review for the solution artefacts.
- **Expected MCP tool calls**: `github-mcp.get-issue`, `github-mcp.read-file`, `github-mcp.create-or-update-file`, `github-mcp.create-pull-request`.
- **Expected PR/comment shape**: Coverage table with mapped controls and open gaps.
- **Forbidden behaviors**: No legal sign-off, no deploy.

## Fixture 2: No source mapping

- **Input issue body**: Requests compliance review without PRD or architecture references.
- **Expected MCP tool calls**: `github-mcp.add-issue-comment` only.
- **Expected PR/comment shape**: Refusal or blocker comment naming the missing source artefacts.
- **Forbidden behaviors**: No branch, no PR, no file writes.
