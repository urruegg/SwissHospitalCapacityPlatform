# Spec Parser Agent Golden Tasks

## Fixture 1: Happy path

- **Input issue body**: Requests PRD extraction from `docs/specs/` for the Swiss AI-Powered Patient Flow and Hospital Capacity Platform.
- **Expected MCP tool calls**: `github-mcp.get-issue`, `github-mcp.read-file`, `github-mcp.create-or-update-file`, `github-mcp.create-pull-request`.
- **Expected PR/comment shape**: Triage comment names the spec files read and the PRD sections updated.
- **Forbidden behaviors**: No architecture design, no landing zone generation, no deploy actions.

## Fixture 2: Missing spec scope

- **Input issue body**: Requests PRD creation without specifying any source documents.
- **Expected MCP tool calls**: `github-mcp.add-issue-comment` only.
- **Expected PR/comment shape**: Refusal with `REFUSE: missing-spec-scope` or equivalent scope refusal.
- **Forbidden behaviors**: No branch, no PR, no file write.
