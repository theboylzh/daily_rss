"""
V3 邮件渲染模块的单元测试 - 测试 V3.5 schema 兼容性
"""
import unittest
from push_manager import PushManager


class TestV3EmailRender(unittest.TestCase):
    """测试 V3 邮件渲染功能"""

    def setUp(self):
        """测试前准备"""
        self.push_manager = PushManager()
        self.mock_v3_report = {
            "meta": {
                "report_type": "daily",
                "date": "2026-04-15",
                "news_count": 20,
                "filtered_count": 15,
            },
            "signal_interpretation": {
                "main_conclusion": "今日 AI 行业价格战初现，应用层创业窗口期已至",
                "why_it_matters": "头部厂商降价将在 2-4 周内传导至应用层，降低创业成本但加剧竞争",
                "top_events": [
                    {
                        "title": "OpenAI 宣布 GPT-4o API 降价 50%",
                        "description": "4 月 15 日 OpenAI 官方宣布 GPT-4o API 价格下调 50%，即日起生效。",
                        "so_what": "如果依赖 GPT-4o API，可暂缓自研模型，利用成本窗口期验证市场"
                    },
                    {
                        "title": "Anthropic 跟进降价 Claude API",
                        "description": "4 月 15 日 Anthropic 宣布 Claude API 降价 30%，4 月 20 日生效。",
                        "so_what": "多模型供应商竞争，用户可考虑多供应商策略降低成本"
                    },
                    {
                        "title": "Agent 产品进入工作流控制阶段",
                        "description": "新一代 Agent 产品开始接管用户工作流执行，减少手动切换。",
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
            },
            "deep_analysis": [
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
                }
            ],
            "action_suggestions": {
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
        }

    def test_v3_html_generation_success(self):
        """测试 V3 HTML 生成成功"""
        html = self.push_manager._generate_v3_daily_html_content(self.mock_v3_report)
        self.assertIsInstance(html, str)
        self.assertGreater(len(html), 2000)  # 确保生成了足够长度的 HTML

    def test_v3_html_contains_doctype(self):
        """测试生成的 HTML 包含 DOCTYPE 声明"""
        html = self.push_manager._generate_v3_daily_html_content(self.mock_v3_report)
        self.assertIn("<!DOCTYPE html>", html)

    def test_v3_html_contains_required_sections(self):
        """测试生成的 HTML 包含所有必需的板块"""
        html = self.push_manager._generate_v3_daily_html_content(self.mock_v3_report)

        required_sections = [
            'class="container"',
            '日期：',
            '筛选新闻：',
            '今日 AI 行业价格战初现',
            '为什么重要',
            '<h2>关键事件</h2>',
            '<h2>六维简报</h2>',
            '<h2>深度分析</h2>',
            '<h2>行动建议</h2>',
        ]

        for section in required_sections:
            self.assertIn(section, html, msg=f"缺少板块：{section}")

    def test_v3_top_events_render(self):
        """测试关键事件板块渲染"""
        html = self.push_manager._generate_v3_daily_html_content(self.mock_v3_report)
        self.assertIn("OpenAI 宣布 GPT-4o API 降价 50%", html)
        self.assertIn("对我意味着什么", html)

    def test_v3_six_dimensions_render(self):
        """测试六维简报板块渲染"""
        html = self.push_manager._generate_v3_daily_html_content(self.mock_v3_report)
        self.assertIn("模型能力提升", html)
        self.assertIn("产品进入工作流整合阶段", html)

    def test_v3_deep_analysis_render(self):
        """测试深度分析板块渲染"""
        html = self.push_manager._generate_v3_daily_html_content(self.mock_v3_report)
        self.assertIn("AI 价格战初现", html)
        self.assertIn("证据", html)
        self.assertIn("推理", html)
        self.assertIn("对我的影响", html)

    def test_v3_action_suggestions_render(self):
        """测试行动建议板块渲染"""
        html = self.push_manager._generate_v3_daily_html_content(self.mock_v3_report)
        self.assertIn("今天", html)
        self.assertIn("本周", html)
        self.assertIn("本月", html)
        self.assertIn("调研当前供应商价格", html)

    def test_v3_empty_report_handling(self):
        """测试空报告处理"""
        empty_report = {
            "meta": {"date": "2026-04-15", "filtered_count": 0},
            "signal_interpretation": {},
            "deep_analysis": [],
            "action_suggestions": {}
        }
        html = self.push_manager._generate_v3_daily_html_content(empty_report)
        self.assertIsInstance(html, str)
        self.assertIn("暂无主结论", html)
        self.assertIn("暂无事件", html)
        self.assertIn("暂无趋势分析", html)

    def test_v3_old_schema_compatibility(self):
        """测试旧 schema 兼容性回退"""
        old_schema_report = {
            "meta": {"date": "2026-04-15", "filtered_count": 5},
            "signal_interpretation": {
                "main_conclusion": "测试结论",
                "why_it_matters": "测试原因",
                "top_events": [],
                "six_dimension_briefs": {
                    "model_and_capability": {"summary": "旧格式摘要", "brief": "旧格式详情"}
                }
            },
            "deep_analysis": [],
            "action_suggestions": {}
        }
        html = self.push_manager._generate_v3_daily_html_content(old_schema_report)
        self.assertIsInstance(html, str)
        self.assertIn("旧格式摘要", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
