import unittest
from unittest.mock import patch

from daily_report_service import DailyReportService


class DailyReportServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.service = DailyReportService()
        self.filter_payload = {
            "date": "2026-04-14",
            "news": [
                {
                    "id": "n1",
                    "title": "Agent products reshape workflows",
                    "url": "https://example.com/1",
                    "content": "content",
                    "source": "Example",
                    "theme_tags": ["workflow"],
                    "final_score": 8.0,
                    "signal_level": "S",
                }
            ],
        }

    def test_service_falls_back_when_ai_analysis_fails(self):
        with patch.object(self.service.ai_analyzer, "analyze_daily_report_v3", return_value=None):
            report = self.service.build(self.filter_payload, raw_news_count=1)

        self.assertEqual(report["meta"]["report_type"], "daily")
        self.assertIn("internal_candidates", report)
        self.assertIn("trend_candidates", report["internal_candidates"])


if __name__ == "__main__":
    unittest.main()
