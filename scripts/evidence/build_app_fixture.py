"""Build the presenter-whiteboard evidence fixture for hcc-app-fluent.

Sprint 14.1 · T5. Reuses the evidence parsers (``scripts.evidence.publish``) and
the pure readiness scorer (``readiness_rules.score_readiness``) to emit a
compact, **byte-stable** JSON dataset the Fluent app imports for the Backstage
Evidence tab:

    apps/hcc-app-fluent/src/data/evidence/evidence-demo.json

The app reads this committed fixture in dev/CI where no Fabric SQL endpoint is
wired (design spec §5; ADR-0026). It carries per-card provenance
(``sourceUrl`` + ``asOf``) so the whiteboard's provenance contract can render
every card with lineage.

Regenerate after editing ``docs/bom.yaml`` / ``docs/region-availability.yaml`` /
``docs/adr/**`` / ``docs/PRD.md``::

    python -m scripts.evidence.build_app_fixture

The volatile source commit is intentionally excluded so the output stays stable;
provenance URLs point at the ``main`` ref.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.evidence.publish import build_outputs

# The readiness scorer lives with the Fabric notebooks; import it off-cluster.
_NOTEBOOKS = Path(__file__).resolve().parents[2] / "data-platform" / "notebooks" / "evidence"
sys.path.insert(0, str(_NOTEBOOKS))
from readiness_rules import aggregate_readiness, score_readiness  # noqa: E402

REPO_BLOB = "https://github.com/urruegg/SwissHospitalCapacityPlatform/blob/main"

# Fixed snapshot date → byte-stable output. Represents the evidence "as of" date;
# bump when the seed catalogs are re-curated.
AS_OF = "2026-07-10"

DEFAULT_OUT = (
    Path(__file__).resolve().parents[2]
    / "apps"
    / "hcc-app-fluent"
    / "src"
    / "data"
    / "evidence"
    / "evidence-demo.json"
)


def _blob(source_path: str) -> str:
    return f"{REPO_BLOB}/{source_path}"


def _provenance(source_path: str, as_of: str = AS_OF) -> dict:
    return {"sourceUrl": _blob(source_path), "sourcePath": source_path, "asOf": as_of}


def build_dataset(repo_root: Path) -> dict:
    outputs = build_outputs(repo_root, source_commit="main")

    boms = outputs["bom.json"]
    adrs = outputs["adrs.json"]
    requirements = outputs["requirements.json"]
    dependencies = outputs["dependencies.json"]
    availability = outputs["region_availability.json"]

    # Readiness per BOM × track (pure scorer, same rules as the Fabric notebook).
    deps_by_from: dict = {}
    for edge in dependencies:
        deps_by_from.setdefault(edge["fromId"], []).append(
            {"to": edge["toId"], "type": edge["type"]}
        )
    scorer_items = [{"id": b["id"], "dependsOn": deps_by_from.get(b["id"], [])} for b in boms]
    readiness_rows = score_readiness(scorer_items, availability)
    summary = aggregate_readiness(readiness_rows)

    readiness_by_bom: dict = {}
    for row in readiness_rows:
        track_key = "tShow" if row["track"] == "T-SHOW" else "tProd"
        readiness_by_bom.setdefault(row["bomId"], {})[track_key] = {
            "status": row["status"],
            "region": row["region"],
            "showcaseOnly": row["showcaseOnly"],
            "blockingReason": row["blockingReason"],
        }

    # Best showcase-region availability chip per BOM (CH North, else West Europe).
    dep_count: dict = {b["id"]: len(deps_by_from.get(b["id"], [])) for b in boms}
    chip_by_bom: dict = {}
    for region in ("Switzerland North", "West Europe"):
        for fact in availability:
            if fact["region"] == region and fact["bomId"] not in chip_by_bom:
                chip_by_bom[fact["bomId"]] = {"region": region, "maturity": fact["maturity"]}

    bom_cards = [
        {
            "id": b["id"],
            "name": b["name"],
            "type": b["type"],
            "category": b["category"],
            "sku": b.get("sku"),
            "regionChip": chip_by_bom.get(b["id"]),
            "dependencyCount": dep_count.get(b["id"], 0),
            "realisesRequirements": b.get("realisesRequirements", []),
            "governedByAdrs": b.get("governedByAdrs", []),
            "readiness": readiness_by_bom.get(b["id"], {}),
            "provenance": _provenance(b["sourcePath"]),
        }
        for b in boms
    ]

    adr_cards = [
        {
            "id": a["id"],
            "title": a["title"],
            "status": a["status"],
            "decisionSummary": a.get("decisionSummary", ""),
            "provenance": _provenance(a["sourcePath"]),
        }
        for a in adrs
    ]

    requirement_cards = [
        {
            "id": r["id"],
            "kind": r["kind"],
            "family": r["family"],
            "title": r["title"],
            "mvp": r["mvp"],
            "provenance": _provenance(r["sourcePath"]),
        }
        for r in requirements
    ]

    ga_cards = [
        {
            "bomId": f["bomId"],
            "region": f["region"],
            "maturity": f["maturity"],
            "verifiedBy": f["verifiedBy"],
            "provenance": {
                "sourceUrl": f.get("sourceUrl") or _blob(f["sourcePath"]),
                "sourcePath": f["sourcePath"],
                "asOf": f["asOf"],
            },
        }
        for f in availability
    ]

    edge_cards = [
        {
            "fromId": e["fromId"],
            "toId": e["toId"],
            "type": e["type"],
            "provenance": _provenance(e["sourcePath"]),
        }
        for e in dependencies
    ]

    return {
        "generatedAt": AS_OF,
        "summary": summary,
        "boms": bom_cards,
        "adrs": adr_cards,
        "requirements": requirement_cards,
        "gaEvidence": ga_cards,
        "dependencies": edge_cards,
    }


def write_dataset(dataset: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the app evidence fixture.")
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    args = parser.parse_args(argv)

    dataset = build_dataset(args.repo_root.resolve())
    write_dataset(dataset, args.out.resolve())
    print(f"wrote {args.out} ({len(dataset['boms'])} BOM, {len(dataset['adrs'])} ADR)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
