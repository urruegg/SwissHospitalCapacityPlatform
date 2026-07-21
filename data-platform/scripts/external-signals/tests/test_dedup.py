import unittest
from dedup import collapse
from normalize import build_record


def _rec(source, hazard, cantons, onset, sev="Severe"):
    return build_record(
        signal_id=f"{source}-1", source_id=source, source_authority=source.upper(),
        hazard_type=hazard, severity=sev, certainty="Observed", urgency="Immediate",
        region={"cantons": cantons}, onset=onset, status="Actual",
        connector_version="v1", licence="open", raw=b"{}",
    )


class TestDedup(unittest.TestCase):
    def test_overlapping_heat_collapses_to_one_event(self):
        recs = [_rec("meteoswiss", "heat", ["ZH"], "2026-07-17T12:00:00Z"),
                _rec("alertswiss", "heat", ["ZH"], "2026-07-17T12:00:00Z")]
        events = collapse(recs)
        self.assertEqual(len(events), 1)
        self.assertEqual(len(events[0]["sources"]), 2)

    def test_distinct_hazards_stay_separate(self):
        recs = [_rec("meteoswiss", "heat", ["ZH"], "2026-07-17T12:00:00Z"),
                _rec("sed", "earthquake", ["VS"], "2026-07-17T12:00:00Z")]
        self.assertEqual(len(collapse(recs)), 2)


if __name__ == "__main__":
    unittest.main()
