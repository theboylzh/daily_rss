import unittest
from unittest.mock import patch

from ai_analyzer_v3 import AIAnalyzerV3


class AIAnalyzerV3TestCase(unittest.TestCase):
    def setUp(self):
        self.analyzer = AIAnalyzerV3()
        self.filter_payload = {
            "date": "2026-04-14",
            "news": [
                {
                    "id": "news_1",
                    "title": "Agent products are moving into workflow control",
                    "url": "https://example.com/1",
                    "content": "Agent products now orchestrate workflow steps and replace manual switching.",
                    "source": "Example",
                    "theme_tags": ["workflow", "ai_product"],
                    "final_score": 8.6,
                    "signal_level": "S",
                },
                {
                    "id": "news_2",
                    "title": "Coding copilots improve reasoning and execution",
                    "url": "https://example.com/2",
                    "content": "Coding systems are becoming more reliable on multi-step software tasks.",
                    "source": "Example",
                    "theme_tags": ["coding", "ai_model"],
                    "final_score": 7.8,
                    "signal_level": "A",
                },
            ],
        }

    def test_analyze_daily_report_v3_outputs_json_schema(self):
        signal_json = {
            "main_conclusion": "Today the key shift is workflow control.",
            "why_it_matters": "This affects how products are built.",
            "top_signals": [
                {
                    "title": "Agent workflow control",
                    "event": "Products orchestrate tasks",
                    "signal": "AI is moving from feature to flow",
                    "for_me": "Need to study workflow design",
                    "score": 9,
                    "supporting_news": [{"news_id": "news_1", "title": "Agent products are moving into workflow control", "source": "Example", "url": "https://example.com/1"}],
                },
                {
                    "title": "Coding leverage up",
                    "event": "Copilots improve reasoning",
                    "signal": "Builder ceiling is higher",
                    "for_me": "Need to revisit build scope",
                    "score": 8,
                    "supporting_news": [{"news_id": "news_2", "title": "Coding copilots improve reasoning and execution", "source": "Example", "url": "https://example.com/2"}],
                },
                {
                    "title": "Design and product merge",
                    "event": "Workflow tools reshape UX",
                    "signal": "Roles are converging",
                    "for_me": "Need integrated product thinking",
                    "score": 7,
                    "supporting_news": [{"news_id": "news_1", "title": "Agent products are moving into workflow control", "source": "Example", "url": "https://example.com/1"}],
                },
            ],
            "six_dimension_briefs": {
                "model_and_capability": {"summary": "up", "brief": "up", "related_news": []},
                "ai_product_and_interaction": {"summary": "up", "brief": "up", "related_news": []},
                "design_and_experience": {"summary": "up", "brief": "up", "related_news": []},
                "technology_and_platform": {"summary": "up", "brief": "up", "related_news": []},
                "business_and_monetization": {"summary": "up", "brief": "up", "related_news": []},
                "policy_and_ethics": {"summary": "up", "brief": "up", "related_news": []},
            },
        }
        deep_json = [
            {
                "trend_name": "工作流自动化深化",
                "summary": "Automation is moving deeper into execution.",
                "related_signals": ["Agent workflow control"],
                "repeated_patterns": ["Workflow becomes entry point"],
                "drivers": ["Agent UX", "Model capability"],
                "mechanism": "Products now operate steps instead of exposing tools.",
                "short_term_impact": "More workflow redesign",
                "long_term_impact": "New builder leverage",
                "impact_on_me": "Need to model workflows better",
                "risks": ["Over-automation"],
                "opportunities": ["Build workflow products"],
                "watch_points": ["Retention"],
                "supporting_news": [{"news_id": "news_1", "title": "Agent products are moving into workflow control", "source": "Example", "url": "https://example.com/1"}],
            },
            {
                "trend_name": "AI 编程协作强化",
                "summary": "Coding systems handle more complex tasks.",
                "related_signals": ["Coding leverage up"],
                "repeated_patterns": ["Reasoning and execution rising"],
                "drivers": ["Model quality"],
                "mechanism": "Coding assistance becomes semi-autonomous.",
                "short_term_impact": "Faster prototyping",
                "long_term_impact": "Broader solo build scope",
                "impact_on_me": "Need to upgrade coding workflow",
                "risks": ["False confidence"],
                "opportunities": ["Ship more experiments"],
                "watch_points": ["Reliability"],
                "supporting_news": [{"news_id": "news_2", "title": "Coding copilots improve reasoning and execution", "source": "Example", "url": "https://example.com/2"}],
            },
        ]
        action_json = {
            "today": [{"target": "workflow", "action": "map one workflow", "purpose": "clarify flow", "effort": "low"}],
            "this_week": [{"target": "prototype", "action": "build one demo", "purpose": "test value", "effort": "medium"}],
            "this_month": [{"target": "system", "action": "create repeatable method", "purpose": "compound learning", "effort": "high"}],
        }

        with patch.object(self.analyzer, "_call_json", side_effect=[signal_json, deep_json, action_json]):
            report = self.analyzer.analyze_daily_report_v3(self.filter_payload, raw_news_count=2)

        self.assertEqual(report["meta"]["report_type"], "daily")
        self.assertIn("signal_interpretation", report)
        self.assertIn("deep_analysis", report)
        self.assertIn("action_suggestions", report)
        self.assertIn("internal_candidates", report)
        self.assertGreaterEqual(len(report["deep_analysis"]), 2)

    def test_ai_call_retries_and_then_fallback_can_take_over(self):
        with patch("ai_analyzer_v3.httpx.Client") as mocked_client:
            mocked_client.return_value.__enter__.return_value.post.side_effect = Exception("network down")
            with patch("ai_analyzer_v3.time.sleep"):
                result = self.analyzer._call_ai_api("test prompt")

        self.assertIsNone(result)
        self.assertEqual(mocked_client.return_value.__enter__.return_value.post.call_count, 3)


if __name__ == "__main__":
    unittest.main()
