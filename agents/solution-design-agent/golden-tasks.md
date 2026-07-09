# Solution Design Agent Golden Tasks

## Fixture 1: Happy path

- **Input issue body**: Requests solution architecture from an approved PRD.
- **Expected MCP tool calls**: `github-mcp.get-issue`, `github-mcp.read-file`, `github-mcp.create-or-update-file`, `github-mcp.create-pull-request`.
- **Expected PR/comment shape**: Architecture update with explicit logical layers and MVP boundaries.
- **Forbidden behaviors**: No IaC creation, no app code, no deploy.

## Fixture 2: PRD gap

- **Input issue body**: Requests architecture while PRD is still placeholder content.
- **Expected MCP tool calls**: `github-mcp.add-issue-comment` only.
- **Expected PR/comment shape**: Refusal or blocker comment naming the missing PRD sections.
- **Forbidden behaviors**: No branch, no PR, no file writes.
