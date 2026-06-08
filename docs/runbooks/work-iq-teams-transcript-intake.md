# Work IQ Teams Transcript Intake Runbook

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-08 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | N/A |

## Purpose

Provide an operator-safe procedure to:
1. Read Teams meetings for `urruegg@microsoft.com`.
2. Select a meeting with a transcript ready.
3. Read and export transcript content.
4. Store raw transcript artefacts under `docs/reviews/raw/`.

After this runbook is completed, proceed with the repository-defined review flow in `agents/review-session-agent/AGENT.md` and `agents/review-session-agent/intake-strategy.md`.

## Scope

In scope:
1. Work IQ MCP transcript intake preparation and execution.
2. Meeting discovery and transcript readiness filtering.
3. Raw transcript export and repository placement.

Out of scope:
1. Curated review report generation.
2. Action-item issue creation.
3. Infrastructure deployment or delete operations.

## Prerequisites

Mandatory prerequisites:
1. Microsoft 365 tenant with Work IQ access.
2. Active Copilot entitlement for the operator account.
3. Tenant admin consent for required Work IQ scopes.
4. Work IQ MCP server registered in runtime host.
5. Teams meeting transcription enabled and transcript stored in Microsoft 365.

Repository prerequisites already in place:
1. MCP allow-list contains `work-iq-mcp` in `.github/copilot/mcp.json`.
2. `review-session-agent` allows read-only Work IQ usage in `AGENTS.md` and `agents/review-session-agent/AGENT.md`.

## Security and Compliance Guardrails

1. Use least-privilege scopes only (meeting metadata read + transcript read).
2. Do not store tokens, secrets, or raw auth payloads in repository files.
3. Keep raw transcripts in `docs/reviews/raw/` only.
4. Do not post transcript content to public issue threads.
5. Treat transcript content as sensitive operational data.

## Runtime Activation Checklist (Local Host)

Perform this once per environment profile:
1. Install or run Work IQ MCP runtime according to your tenant-approved method.
2. Accept EULA if required by CLI/runtime (`workiq accept-eula`).
3. Re-authenticate with the operator account `urs.ruegg@microsoft.com`.
4. Restart MCP host (VS Code or CLI runtime) after registration.
5. Verify tools are visible for `work-iq-mcp` in the host MCP inspector.

## Meeting Discovery and Selection Procedure

### Step 1: List recent meetings

Use Copilot with Work IQ MCP and ask for recent meetings for your account.

Suggested prompt:

```text
Use work-iq-mcp to list my recent Teams meetings for urs.ruegg@microsoft.com from the last 14 days.
For each meeting return: meeting id, subject, organizer, start time, transcript available yes/no.
```

Expected outcome:
1. A list of meeting candidates with transcript availability signal.

### Step 2: Select meeting with transcript ready

Selection criteria:
1. Transcript available is `yes`.
2. Meeting has business relevance for review session processing.
3. Meeting metadata is complete (subject and timestamp present).

Suggested prompt:

```text
From the list, select the most recent meeting with transcript available equals yes.
Return selected meeting id, subject, and meeting start time.
```

Expected outcome:
1. One selected meeting identifier and metadata.

### Step 3: Read transcript content

Suggested prompt:

```text
Use work-iq-mcp to read the transcript for selected meeting id <MEETING_ID>.
Return plain transcript text with speaker segments and timestamps when available.
```

Expected outcome:
1. Transcript text is returned in the chat context.

### Step 4: Export raw transcript into repository

Create one raw file in `docs/reviews/raw/` using this naming convention:

`<yyyy-mm-dd>-<meeting-slug>-workiq-transcript.md`

Example:

`2026-06-08-ama-review-session-csa-cantonal-workiq-transcript.md`

Required raw file header:

```markdown
# Raw Transcript Export

- Source: Work IQ MCP
- Account: urs.ruegg@microsoft.com
- Meeting ID: <MEETING_ID>
- Subject: <MEETING_SUBJECT>
- Start Time (UTC): <ISO-8601>
- Exported At (UTC): <ISO-8601>
- Transcript Ready Signal: yes
```

Then append full transcript content below the header.

Expected outcome:
1. Raw transcript file exists under `docs/reviews/raw/`.
2. Source traceability fields are complete.

## Handoff to Review Workflow

After raw export is complete:
1. Run the defined transcript-to-review process from `agents/review-session-agent/intake-strategy.md`.
2. Generate full conversion and curated review artefacts in `docs/reviews/`.
3. Keep approval gate before any follow-up tracker writes.

## Troubleshooting

If meetings are visible but transcripts are missing:
1. Confirm meeting recording/transcription was enabled.
2. Confirm transcript is stored and accessible in Microsoft 365.
3. Re-authenticate Work IQ MCP session.
4. Validate tenant admin consent and scope grants.

If Work IQ tools are not visible:
1. Restart MCP host.
2. Verify runtime registration for Work IQ MCP.
3. Confirm Copilot is running in MCP-enabled mode.
4. Verify operator account has Copilot entitlement.

If transcript retrieval fails for selected meeting:
1. Re-run meeting list and pick another transcript-ready meeting.
2. Retry with explicit meeting id.
3. Escalate to tenant admin if permission boundary is suspected.

## Evidence Checklist

Before closing this runbook execution:
1. Selected meeting metadata captured.
2. Raw transcript file saved to `docs/reviews/raw/`.
3. Source and timestamp fields populated.
4. No secrets or auth data written to repository.
