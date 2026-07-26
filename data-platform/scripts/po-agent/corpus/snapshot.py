"""WS-A Class A corpus: snapshot the product docs tree (Sprint 28, issue #377).

Reads the Curavias product corpus (PRDs, ADRs, design specs, runbooks and the
first-order interview transcripts under ``docs/reviews/``) from the repository
working tree and materialises it as a flat set of source documents the
``chunk_tag`` -> ``phi_gate`` -> ``publish`` pipeline consumes.

In production the CLI writes the snapshot into the ADLS Gen2 corpus landing zone
(``landing/curavias-product-corpus/<source>/<yyyy-mm-dd>/``, see
``infra/modules/knowledge-layer/corpus-landing``); here it is filesystem-based so
it is fully testable with no cloud dependency and no PHI.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date
from pathlib import Path

# Corpus source roots (relative to the repo root), each mapped to a source tag.
CORPUS_SOURCES: dict[str, str] = {
    "docs/reviews": "interview",
    "docs/adr": "adr",
    "docs": "prd",
    "docs/superpowers/specs": "design",
    "docs/runbooks": "runbook",
}


def get_commit(repo_root: Path) -> str:
    """Return the short HEAD commit sha, or ``unknown`` outside a git tree."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10, check=True,
        )
        return out.stdout.strip() or "unknown"
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def snapshot_tree(root: Path, commit: str, sources: dict[str, str] | None = None) -> list[dict]:
    """Walk the corpus source roots under ``root`` and return SourceDocs.

    Each SourceDoc is ``{"path": <repo-relative posix path>, "text": str,
    "commit": str, "source": <tag>}``. A document is attributed to the *most
    specific* matching source root so ``docs/adr/x.md`` is ``adr`` not ``prd``.
    """
    sources = sources or CORPUS_SOURCES
    # Longest path first so nested roots win over their parents.
    ordered = sorted(sources.items(), key=lambda kv: len(kv[0]), reverse=True)
    docs: dict[str, dict] = {}
    for rel_root, tag in ordered:
        base = (root / rel_root)
        if not base.is_dir():
            continue
        for md in base.rglob("*.md"):
            rel = md.relative_to(root).as_posix()
            if rel in docs:
                continue  # already claimed by a more specific source root
            docs[rel] = {
                "path": rel,
                "text": md.read_text(encoding="utf-8"),
                "commit": commit,
                "source": tag,
            }
    return list(docs.values())


def _iso_today() -> str:
    return date.today().isoformat()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Snapshot the PO Agent Class A corpus.")
    parser.add_argument("--repo-root", default=".", help="Repository root to snapshot.")
    parser.add_argument("--out", required=True, help="Output directory for the snapshot JSONL.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    commit = get_commit(repo_root)
    docs = snapshot_tree(repo_root, commit)

    out_dir = Path(args.out) / _iso_today()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "corpus-snapshot.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for doc in docs:
            fh.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"snapshot: {len(docs)} documents @ {commit} -> {out_file}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
