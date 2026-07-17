#!/usr/bin/env python3
"""Repair double-encoded UTF-8 (mojibake) in text files.

Companion to ``check_mojibake.py``. For every mojibake run the detector finds,
this applies the deterministic inverse transform -- re-encode the corrupted run
as cp1252 and decode it as UTF-8 -- which recovers the original character
(``A-circ + section`` -> section sign, ``a-circ + euro + quote`` -> em dash,
``A-tilde + 1/4`` -> u-umlaut, and so on).

The transform only runs on detected signatures, skips lines carrying the
``mojibake-allow`` token, preserves the original line endings, and writes
BOM-less UTF-8. Runs that do not round-trip cleanly are left untouched and
reported so a human can fix them by hand.

Usage::

    python scripts/lint/fix_mojibake.py                 # all tracked text files
    python scripts/lint/fix_mojibake.py PATH [PATH...]  # explicit files
    python scripts/lint/fix_mojibake.py --check         # report only, do not write

Exit codes: 0 = nothing left to fix, 1 = residual (non-round-trippable) runs,
2 = usage error.
"""

from __future__ import annotations

import subprocess
import sys
from os.path import dirname, abspath

sys.path.insert(0, dirname(abspath(__file__)))
from check_mojibake import is_mojibake_at, _CONT, _EURO, _SUPPRESS_TOKEN, _has_text_ext  # noqa: E402


def _extend_run(line: str, start: int) -> int:
    """Return the end index (exclusive) of the mojibake run beginning at start."""
    j = start + 1
    while j < len(line) and (ord(line[j]) in _CONT or ord(line[j]) == _EURO):
        j += 1
    return j


def _repair_run(run: str):
    """Return the clean character(s) for a mojibake run, or None if it does not
    round-trip through the cp1252 -> utf-8 inverse."""
    try:
        return run.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None


def fix_line(line: str):
    """Return (fixed_line, num_fixed, num_residual) for a single line."""
    if _SUPPRESS_TOKEN in line:
        return line, 0, 0
    out = []
    i = 0
    fixed = residual = 0
    while i < len(line):
        if is_mojibake_at(line, i):
            end = _extend_run(line, i)
            run = line[i:end]
            repaired = _repair_run(run)
            if repaired is not None:
                out.append(repaired)
                fixed += 1
            else:
                out.append(run)
                residual += 1
            i = end
        else:
            out.append(line[i])
            i += 1
    return "".join(out), fixed, residual


def fix_text(text: str):
    """Fix a whole document, preserving CRLF/LF line endings."""
    lines = text.split("\n")  # keeps any trailing '\r' on each line
    total_fixed = total_residual = 0
    for idx, line in enumerate(lines):
        new_line, fixed, residual = fix_line(line)
        lines[idx] = new_line
        total_fixed += fixed
        total_residual += residual
    return "\n".join(lines), total_fixed, total_residual


def _git_text_files():
    try:
        out = subprocess.check_output(["git", "ls-files"]).decode("utf-8", "replace")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [f for f in out.splitlines() if f and _has_text_ext(f)]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    check_only = "--check" in argv
    explicit = [a for a in argv if not a.startswith("--")]
    files = explicit if explicit else _git_text_files()

    grand_fixed = grand_residual = touched = 0
    for path in files:
        try:
            with open(path, encoding="utf-8", newline="") as handle:
                text = handle.read()
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError, PermissionError, OSError):
            continue
        new_text, fixed, residual = fix_text(text)
        grand_residual += residual
        if fixed and new_text != text:
            grand_fixed += fixed
            touched += 1
            if not check_only:
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    handle.write(new_text)
            verb = "would fix" if check_only else "fixed"
            print(f"{verb} {fixed} run(s) in {path}")
        if residual:
            print(f"WARNING: {residual} non-round-trippable run(s) remain in {path}", file=sys.stderr)

    action = "repairable" if check_only else "repaired"
    print(f"\n{grand_fixed} mojibake run(s) {action} across {touched} file(s).")
    return 1 if grand_residual else 0


if __name__ == "__main__":
    raise SystemExit(main())
