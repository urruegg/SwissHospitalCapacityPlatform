"""Unit tests for scripts/lint/check_conflict_markers.py.

Marker strings are constructed from character multiplication (e.g. ``"<" * 7``)
so this test source never contains a literal marker at column 0 and therefore
never trips the very checker it exercises.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from check_conflict_markers import scan_text  # noqa: E402

OURS = "<" * 7
BASE = "|" * 7
SEP = "=" * 7
THEIRS = ">" * 7


class TestDetection(unittest.TestCase):
    def test_detects_each_marker(self):
        cases = [
            OURS + " HEAD",
            BASE + " merged common ancestor",
            SEP,
            THEIRS + " origin/main",
        ]
        for line in cases:
            with self.subTest(line=line):
                self.assertTrue(list(scan_text(line)), f"missed {line!r}")

    def test_reports_line_number(self):
        text = "clean\nmore clean\n" + SEP + "\ntail"
        hits = list(scan_text(text))
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0][0], 3)

    def test_full_conflict_block(self):
        text = "\n".join([OURS + " HEAD", "mine", SEP, "theirs", THEIRS + " branch"])
        self.assertEqual(len(list(scan_text(text))), 3)


class TestNoFalsePositives(unittest.TestCase):
    def test_ordinary_text_is_clean(self):
        good = [
            "normal ascii text",
            "a << b and c >> d in code",          # shift operators, not markers
            "===== short rule =====",              # not exactly 7 leading '='
            "======== eight equals ========",      # 8, not 7
            "<<<<<< six opening",                   # 6, not 7
            "    " + OURS + " indented (not col 0)",  # markers never indent
            "table | cell ======= inline",         # '=' run not at line start
        ]
        for g in good:
            with self.subTest(good=g):
                self.assertEqual(list(scan_text(g)), [], f"false positive on {g!r}")


class TestSuppression(unittest.TestCase):
    def test_allow_token_skips_line(self):
        text = SEP + "   conflict-marker-allow"
        self.assertEqual(list(scan_text(text)), [])

    def test_suppression_is_line_scoped(self):
        text = SEP + " conflict-marker-allow\n" + THEIRS + " origin/main"
        hits = list(scan_text(text))
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0][0], 2)


if __name__ == "__main__":
    unittest.main()
