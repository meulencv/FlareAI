import unittest
from datetime import datetime, timedelta, timezone

from recency import apply_recency, parse_overlay_time, refresh_recency

NOW = datetime(2026, 9, 19, 11, 10, tzinfo=timezone.utc)


class RecencyTests(unittest.TestCase):
    def test_madrid_timestamp_is_converted_to_utc(self):
        parsed = parse_overlay_time("19-09-2026 13:05:00", "Europe/Madrid")
        self.assertEqual(parsed, datetime(2026, 9, 19, 11, 5, tzinfo=timezone.utc))

    def test_canary_timezone_is_different(self):
        parsed = parse_overlay_time("19/09/2026 12:05:00", "Atlantic/Canary")
        self.assertEqual(parsed, datetime(2026, 9, 19, 11, 5, tzinfo=timezone.utc))

    def test_unknown_incomplete_invalid_or_ambiguous_clock_is_rejected(self):
        for value in (None, "13:05:00", "31-02-2026 13:05:00", "2026-09-19 25:00:00",
                      "25-10-2026 02:30:00", "29-03-2026 02:30:00", "19-09-2026 13:05:00 UTC"):
            self.assertIsNone(parse_overlay_time(value, "Europe/Madrid"))
        self.assertIsNone(parse_overlay_time("19-09-2026 13:05:00", "unknown"))

    def visual(self):
        return {"density": "moderate", "vehicle_count_estimate": 12, "image_status": "road_visible", "limitations": [], "reason": "Coches visibles"}

    def test_ten_minutes_is_allowed_but_one_more_second_is_stale(self):
        recent = apply_recency(self.visual(), "19-09-2026 13:00:00", True, "Europe/Madrid", NOW)
        self.assertEqual(recent["freshness"], "recent")
        self.assertEqual(recent["vehicle_count_estimate"], 12)
        old = refresh_recency(recent, NOW + timedelta(seconds=1))
        self.assertEqual(old["freshness"], "stale")
        self.assertIsNone(old["vehicle_count_estimate"])
        self.assertEqual(old["visual_estimate"]["vehicle_count_estimate"], 12)

    def test_analysis_time_never_renews_capture_age(self):
        old = apply_recency(self.visual(), "19-09-2026 12:59:00", True, "Europe/Madrid", NOW)
        self.assertEqual(old["freshness"], "stale")
        self.assertEqual(old["density"], "unknown")
        self.assertEqual(old["analyzed_at"], NOW.isoformat())

    def test_missing_unreadable_or_future_clock_abstains(self):
        for text, legible in [(None, False), ("19-09-2026 13:05:00", False), ("19-09-2026 13:11:00", True)]:
            result = apply_recency(self.visual(), text, legible, "Europe/Madrid", NOW)
            self.assertNotEqual(result["freshness"], "recent")
            self.assertIsNone(result["vehicle_count_estimate"])
            self.assertFalse(result["dispatch_authorized"])

    def test_future_clock_does_not_become_valid_by_waiting(self):
        result = apply_recency(self.visual(), "19-09-2026 13:11:00", True, "Europe/Madrid", NOW)
        later = refresh_recency(result, NOW + timedelta(minutes=3))
        self.assertEqual(later["freshness"], "future")
        self.assertIsNone(later["vehicle_count_estimate"])

    def test_embedded_timezones_work_when_sandbox_has_no_zone_database(self):
        import recency
        from unittest.mock import patch
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
        from remote_setup import timezone_payload
        real_from_file = ZoneInfo.from_file
        with patch.dict(recency.EMBEDDED_TZDATA, timezone_payload()), patch.object(recency, "ZoneInfo") as zone:
            zone.side_effect = ZoneInfoNotFoundError("No timezone database")
            zone.from_file.side_effect = real_from_file
            self.assertEqual(parse_overlay_time("19-09-2026 13:05:00", "Europe/Madrid"), datetime(2026, 9, 19, 11, 5, tzinfo=timezone.utc))

    def test_ocr_is_not_advertised_as_independent_verification(self):
        result = apply_recency(self.visual(), "19-09-2026 13:05:00", True, "Europe/Madrid", NOW)
        self.assertFalse(result["capture_time_verified"])
        self.assertEqual(result["capture_time_source"], "image_overlay_ai_transcription")
        self.assertTrue(result["requires_human_review"])

    def test_unusable_image_never_becomes_usable_from_its_clock(self):
        visual = {**self.visual(), "image_status": "unavailable"}
        result = apply_recency(visual, "19-09-2026 13:05:00", True, "Europe/Madrid", NOW)
        self.assertEqual(result["density"], "unknown")
        self.assertIsNone(result["vehicle_count_estimate"])


if __name__ == "__main__":
    unittest.main()
