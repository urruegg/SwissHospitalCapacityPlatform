#!/usr/bin/env python3
"""Sync the repository's issue/PR labels from ``.github/labels.yml``.

Single source of truth for the prefixed label taxonomy (``type:`` / ``lane:`` /
``status:`` / ``deploy:``) that keeps the WORK -> REVIEW -> APPROVE context of
every issue and pull request legible at a glance (see ``docs/DEV_WORKFLOW.md``).

The sync is **additive and idempotent** by default: it creates missing labels
and updates the colour/description of existing ones via ``gh label create
--force``. It never deletes ``sprint-NN`` or other legacy labels unless invoked
with ``--prune`` (which removes only labels absent from the file).

Usage::

    python scripts/labels/sync_labels.py            # dry-run (print plan)
    python scripts/labels/sync_labels.py --apply     # create/update labels
    python scripts/labels/sync_labels.py --apply --prune   # also delete extras

Requires the GitHub CLI (``gh``) authenticated for the current repository.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

LABELS_FILE = Path(__file__).resolve().parents[2] / ".github" / "labels.yml"


def _run(args: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(
        args, check=True, text=True, capture_output=capture
    )
    return result.stdout if capture else ""


def load_desired() -> list[dict]:
    data = yaml.safe_load(LABELS_FILE.read_text(encoding="utf-8"))
    labels = data.get("labels", [])
    for label in labels:
        if not label.get("name") or not label.get("color"):
            raise SystemExit(f"Invalid label entry (needs name + color): {label!r}")
    return labels


def existing_names() -> set[str]:
    out = _run(["gh", "label", "list", "--limit", "200", "--json", "name"], capture=True)
    return {item["name"] for item in json.loads(out)}


def sync(apply: bool, prune: bool) -> int:
    desired = load_desired()
    have = existing_names()
    desired_names = {label["name"] for label in desired}

    for label in desired:
        name = label["name"]
        verb = "update" if name in have else "create"
        print(f"[{verb}] {name}  #{label['color']}  {label.get('description', '')}")
        if apply:
            _run([
                "gh", "label", "create", name,
                "--color", label["color"],
                "--description", label.get("description", ""),
                "--force",
            ])

    if prune:
        for name in sorted(have - desired_names):
            print(f"[delete] {name}")
            if apply:
                _run(["gh", "label", "delete", name, "--yes"])

    if not apply:
        print("\nDry-run only. Re-run with --apply to make changes.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Create/update labels (default: dry-run)")
    parser.add_argument("--prune", action="store_true", help="Delete labels not present in labels.yml")
    args = parser.parse_args()
    return sync(apply=args.apply, prune=args.prune)


if __name__ == "__main__":
    sys.exit(main())
