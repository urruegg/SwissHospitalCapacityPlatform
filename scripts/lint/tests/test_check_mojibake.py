"""Unit tests for scripts/lint/check_mojibake.py.

Mojibake strings are constructed with ``chr()`` / codepoints so this test
source stays pure ASCII and never trips the very checker it exercises.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from check_mojibake import scan_text, is_mojibake_at  # noqa: E402


def moji(*codepoints):
    return "".join(chr(cp) for cp in codepoints)


# Canonical mojibake signatures (what a corrupted file actually contains).
AE = moji(0x00C3, 0x00A4)          # 'ae' umlaut  -> A-tilde + currency
UE = moji(0x00C3, 0x00BC)          # 'ue' umlaut  -> A-tilde + 1/4
OE = moji(0x00C3, 0x00B6)          # 'oe' umlaut  -> A-tilde + pilcrow
SHARP_S = moji(0x00C3, 0x0178)     # sharp-s      -> A-tilde + Y-diaeresis (cp1252 0x9F)
EM_DASH = moji(0x00E2, 0x20AC, 0x201D)   # em dash -> a-circ + euro + curly-quote
NBSP = moji(0x00C2, 0x00A0)        # NBSP         -> A-circ + NBSP
DEGREE = moji(0x00C2, 0x00B0)      # degree sign  -> A-circ + degree


class TestDetection(unittest.TestCase):
    def test_detects_umlaut_families(self):
        for bad in (AE, UE, OE, SHARP_S):
            with self.subTest(bad=bad):
                self.assertTrue(list(scan_text(f"Herr {bad}rzt")), f"missed {bad!r}")

    def test_detects_dash_and_space_families(self):
        for bad in (EM_DASH, NBSP, DEGREE):
            with self.subTest(bad=bad):
                self.assertTrue(list(scan_text(f"value {bad} here")), f"missed {bad!r}")

    def test_reports_line_and_column(self):
        text = "clean line\nHerr " + UE + "berlingen"
        hits = list(scan_text(text))
        self.assertEqual(len(hits), 1)
        line_no, col, _snippet = hits[0]
        self.assertEqual(line_no, 2)
        self.assertEqual(col, 6)  # 1-based column of the lead char after 'Herr '


class TestNoFalsePositives(unittest.TestCase):
    def test_correct_utf8_is_clean(self):
        good = [
            "R" + chr(0x00FC) + "egg",           # Rueegg with correct u-umlaut
            "Z" + chr(0x00FC) + "rich",           # correct u-umlaut
            "stra" + chr(0x00DF) + "e",           # correct sharp-s
            "caf" + chr(0x00E9),                   # correct e-acute
            "5 " + chr(0x2192) + " 10",           # correct right-arrow
            "a " + chr(0x2014) + " b",            # correct em dash, standalone
            chr(0x00AB) + "quote" + chr(0x00BB),  # correct guillemets
            "normal ascii text only",
        ]
        for g in good:
            with self.subTest(good=g):
                self.assertEqual(list(scan_text(g)), [], f"false positive on {g!r}")


class TestSuppression(unittest.TestCase):
    def test_mojibake_allow_skips_line(self):
        text = "Example of " + AE + " glyph  mojibake-allow"
        self.assertEqual(list(scan_text(text)), [])

    def test_suppression_is_line_scoped(self):
        text = ("Example " + AE + " mojibake-allow\n" + "Real " + UE + " corruption")
        hits = list(scan_text(text))
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0][0], 2)


class TestPrimitive(unittest.TestCase):
    def test_is_mojibake_at_boundary(self):
        self.assertFalse(is_mojibake_at(chr(0x00C3), 0))  # lead at end of string
        self.assertTrue(is_mojibake_at(AE, 0))


if __name__ == "__main__":
    unittest.main()
