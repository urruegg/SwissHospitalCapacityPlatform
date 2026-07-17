#!/usr/bin/env python3
"""Detect double-encoded UTF-8 (mojibake) in tracked text files.

Mojibake happens when UTF-8 bytes are decoded as Latin-1 / cp1252 and then
re-encoded as UTF-8. The resulting file is still *valid* UTF-8, so it passes
markdownlint and every JSON/YAML parser untouched -- but it reads as garbage
(``A-tilde`` + Latin-1 for umlauts, ``a-circumflex`` + euro for dashes/quotes,
``A-circumflex`` + NBSP for non-breaking spaces).

This checker greps the *decoded* text of each file for the canonical mojibake
codepoint signatures. The source of this module is pure ASCII on purpose: every
signature is expressed as a numeric codepoint so the file survives being piped,
re-encoded, or edited on any platform without corrupting the detector itself.

Usage::

    python scripts/lint/check_mojibake.py                 # all tracked text files
    python scripts/lint/check_mojibake.py PATH [PATH...]  # explicit files
    python scripts/lint/check_mojibake.py --staged        # git-staged files only

Suppression: put the token ``mojibake-allow`` anywhere on a line to skip that
single line. Use it only for documentation that must show a mojibake glyph as a
literal example (the ``document-authoring`` skill and knowledge-agent golden
tasks do this). Suppressing a line never suppresses the rest of the file.

Exit codes: 0 = clean, 1 = mojibake found, 2 = usage / environment error.
"""

from __future__ import annotations

import subprocess
import sys

# Lead codepoints that begin a mojibake run when followed by a "continuation"
# codepoint. Expressed numerically so this file stays pure ASCII.
_A_TILDE = 0x00C3   # 'A' with tilde  -> umlaut/accented-letter family (e.g. ae, ue, oe)
_A_CIRC = 0x00C2    # 'A' with circumflex -> punctuation/symbol/NBSP family
_a_circ = 0x00E2    # 'a' with circumflex -> 3-byte-char family (dashes, curly quotes)
_ETH = 0x00F0       # small eth -> emoji / 4-byte family
_EURO = 0x20AC      # euro sign -> the '.a_circ. + euro' quote/dash signature

# Continuation codepoints: the Latin-1 supplement block 0x80-0xBF plus the
# cp1252 "special" mappings that raw bytes 0x80-0x9F decode to. A correctly
# encoded German/French/English document never places one of these immediately
# after a lead codepoint above.
_CONT = set(range(0x0080, 0x00C0)) | {
    0x0152, 0x0153,          # OE / oe ligature
    0x0160, 0x0161,          # S / s caron
    0x0178,                  # Y diaeresis (from sharp-s mojibake)
    0x017D, 0x017E,          # Z / z caron
    0x0192,                  # florin
    0x02C6, 0x02DC,          # modifier circumflex / small tilde
    0x2013, 0x2014,          # en dash / em dash
    0x2018, 0x2019,          # curly single quotes
    0x201A, 0x201C, 0x201D, 0x201E,  # low-9 / curly double quotes
    0x2020, 0x2021,          # dagger / double dagger
    0x2022, 0x2026,          # bullet / ellipsis
    0x2030,                  # per-mille
    0x2039, 0x203A,          # single angle quotes
    0x20AC,                  # euro
    0x2122,                  # trademark
}

_SUPPRESS_TOKEN = "mojibake-allow"

# Text extensions worth scanning. Binary / generated formats are skipped.
_TEXT_EXTS = {
    ".md", ".markdown", ".yaml", ".yml", ".json", ".txt", ".ttl",
    ".bicep", ".py", ".ps1", ".sh", ".toml", ".cfg", ".ini",
}


def is_mojibake_at(text: str, i: int) -> bool:
    """Return True if a mojibake signature begins at index ``i`` in ``text``."""
    lead = ord(text[i])
    if i + 1 >= len(text):
        return False
    nxt = ord(text[i + 1])
    if lead in (_A_TILDE, _A_CIRC, _ETH):
        return nxt in _CONT
    if lead == _a_circ:
        # Keep the 'a-circumflex' family strict: only flag the euro-sign
        # signature (dashes / curly quotes) or a C1-control continuation.
        return nxt == _EURO or 0x0080 <= nxt <= 0x009F
    return False


def scan_text(text: str):
    """Yield (line_number, column, snippet) for each mojibake hit in ``text``."""
    for line_no, line in enumerate(text.splitlines(), start=1):
        if _SUPPRESS_TOKEN in line:
            continue
        i = 0
        while i < len(line):
            if is_mojibake_at(line, i):
                snippet = line[max(0, i - 12):i + 12]
                yield line_no, i + 1, snippet
                i += 2
            else:
                i += 1


def scan_file(path: str):
    """Return a list of findings for ``path`` (empty if clean or unreadable)."""
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError, PermissionError, OSError):
        return []
    return list(scan_text(text))


def _has_text_ext(path: str) -> bool:
    lower = path.lower()
    return any(lower.endswith(ext) for ext in _TEXT_EXTS)


def _git_files(staged: bool):
    if staged:
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
    else:
        cmd = ["git", "ls-files"]
    try:
        out = subprocess.check_output(cmd).decode("utf-8", "replace")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [f for f in out.splitlines() if f and _has_text_ext(f)]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    staged = "--staged" in argv
    explicit = [a for a in argv if not a.startswith("--")]

    if explicit:
        files = explicit
    else:
        files = _git_files(staged=staged)

    total = 0
    dirty_files = 0
    for path in files:
        findings = scan_file(path)
        if findings:
            dirty_files += 1
            total += len(findings)
            for line_no, col, snippet in findings:
                print(f"{path}:{line_no}:{col}: mojibake: ...{snippet}...")

    if total:
        print(
            f"\nFAIL: {total} mojibake occurrence(s) in {dirty_files} file(s). "
            f"Fix by re-writing the affected text as clean UTF-8, or add the "
            f"'{_SUPPRESS_TOKEN}' token to a line that must show a literal example.",
            file=sys.stderr,
        )
        return 1

    scope = "staged" if staged and not explicit else ("listed" if explicit else "tracked")
    print(f"OK: no mojibake in {len(files)} {scope} text file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
