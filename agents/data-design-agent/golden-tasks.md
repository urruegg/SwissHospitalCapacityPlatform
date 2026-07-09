# Data Design Agent Golden Tasks

## Fixture 1: Happy path

- **Input issue body**: Requests a data model and data platform design based on the PRD and architecture.
- **Expected MCP tool calls**: `github-mcp.get-issue`, `github-mcp.read-file`, `github-mcp.create-or-update-file`, `github-mcp.create-pull-request`.
- **Expected PR/comment shape**: Data model summary with entities, relationships, and design assumptions.
- **Forbidden behaviors**: No physical deployment, no app code.

## Fixture 2: Missing upstream artefacts

- **Input issue body**: Requests data design without PRD or architecture inputs.
- **Expected MCP tool calls**: `github-mcp.add-issue-comment` only.
- **Expected PR/comment shape**: Refusal or blocker comment naming the missing upstream artefacts.
- **Forbidden behaviors**: No branch, no PR, no file writes.
