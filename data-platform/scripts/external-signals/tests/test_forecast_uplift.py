import unittest

import forecast_uplift as fu


class TestUpliftMap(unittest.TestCase):
    def setUp(self):
        self.m = fu.load_uplift_map()

    def test_heat_severe_geriatrics(self):
        self.assertAlmostEqual(fu.uplift_factor("heat", "Severe", "geriatrics", self.m), 0.25)

    def test_heat_severe_real_specialty_id(self):
        self.assertAlmostEqual(fu.uplift_factor("heat", "Severe", "SPEC_NOTFALL", self.m), 0.20)

    def test_unmatched_specialty_zero(self):
        self.assertEqual(fu.uplift_factor("heat", "Severe", "orthopaedics", self.m), 0.0)

    def test_unmatched_severity_zero(self):
        self.assertEqual(fu.uplift_factor("heat", "Minor", "geriatrics", self.m), 0.0)


class TestWindow(unittest.TestCase):
    def test_in_window_inclusive(self):
        self.assertTrue(fu.signal_applies("2026-07-21", "2026-07-20", "2026-07-22"))
        self.assertTrue(fu.signal_applies("2026-07-20", "2026-07-20", "2026-07-22"))

    def test_out_of_window(self):
        self.assertFalse(fu.signal_applies("2026-07-23", "2026-07-20", "2026-07-22"))

    def test_null_expiry_is_open_ended(self):
        self.assertTrue(fu.signal_applies("2026-07-23", "2026-07-20", None))


class TestCombine(unittest.TestCase):
    def test_single_factor(self):
        self.assertAlmostEqual(fu.combine(100.0, [0.25]), 125.0)

    def test_multiplicative_overlap(self):
        self.assertAlmostEqual(fu.combine(100.0, [0.25, 0.20]), 150.0)

    def test_clamp(self):
        self.assertAlmostEqual(fu.combine(100.0, [0.5, 0.5, 0.5], clamp=2.0), 200.0)

    def test_no_factors_is_base(self):
        self.assertAlmostEqual(fu.combine(100.0, []), 100.0)


if __name__ == "__main__":
    unittest.main()
