# Review Session Agent Intake Strategy

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-08 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | N/A |

## Purpose

Define a deterministic, agent-friendly transcript intake path for review sessions.

## Tooling Model

1. Work IQ MCP retrieves meeting context and transcript content from Microsoft 365.
2. Markitdown converts Word transcript files (`.docx`) into markdown.
3. The `review-session-agent` evaluates and normalizes output into a dedicated report under `docs/reviews/`.

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

1. Store source transcripts under `docs/reviews/raw/`.
2. Generate `*-full.md` from source transcript.
3. Produce curated review report `<yyyy-mm-dd>-<session-slug>.md`.
4. Keep source path and evaluated artefact list in each report.

## Guardrails

1. Human review is mandatory before any write actions to external trackers.
2. Separate extraction draft from action-item publication.
3. Keep prompts and instructions versioned in repository.
4. Preserve transcript-source traceability in every review artefact.
