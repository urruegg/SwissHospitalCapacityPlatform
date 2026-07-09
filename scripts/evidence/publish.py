"""Evidence publish orchestrator.

Runs every parser against the canonical repo sources and writes byte-stable
JSON to ``data/evidence/*.json``. Invoked locally, by the ``evidence-publish``
GitHub Actions workflow, and by the parser test-suite.

    python -m scripts.evidence.publish --repo-root . --out data/evidence
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from scripts.evidence.parsers.adr_parser import parse_adrs
from scripts.evidence.parsers.bom_parser import parse_bom
from scripts.evidence.parsers.common import resolve_commit, write_json
from scripts.evidence.parsers.infra_parser import parse_infra
from scripts.evidence.parsers.prd_parser import parse_prd
from scripts.evidence.parsers.region_availability_parser import parse_region_availability

OUTPUT_FILES = (
    "requirements.json",
    "adrs.json",
    "req_adr_map.json",
    "bom.json",
    "dependencies.json",
    "region_availability.json",
    "deployed_bom.json",
)


def build_outputs(repo_root: Path, source_commit: str | None = None) -> dict[str, list[dict]]:
    """Run all parsers and return the output-file -> rows mapping (no I/O)."""
    commit = source_commit or resolve_commit(repo_root)
    docs = repo_root / "docs"

    outputs: dict[str, list[dict]] = {}
    outputs["requirements.json"] = parse_prd(docs / "PRD.md", source_commit=commit)

    adr_rows, map_rows = parse_adrs(docs / "adr", source_commit=commit)
    outputs["adrs.json"] = adr_rows
    outputs["req_adr_map.json"] = _merge_req_adr_map(
        map_rows, docs / "adr-requirement-map.yaml", commit
    )

    bom_path = docs / "bom.yaml"
    if bom_path.exists():
        bom_rows, dep_rows = parse_bom(bom_path, source_commit=commit)
    else:
        bom_rows, dep_rows = [], []
    outputs["bom.json"] = bom_rows
    outputs["dependencies.json"] = dep_rows

    region_path = docs / "region-availability.yaml"
    outputs["region_availability.json"] = (
        parse_region_availability(region_path, source_commit=commit)
        if region_path.exists()
        else []
    )

    outputs["deployed_bom.json"] = parse_infra(
        repo_root / "infra", repo_root=repo_root, source_commit=commit
    )
    return outputs


def _merge_req_adr_map(front_matter_rows: list[dict], map_path: Path, commit: str) -> list[dict]:
    """Merge ADR-front-matter edges with the curated ``adr-requirement-map.yaml``.

    Deduped on ``(requirementId, adrId, relationship)`` and sorted for
    byte-stable output.
    """
    rows = list(front_matter_rows)
    if map_path.exists():
        data = yaml.safe_load(map_path.read_text(encoding="utf-8")) or {}
        for edge in data.get("edges", []):
            row = {
                "requirementId": edge["requirementId"],
                "adrId": edge["adrId"],
                "relationship": edge.get("relationship", "governs"),
                "sourcePath": "docs/adr-requirement-map.yaml",
                "sourceCommit": commit,
            }
            if edge.get("note"):
                row["note"] = edge["note"]
            rows.append(row)

    seen: set[tuple[str, str, str]] = set()
    unique: list[dict] = []
    for row in rows:
        key = (row["requirementId"], row["adrId"], row.get("relationship", "governs"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return sorted(unique, key=lambda r: (r["requirementId"], r["adrId"], r.get("relationship", "")))


def publish(repo_root: Path, out_dir: Path, source_commit: str | None = None) -> list[Path]:
    """Write all evidence outputs to ``out_dir`` and return the written paths."""
    outputs = build_outputs(repo_root, source_commit=source_commit)
    written: list[Path] = []
    for filename in OUTPUT_FILES:
        target = out_dir / filename
        write_json(target, outputs[filename])
        written.append(target)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish evidence JSON from repo sources.")
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--out", default=Path("data/evidence"), type=Path)
    parser.add_argument("--source-commit", default=None)
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    written = publish(repo_root, args.out.resolve(), source_commit=args.source_commit)
    for path in written:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
