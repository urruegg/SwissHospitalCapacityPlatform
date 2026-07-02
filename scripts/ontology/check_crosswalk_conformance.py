"""Ontology two-layer crosswalk conformance check.

Realises `FR-GOV-ONT-003` (Sprint 09 scaffold; enforcement flips in Sprint 10
per AMA HCC/North Star review §11.1 H-05).

Verifies consistency between:
- Reference layer:  `docs/ontology/reference-layer.ttl`  (Turtle/OWL classes)
- Crosswalk:        `docs/ontology/crosswalk.md`         (MVO scope table)

Sprint 09 semantics (WARN-only):
- Missing crosswalk rows are reported but do NOT fail the build.
- Exit code is always 0 unless the script itself errors (I/O, malformed TTL).
- Sprint 10 flips the tail return to a non-zero exit when WARN count > 0.

Usage:
    python scripts/ontology/check_crosswalk_conformance.py
    python scripts/ontology/check_crosswalk_conformance.py --strict   # Sprint 10 preview

Exit codes:
    0 — check ran successfully (WARN-only mode; or STRICT mode with no findings)
    1 — check found conformance issues in STRICT mode
    2 — script error (file missing, unreadable, etc.)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TTL_PATH = REPO_ROOT / "docs" / "ontology" / "reference-layer.ttl"
CROSSWALK_PATH = REPO_ROOT / "docs" / "ontology" / "crosswalk.md"

TTL_CLASS_RX = re.compile(
    r"^(hcp:[A-Za-z_][A-Za-z0-9_]*)\s+a\s+owl:Class\s*[;.]",
    re.MULTILINE,
)
# Also match subclass declarations like "hcp:Bed a owl:Class ;\n    rdfs:subClassOf hcp:CapacityUnit ;"
TTL_SUBCLASS_RX = re.compile(
    r"^(hcp:[A-Za-z_][A-Za-z0-9_]*)\s+a\s+owl:Class\s*[;\n]",
    re.MULTILINE,
)

# Match crosswalk MVO rows: | `hcp:Foo` | ... |
CROSSWALK_ROW_RX = re.compile(
    r"^\|\s*`(hcp:[A-Za-z_][A-Za-z0-9_]*)`\s*\|",
    re.MULTILINE,
)


@dataclass
class Finding:
    severity: str  # "WARN" | "FAIL"
    message: str


def parse_reference_classes(ttl_text: str) -> set[str]:
    """Extract every `hcp:*` class declared in the reference layer."""
    matches = set(TTL_SUBCLASS_RX.findall(ttl_text))
    return matches


def parse_crosswalk_classes(md_text: str) -> set[str]:
    """Extract every `hcp:*` class referenced from the MVO crosswalk rows."""
    return set(CROSSWALK_ROW_RX.findall(md_text))


def check_conformance(reference: set[str], crosswalk: set[str]) -> list[Finding]:
    findings: list[Finding] = []

    # Every reference class should have a crosswalk row (except the abstract root).
    ABSTRACT_ROOT = {"hcp:CapacityUnit", "hcp:CapacityState"}
    ref_gap = reference - crosswalk - ABSTRACT_ROOT
    for cls in sorted(ref_gap):
        findings.append(
            Finding(
                "WARN",
                f"reference class {cls!r} has no row in crosswalk.md MVO table "
                f"(add a row, or annotate the class as reference-layer-only "
                f"in a comment).",
            )
        )

    # Every crosswalk row should reference a class declared in the TTL.
    crosswalk_gap = crosswalk - reference
    for cls in sorted(crosswalk_gap):
        findings.append(
            Finding(
                "FAIL",
                f"crosswalk row references undeclared reference class {cls!r} "
                f"(add the class to reference-layer.ttl or fix the row).",
            )
        )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Sprint 10 mode: exit non-zero on any WARN or FAIL finding.",
    )
    args = parser.parse_args()

    print(f"[ontology-check] reading {TTL_PATH.relative_to(REPO_ROOT)}")
    try:
        ttl_text = TTL_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[ontology-check] ERROR: cannot read TTL: {exc}", file=sys.stderr)
        return 2

    print(f"[ontology-check] reading {CROSSWALK_PATH.relative_to(REPO_ROOT)}")
    try:
        crosswalk_text = CROSSWALK_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[ontology-check] ERROR: cannot read crosswalk: {exc}", file=sys.stderr)
        return 2

    reference = parse_reference_classes(ttl_text)
    crosswalk = parse_crosswalk_classes(crosswalk_text)

    print(f"[ontology-check] reference classes:  {len(reference):3d}  {sorted(reference)}")
    print(f"[ontology-check] crosswalk classes:  {len(crosswalk):3d}  {sorted(crosswalk)}")

    findings = check_conformance(reference, crosswalk)

    warn_count = sum(1 for f in findings if f.severity == "WARN")
    fail_count = sum(1 for f in findings if f.severity == "FAIL")

    print("")
    print(f"[ontology-check] findings: {warn_count} WARN, {fail_count} FAIL")
    for finding in findings:
        prefix = f"[ontology-check] {finding.severity}"
        print(f"{prefix}: {finding.message}")

    if not findings:
        print("[ontology-check] PASS — two-layer crosswalk is coherent.")
        return 0

    if args.strict:
        print("[ontology-check] STRICT mode: non-zero exit due to findings.")
        return 1

    print(
        "[ontology-check] Sprint 09 WARN-only mode: exiting 0. "
        "Strict enforcement flips in Sprint 10 per AMA §11.1 H-05."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
