# `.github/agents/` — VS Code custom agent personas

These are **VS Code Copilot Chat custom agent modes** (`*.agent.md`), sourced
from [github/awesome-copilot](https://github.com/github/awesome-copilot) and
selected for this repo's actual tech stack (Bicep IaC, Playwright E2E testing,
technical-spike research discipline). Reviewed and intake-approved by
@urruegg on 2026-08-08.

**Do not confuse these with `agents/<name>/AGENT.md`** at the repo root —
that is this platform's own bespoke, AGENTS.md-governed agent registry
(runtime prompt packs consumed by the GitHub Copilot coding agent and the
Sprint 13 agent-host, per [ADR-0002](../../docs/adr/0002-runtime-is-github-copilot-coding-agent.md)).
The files here are a personal/team VS Code chat-mode convenience layer with
no runtime relationship to that registry.

| File | Source | Use for |
| ---- | ------ | ------- |
| `research-technical-spike.agent.md` | awesome-copilot `agents/research-technical-spike.agent.md` | Timeboxed technical spikes (mirrors the Sprint 42/43 spike pattern already used in this repo's `docs/superpowers/specs/`) — pair with the `create-technical-spike` skill |
| `playwright-tester.agent.md` | awesome-copilot `agents/playwright-tester.agent.md` | Building/maintaining the Sprint 43 WS-4 Playwright E2E suite; complements `ux-design-agent`'s existing Playwright usage |
| `azure-verified-modules-bicep.agent.md` | awesome-copilot `agents/azure-verified-modules-bicep.agent.md` | Reviewing `infra/modules/**` for Azure Verified Modules (AVM) adoption opportunities |

Third-party content — inspected before intake per this repo's own
[skill discovery governance](../../AGENTS.md#skill-discovery--rule-of-engagement-v1140-2026-07-08)
and per [awesome-copilot's own contribution guidance](https://github.com/github/awesome-copilot/blob/main/CONTRIBUTING.md).

## Refresh

```powershell
$base = "https://raw.githubusercontent.com/github/awesome-copilot/main"
Invoke-WebRequest -Uri "$base/agents/research-technical-spike.agent.md" -OutFile ".github/agents/research-technical-spike.agent.md"
Invoke-WebRequest -Uri "$base/agents/playwright-tester.agent.md" -OutFile ".github/agents/playwright-tester.agent.md"
Invoke-WebRequest -Uri "$base/agents/azure-verified-modules-bicep.agent.md" -OutFile ".github/agents/azure-verified-modules-bicep.agent.md"
git diff --stat .github/agents/
```

Diff any changes and PR them like normal repo edits.
