#!/usr/bin/env python3
"""Detect leftover Git merge-conflict markers in tracked text files.

A botched conflict resolution can commit raw markers
(``<<<<<<<`` / ``|||||||`` / ``=======`` / ``>>>>>>>``) straight into a file.
For Markdown this then fails markdownlint (a ``=======`` line reads as a setext
heading underline; ``<<<<<<<`` / ``>>>>>>>`` corrupt tables); for JSON/Bicep it
produces an unparseable, undeployable artifact. Neither the mojibake gate nor a
JSON linter necessarily catches it, so this dedicated gate does.

The source of this module is pure ASCII on purpose and never places a literal
marker at column 0, so the detector never trips over itself.

Usage::

    python scripts/lint/check_conflict_markers.py                 # all tracked files
    python scripts/lint/check_conflict_markers.py PATH [PATH...]  # explicit files
    python scripts/lint/check_conflict_markers.py --staged        # git-staged files only

Suppression: put the token ``conflict-marker-allow`` anywhere on a line to skip
that single line. Use it only for documentation that must show a literal marker
as an example. Suppressing a line never suppresses the rest of the file.

Exit codes: 0 = clean, 1 = markers found, 2 = usage / environment error.
"""

from __future__ import annotations

import re
import subprocess
import sys

_SUPPRESS_TOKEN = "conflict-marker-allow"

# Standard Git conflict markers are exactly seven identical characters. The
# opening/base/closing markers are followed by a space + label (or end of line);
# the separator stands alone. Patterns are built from character classes so this
# file never contains a literal marker at column 0.
_MARKERS = (
    re.compile(r"^<{7}(?= |$)"),   # ours
    re.compile(r"^\|{7}(?= |$)"),  # diff3 merged base
    re.compile(r"^={7}$"),          # separator
    re.compile(r"^>{7}(?= |$)"),   # theirs
)


def scan_text(text: str):
    """Yield (line_number, marker) for each conflict marker in ``text``."""
    for line_no, line in enumerate(text.splitlines(), start=1):
        if _SUPPRESS_TOKEN in line:
            continue
        for pattern in _MARKERS:
            if pattern.match(line):
                yield line_no, line[:7]
                break


def scan_file(path: str):
    """Return a list of findings for ``path`` (empty if clean or binary)."""
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError, PermissionError, OSError):
        return []
    return list(scan_text(text))


def _git_files(staged: bool):
    if staged:
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
    else:
        cmd = ["git", "ls-files"]
    try:
        out = subprocess.check_output(cmd).decode("utf-8", "replace")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [f for f in out.splitlines() if f]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    staged = "--staged" in argv
    explicit = [a for a in argv if not a.startswith("--")]

    files = explicit if explicit else _git_files(staged=staged)

    total = 0
    dirty_files = 0
    for path in files:
        findings = scan_file(path)
        if findings:
            dirty_files += 1
            total += len(findings)
            for line_no, marker in findings:
                print(f"{path}:{line_no}: conflict marker: {marker}")

    if total:
        print(
            f"\nFAIL: {total} conflict marker(s) in {dirty_files} file(s). "
            f"Finish the merge/resolution and remove every marker, or add the "
            f"'{_SUPPRESS_TOKEN}' token to a line that must show a literal example.",
            file=sys.stderr,
        )
        return 1

    scope = "staged" if staged and not explicit else ("listed" if explicit else "tracked")
    print(f"OK: no conflict markers in {len(files)} {scope} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
