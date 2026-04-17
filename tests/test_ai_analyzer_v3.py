import unittest
from unittest.mock import patch

from ai_analyzer_v3 import AIAnalyzerV3


class AIAnalyzerV3TestCase(unittest.TestCase):
    """AIAnalyzerV3 单元测试 - MVP 最小可运行验证"""

    def setUp(self):
        self.analyzer = AIAnalyzerV3()
        self.filter_payload = {
            "date": "2026-04-15",
            "news": [
                {
                    "id": "news_1",
                    "title": "OpenAI 宣布 GPT-4o API 降价 50%",
                    "url": "https://example.com/1",
                    "content": "OpenAI 官方宣布 GPT-4o API 价格下调 50%，即日起生效。这是 3 周内第 2 家头部厂商降价。",
                    "source": "The Decoder",
                    "theme_tags": ["ai_model", "business"],
                    "final_score": 9.2,
                    "signal_level": "S",
                },
                {
                    "id": "news_2",
                    "title": "Anthropic 跟进降价 Claude API",
                    "url": "https://example.com/2",
                    "content": "Anthropic 宣布 Claude API 降价 30%，4 月 20 日生效。",
                    "source": "TechCrunch",
                    "theme_tags": ["ai_model", "business"],
                    "final_score": 8.5,
                    "signal_level": "A",
                },
                {
                    "id": "news_3",
                    "title": "Agent 产品进入工作流控制阶段",
                    "url": "https://example.com/3",
                    "content": "新一代 Agent 产品开始接管用户工作流执行，减少手动切换。",
                    "source": "VentureBeat",
                    "theme_tags": ["ai_product", "workflow"],
                    "final_score": 7.8,
                    "signal_level": "A",
                },
            ],
        }

    def test_analyze_daily_report_v3_schema(self):
        """测试：AI 分析器输出符合 V3.5 schema"""
        # Mock AI 返回（新 schema V3.5）
        signal_json = {
            "main_conclusion": "今日 AI 行业价格战初现，应用层创业窗口期已至",
            "why_it_matters": "头部厂商降价将在 2-4 周内传导至应用层，降低创业成本但加剧竞争",
            "top_events": [
                {
                    "title": "OpenAI 宣布 GPT-4o API 降价 50%",
                    "description": "4 月 15 日 OpenAI 官方宣布 GPT-4o API 价格下调 50%，即日起生效。这是 3 周内第 2 家头部厂商降价。",
                    "so_what": "如果依赖 GPT-4o API，可暂缓自研模型，利用成本窗口期验证市场"
                },
                {
                    "title": "Anthropic 跟进降价",
                    "description": "4 月 15 日 Anthropic 宣布 Claude API 降价 30%，4 月 20 日生效。",
                    "so_what": "多模型供应商竞争，用户可考虑多供应商策略降低成本"
                },
                {
                    "title": "Agent 产品进入工作流控制",
                    "description": "新一代 Agent 产品开始接管用户工作流执行，减少手动切换应用。",
                    "so_what": "学习工作流设计，整合到你的产品中"
                }
            ],
            "six_dimension_briefs": {
                "model_and_capability": "模型能力提升，价格下降，创业门槛降低",
                "ai_product_and_interaction": "产品进入工作流整合阶段，竞争加剧",
                "design_and_experience": "今日无显著动态",
                "technology_and_platform": "API 成本下降利好开发者",
                "business_and_monetization": "价格战压缩利润空间，需寻找差异化",
                "policy_and_ethics": "今日无显著动态"
            }
        }

        deep_json = [
            {
                "type": "trend_observation",
                "id": "obs_2026-04-15_1",
                "title": "AI 价格战初现",
                "evidence": "OpenAI 降价 50%，3 周内第 2 家头部厂商，可能是价格战雏形",
                "news_ids": ["news_1", "news_2"],
                "reasoning": "头部降价→创业门槛降低→应用层竞争加剧。如果 7 天内其他厂商不跟进则判断不成立。4 月 22 日前观察国内云厂商定价。",
                "so_what_for_me": "暂缓自研模型，利用成本窗口期验证市场"
            },
            {
                "type": "trend_observation",
                "id": "obs_2026-04-15_2",
                "title": "工作流整合成为主流",
                "evidence": "Agent 产品开始接管工作流执行，这是模式雏形",
                "news_ids": ["news_3"],
                "reasoning": "工作流整合→用户粘性提升→切换成本增加。需要观察留存率来确认。",
                "so_what_for_me": "学习工作流设计，整合到产品中"
            },
            {
                "type": "trend_observation",
                "id": "obs_2026-04-15_3",
                "title": "AI 编程协作强化",
                "evidence": "Coding copilot 可处理多步软件任务，这是单点事件",
                "news_ids": ["news_2"],
                "reasoning": "编程辅助→半自主→独立开发。如果可靠性无提升则判断降级。",
                "so_what_for_me": "升级编程工作流，尝试更多实验"
            }
        ]

        action_json = {
            "today": [
                {"target": "API 供应商", "action": "调研当前供应商价格", "purpose": "评估成本节省空间", "effort": "low"}
            ],
            "this_week": [
                {"target": "原型", "action": "构建一个 demo", "purpose": "验证市场价值", "effort": "medium"}
            ],
            "this_month": [
                {"target": "系统", "action": "创建可复用方法", "purpose": "积累学习", "effort": "high"}
            ]
        }

        with patch.object(self.analyzer, "_call_json", side_effect=[signal_json, deep_json, action_json]):
            report = self.analyzer.analyze_daily_report_v3(self.filter_payload, raw_news_count=3)

        # 验证 meta
        self.assertEqual(report["meta"]["report_type"], "daily")
        self.assertEqual(report["meta"]["date"], "2026-04-15")
        self.assertEqual(report["meta"]["news_count"], 3)

        # 验证 signal_interpretation
        si = report["signal_interpretation"]
        self.assertIn("main_conclusion", si)
        self.assertIn("why_it_matters", si)
        self.assertEqual(len(si["top_events"]), 3)
        for event in si["top_events"]:
            self.assertIn("title", event)
            self.assertIn("description", event)
            self.assertIn("so_what", event)

        # 验证 six_dimension_briefs
        six = si["six_dimension_briefs"]
        self.assertEqual(len(six), 6)
        for key in six:
            self.assertIsInstance(six[key], str)

        # 验证 deep_analysis
        da = report["deep_analysis"]
        self.assertGreaterEqual(len(da), 3)
        for obs in da:
            self.assertEqual(obs["type"], "trend_observation")
            self.assertIn("title", obs)
            self.assertIn("evidence", obs)
            self.assertIn("news_ids", obs)
            self.assertIn("reasoning", obs)
            self.assertIn("so_what_for_me", obs)

        # 验证 action_suggestions
        action = report["action_suggestions"]
        self.assertIn("today", action)
        self.assertIn("this_week", action)
        self.assertIn("this_month", action)

    def test_normalize_signal_interpretation(self):
        """测试：signal_interpretation 归一化逻辑"""
        result = {
            "main_conclusion": "测试结论",
            "why_it_matters": "测试原因",
            "top_events": [
                {
                    "title": "事件 1",
                    "description": "描述 1",
                    "so_what": "影响 1"
                },
                {
                    "title": "事件 2",
                    "description": "描述 2",
                    "so_what": "影响 2"
                }
            ],
            "six_dimension_briefs": {
                "model_and_capability": "模型能力提升",
                "ai_product_and_interaction": "产品整合加速"
            }
        }
        fallback = {
            "main_conclusion": "fallback 结论",
            "why_it_matters": "fallback 原因",
            "top_events": [],
            "six_dimension_briefs": {}
        }

        normalized = self.analyzer._normalize_signal_interpretation(result, fallback)

        self.assertEqual(normalized["main_conclusion"], "测试结论")
        self.assertEqual(len(normalized["top_events"]), 3)  # 应该补齐到 3 条
        self.assertEqual(normalized["six_dimension_briefs"]["model_and_capability"], "模型能力提升")

    def test_normalize_deep_analysis(self):
        """测试：deep_analysis 归一化逻辑"""
        result = [
            {
                "type": "trend_observation",
                "title": "趋势 1",
                "evidence": "证据 1",
                "news_ids": ["news_1"],
                "reasoning": "推理 1",
                "so_what_for_me": "影响 1"
            },
            {
                "type": "trend_observation",
                "title": "趋势 2",
                "evidence": "证据 2",
                "news_ids": ["news_2"],
                "reasoning": "推理 2",
                "so_what_for_me": "影响 2"
            }
        ]
        fallback = []

        normalized = self.analyzer._normalize_deep_analysis(result, fallback, "2026-04-15")

        self.assertEqual(len(normalized), 2)
        self.assertEqual(normalized[0]["type"], "trend_observation")
        self.assertEqual(normalized[0]["title"], "趋势 1")

    def test_ai_call_failure_returns_none(self):
        """测试：AI 调用失败时返回 None"""
        with patch("ai_analyzer_v3.httpx.Client") as mocked_client:
            mocked_client.return_value.__enter__.return_value.post.side_effect = Exception("network error")
            with patch("ai_analyzer_v3.time.sleep"):
                result = self.analyzer._call_ai_api("test prompt")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
