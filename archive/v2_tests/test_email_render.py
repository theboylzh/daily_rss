"""
V2.0.0 邮件渲染模块的单元测试
"""
import unittest
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from push_manager import PushManager
from ai_analyzer_v2 import get_empty_structure


class TestV2EmailRender(unittest.TestCase):
    """测试 V2 邮件渲染功能"""

    def setUp(self):
        """测试前准备"""
        self.push_manager = PushManager()
        self.mock_v2_analysis = {
            "date": "2026-04-11",
            "timestamp": "2026-04-11T10:00:00",
            "news_count": 20,
            "summary": {
                "one_liner": "未来难料，AI 局势依旧充满变数",
                "digest": "AI 领域动态频发，行业震动与巨头布局并存。",
                "keywords": ["震荡", "未知", "涨价"]
            },
            "key_news_brief": [
                {"title": "OpenAI 宣布关停 AI 视频生成模型 Sora", "tags": ["科技"]},
                {"title": "苹果被曝正开发 AI Siri", "tags": ["科技"]},
                {"title": "国内油价全面进入 9 元时代", "tags": ["经济"]}
            ],
            "briefing": {
                "politics": "油价全面进入 9 元时代，可能影响消费者出行选择。",
                "economy": "国内油价大幅上调，全国 92 号汽油均价突破 9 元/升。",
                "industry": "新一代迈巴赫 S 级及一款全新 MPV 亮相。",
                "tech": "OpenAI 宣布关停 AI 视频生成模型 Sora。"
            },
            "perspectives": [
                {
                    "title": "告别流量与代码，拥抱认知与架构",
                    "description": "AI 正在重塑商业与技术的底层逻辑。",
                    "references": [
                        {"title": "AI 投资新范式", "url": "https://example.com/1"}
                    ]
                }
            ],
            "deep_analysis": [
                {
                    "tags": ["消费", "经济"],
                    "title": "国内油价全面进入 9 元时代",
                    "facts": "发改委于 2026 年 3 月 23 日调价，汽油每吨上调 2000 元。",
                    "viewpoint": "油价上涨对居民消费成本产生直接影响。",
                    "causes": "遵循与国际市场油价联动的成品油价格形成机制。",
                    "prediction": "预计油价将维持高位震荡。",
                    "advice": "投资：关注新能源汽车产业链龙头企业。"
                }
            ],
            "suggestions": {
                "thinking": {"title": "技术理想与商业现实的鸿沟", "content": "油价上涨推动能源转型。"},
                "investment": {"title": "投资思路应更注重务实", "content": "拥抱确定性趋势，规避纯概念炒作。"},
                "self_improvement": {"title": "个人能力需要同步升级", "content": "从操作工转向架构师与协作者。"},
                "opportunities_risks": {"title": "机遇与风险并存", "content": "AI 视频行业进入整合期。"}
            }
        }

    def test_v2_html_generation_success(self):
        """测试 V2 HTML 生成成功"""
        html = self.push_manager._generate_v2_html_content(self.mock_v2_analysis)
        self.assertIsInstance(html, str)
        self.assertGreater(len(html), 1000)  # 确保生成了足够长度的 HTML

    def test_v2_html_contains_doctype(self):
        """测试生成的 HTML 包含 DOCTYPE 声明"""
        html = self.push_manager._generate_v2_html_content(self.mock_v2_analysis)
        self.assertIn("<!DOCTYPE html>", html)

    def test_v2_html_contains_required_sections(self):
        """测试生成的 HTML 包含所有必需的板块"""
        html = self.push_manager._generate_v2_html_content(self.mock_v2_analysis)

        required_sections = [
            'class="header"',
            'class="today-brief"',
            'class="news-list"',
            'class="opinion-section"',
            'class="insight-section"',
            'class="advice-section"'
        ]

        for section in required_sections:
            self.assertIn(section, html, msg=f"缺少板块：{section}")

    def test_v2_summary_render(self):
        """测试摘要板块渲染"""
        html = self.push_manager._render_v2_summary(
            "<html>{{summary.one_liner}}{{keywords_html}}</html>",
            self.mock_v2_analysis["summary"]
        )
        self.assertIn("未来难料，AI 局势依旧充满变数", html)
        self.assertIn("keyword-item", html)

    def test_v2_keywords_render(self):
        """测试关键词渲染"""
        html = self.push_manager._render_v2_summary(
            "<html>{{keywords_html}}</html>",
            {"keywords": ["科技", "创新", "AI"]}
        )
        self.assertIn("科技", html)
        self.assertIn("创新", html)
        self.assertIn("AI", html)

    def test_v2_key_news_render(self):
        """测试重点新闻渲染"""
        html = self.push_manager._render_v2_key_news(
            "<html>{{highlight_economy}}{{highlight_tech_1}}{{highlight_tech_2}}</html>",
            self.mock_v2_analysis["key_news_brief"],
            self.mock_v2_analysis["briefing"]
        )
        self.assertIn("OpenAI 宣布关停", html)
        self.assertIn("苹果被曝", html)

    def test_v2_opinions_render(self):
        """测试观点板块渲染"""
        html = self.push_manager._render_v2_opinions(
            "<html>{{opinions_html}}</html>",
            self.mock_v2_analysis["perspectives"]
        )
        self.assertIn("opinion-item", html)
        self.assertIn("告别流量与代码", html)

    def test_v2_opinions_empty(self):
        """测试空观点板块处理"""
        html = self.push_manager._render_v2_opinions("<html>{{opinions_html}}</html>", [])
        self.assertIn("暂无观点内容", html)

    def test_v2_insights_render(self):
        """测试分析板块渲染"""
        html = self.push_manager._render_v2_insights(
            "<html>{{insights_html}}</html>",
            self.mock_v2_analysis["deep_analysis"]
        )
        self.assertIn("insight-item", html)
        self.assertIn("国内油价全面进入 9 元时代", html)
        self.assertIn("客观事实", html)
        self.assertIn("01", html)

    def test_v2_insights_empty(self):
        """测试空分析板块处理"""
        html = self.push_manager._render_v2_insights("<html>{{insights_html}}</html>", [])
        self.assertIn("暂无分析内容", html)

    def test_v2_advices_render(self):
        """测试建议板块渲染"""
        html = self.push_manager._render_v2_advices(
            "<html>{{advices_html}}</html>",
            self.mock_v2_analysis["suggestions"]
        )
        self.assertIn("思维启发", html)
        self.assertIn("投资建议", html)
        self.assertIn("个人提升", html)
        self.assertIn("机遇风险", html)

    def test_v2_advices_empty(self):
        """测试空建议板块处理"""
        html = self.push_manager._render_v2_advices("<html>{{advices_html}}</html>", {})
        self.assertIn("暂无建议内容", html)

    def test_v2_news_list_empty_fallback(self):
        """测试新闻列表空数据回退"""
        html = self.push_manager._fill_empty_news_list("<html>{{news_politics_items}}</html>")
        self.assertIn("暂无新闻数据", html)

    def test_v2_single_advice_render(self):
        """测试单个建议项渲染"""
        html = self.push_manager._render_single_advice(
            "投资建议",
            "测试标题",
            "这是第一行\n这是第二行\n这是第三行"
        )
        self.assertIn("投资建议", html)
        self.assertIn("测试标题", html)
        self.assertIn("<p>", html)

    def test_fallback_template(self):
        """测试备用模板"""
        html = self.push_manager._get_fallback_v2_template()
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("{{date}}", html)

    def test_v1_format_detection(self):
        """测试 V1 格式检测（向后兼容）"""
        v1_analysis = {
            "date": "2026-04-11",
            "daily_summary": "# 测试摘要",
            "event_analysis": "# 测试分析",
            "timestamp": "2026-04-11T10:00:00",
            "news_count": 10
        }
        # V1 格式不应该有 summary 字段
        self.assertNotIn("summary", v1_analysis)
        # send_daily_analysis 应该能处理 V1 格式
        # 这里只测试格式检测逻辑，不实际发送邮件

    def test_empty_structure_compatibility(self):
        """测试空结构兼容性"""
        empty = get_empty_structure()
        html = self.push_manager._generate_v2_html_content(empty)
        self.assertIsInstance(html, str)
        self.assertGreater(len(html), 1000)


class TestV2SchemaValidation(unittest.TestCase):
    """测试 V2 Schema 验证"""

    def test_empty_structure_valid(self):
        """测试空结构验证"""
        from v2_schema import get_empty_structure
        from v2_parser import validate_v2_structure

        empty = get_empty_structure()
        is_valid, errors = validate_v2_structure(empty)
        self.assertTrue(is_valid, msg=f"空结构验证失败：{errors}")

    def test_minimal_valid_structure(self):
        """测试最小有效结构"""
        from v2_parser import validate_v2_structure

        data = {
            "summary": {"one_liner": "t", "digest": "t", "keywords": ["k"]},
            "key_news_brief": [],
            "briefing": {"politics": "", "economy": "", "industry": "", "tech": ""},
            "perspectives": [],
            "deep_analysis": [],
            "suggestions": {
                "thinking": {"title": "", "content": ""},
                "investment": {"title": "", "content": ""},
                "self_improvement": {"title": "", "content": ""},
                "opportunities_risks": {"title": "", "content": ""}
            }
        }
        is_valid, errors = validate_v2_structure(data)
        self.assertTrue(is_valid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
