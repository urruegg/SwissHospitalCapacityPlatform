# Review Session Agent Intake Strategy

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-22 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (transcript intake only) |

## Purpose

Define a deterministic, agent-friendly intake path for review sessions **and email-feedback threads**. The agent must resolve the intake **kind** (`session` or `email`) before selecting a tooling path.

## Tooling Model

1. Work IQ MCP retrieves meeting context, transcript content, and email (message / thread / attachment) content from Microsoft 365. Strictly read-only.
2. Markitdown converts Word transcript files (`.docx`) and supported email attachments into markdown.
3. The `review-session-agent` evaluates and normalizes output into a dedicated report under `docs/reviews/` (naming pattern `<yyyy-mm-dd>-<kind>-<slug>.md`).

## Conversion Options

1. Local deterministic conversion:

```powershell
py -m markitdown "docs/reviews/raw/<source>.docx" -o "docs/reviews/<date>-<slug>-full.md"
```

2. Document Intelligence-assisted extraction when OCR/layout fidelity is needed:

```powershell
py -m markitdown "docs/reviews/raw/<source>.docx" -d -e "<docintel-endpoint>" -o "docs/reviews/<date>-<slug>-full.md"
```

3. Content Understanding-assisted extraction for richer parsing scenarios:

```powershell
py -m markitdown "docs/reviews/raw/<source>.docx" --use-content-understanding --cu-endpoint "<cu-endpoint>" -o "docs/reviews/<date>-<slug>-full.md"
```

## Canonical Workflow

### For `kind = session`

1. For a `.docx` / file transcript, store the source under `docs/reviews/raw/`. For a Microsoft 365 / Teams **meeting recording**, resolve the meeting via Work IQ MCP and retrieve its transcript + meeting context (subject, organiser, participants, start/end time, meeting id); never fetch or store the raw audio/video binary.
2. Generate `*-full.md` from the source transcript (Work IQ MCP export or Markitdown conversion of `.docx`).
3. Produce curated review report `<yyyy-mm-dd>-session-<slug>.md`.
4. Keep the source reference (path or Work IQ meeting id) and evaluated artefact list in each report.

### For `kind = email`

1. Resolve the message via Work IQ MCP: capture `messageId`, `conversationId`, sender, recipients, subject, sentDateTime.
2. If the input references a thread, retrieve all messages in chronological order via Work IQ MCP.
3. For each attachment: if it is a supported document format, convert with Markitdown into `docs/reviews/raw/<yyyy-mm-dd>-<slug>-attach-<n>.md`; otherwise record the attachment name + size + content-type in the report and skip binary storage.
4. Do **not** commit raw message body content that contains PHI or personal data to `docs/reviews/raw/`. Persist only the sanitized, evaluated report under `docs/reviews/`.
5. Produce curated review report `<yyyy-mm-dd>-email-<slug>.md`. Include `messageId` and `conversationId` in the report front-matter for traceability.

## Guardrails

1. Human review is mandatory before any write actions to external trackers.
2. Separate extraction draft from action-item publication.
3. Keep prompts and instructions versioned in repository.
4. Preserve transcript- or mail-source traceability in every review artefact.
5. Work IQ MCP is used **read-only** for both intake kinds; no reply, forward, or mailbox mutation is permitted from this agent.
6. PHI / personal data must not be persisted in git — sanitize before writing any artefact to `docs/reviews/`.
