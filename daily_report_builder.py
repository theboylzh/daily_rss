from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List


class DailyReportBuilder:
    """构建符合 V3 schema 的日报 JSON。"""

    DIMENSION_KEYS = {
        "model_and_capability": ("ai_model", "research"),
        "ai_product_and_interaction": ("ai_product", "workflow"),
        "design_and_experience": ("design",),
        "technology_and_platform": ("coding", "research"),
        "business_and_monetization": ("business",),
        "policy_and_ethics": ("policy",),
    }

    DIMENSION_TITLES = {
        "model_and_capability": "模型与能力",
        "ai_product_and_interaction": "AI 产品与交互",
        "design_and_experience": "设计与体验",
        "technology_and_platform": "技术与平台",
        "business_and_monetization": "商业化与变现",
        "policy_and_ethics": "政策与伦理",
    }

    ACTION_TARGETS = {
        "ai_model": "模型能力跟踪",
        "ai_product": "产品判断",
        "workflow": "工作流实验",
        "design": "设计方法升级",
        "coding": "开发工具栈",
        "business": "商业机会判断",
        "policy": "风险边界",
        "research": "研究趋势追踪",
        "general_ai": "AI 动态追踪",
    }

    def build(self, filter_payload: Dict[str, Any], raw_news_count: int = None) -> Dict[str, Any]:
        date_str = filter_payload.get("date") or datetime.now().strftime("%Y-%m-%d")
        news_items = filter_payload.get("news", [])
        top_news = sorted(news_items, key=lambda item: item.get("final_score", 0), reverse=True)

        report = {
            "meta": {
                "report_type": "daily",
                "date": date_str,
                "news_count": raw_news_count if raw_news_count is not None else len(news_items),
                "filtered_count": len(news_items),
            },
            "signal_interpretation": self._build_signal_interpretation(top_news, date_str),
            "deep_analysis": self._build_deep_analysis(top_news, date_str),
            "action_suggestions": {"today": [], "this_week": [], "this_month": []},
            "internal_candidates": {
                "trend_candidates": [],
                "opportunity_candidates": [],
            },
        }

        report["action_suggestions"] = self._build_action_suggestions(report["deep_analysis"], date_str)
        report["internal_candidates"] = self._build_internal_candidates(report["deep_analysis"], date_str)
        return report

    def build_internal_candidates(self, deep_analysis: List[Dict[str, Any]], date_str: str) -> Dict[str, List[Dict[str, Any]]]:
        return self._build_internal_candidates(deep_analysis, date_str)

    def _build_signal_interpretation(self, news_items: List[Dict[str, Any]], date_str: str) -> Dict[str, Any]:
        top_signals = []
        for index, item in enumerate(news_items[:3], start=1):
            top_signals.append({
                "id": "signal_%s_%s" % (date_str, index),
                "title": item.get("title", "今日关键信号"),
                "event": self._truncate(item.get("content", ""), 80),
                "signal": self._signal_summary(item),
                "for_me": self._for_me_summary(item),
                "score": round(item.get("final_score", 0), 1),
                "supporting_news": [self._supporting_news_item(item)],
            })

        main_conclusion = self._signal_summary(news_items[0]) if news_items else "今日暂无足够强的行业信号，继续观察。"
        why_it_matters = self._for_me_summary(news_items[0]) if news_items else "当前信息密度不足，适合保留带问题意识的跟踪。"

        return {
            "main_conclusion": main_conclusion,
            "why_it_matters": why_it_matters,
            "top_signals": top_signals,
            "six_dimension_briefs": self._build_six_dimension_briefs(news_items),
        }

    def _build_six_dimension_briefs(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        dimension_news = dict((key, []) for key in self.DIMENSION_KEYS)
        fallback_pool = news_items[:2]

        for item in news_items:
            tags = set(item.get("theme_tags", []))
            for dimension, keywords in self.DIMENSION_KEYS.items():
                if tags.intersection(keywords):
                    dimension_news[dimension].append(item)

        briefs = {}
        for dimension, items in dimension_news.items():
            picked = items[:2] if items else fallback_pool[:1]
            title = self.DIMENSION_TITLES[dimension]
            if picked:
                lead = picked[0]
                summary = "%s出现了新的推进信号。" % title
                brief = "%s 是当前最直接的代表事件，说明这一维度正在发生可追踪的变化。" % lead.get("title", "暂无标题")
                related_news = [self._supporting_news_item(item) for item in picked]
            else:
                summary = "%s暂无突出变化。" % title
                brief = "今天这一维度的有效信号较弱，建议继续观察后续连续性。"
                related_news = []

            briefs[dimension] = {
                "summary": summary,
                "brief": brief,
                "related_news": related_news,
            }

        return briefs

    def _build_deep_analysis(self, news_items: List[Dict[str, Any]], date_str: str) -> List[Dict[str, Any]]:
        grouped = defaultdict(list)
        for item in news_items:
            primary_tag = item.get("theme_tags", ["general_ai"])[0]
            grouped[primary_tag].append(item)

        sorted_groups = sorted(
            grouped.items(),
            key=lambda pair: max(news.get("final_score", 0) for news in pair[1]),
            reverse=True,
        )

        trends = []
        for index, (tag, items) in enumerate(sorted_groups[:3], start=1):
            lead = items[0]
            trends.append({
                "id": "daily_trend_%s_%s" % (date_str, index),
                "trend_name": self._trend_name(tag),
                "summary": self._signal_summary(lead),
                "repeated_patterns": [self._repeated_pattern(tag, items)],
                "drivers": [self._driver_summary(item) for item in items[:2]],
                "mechanism": self._mechanism_summary(tag),
                "short_term_impact": self._short_term_impact(tag),
                "long_term_impact": self._long_term_impact(tag),
                "impact_on_me": self._for_me_summary(lead),
                "watch_points": [self._watch_point(item) for item in items[:2]],
                "supporting_news": [self._supporting_news_item(item) for item in items[:3]],
            })

        return trends

    def _build_action_suggestions(self, deep_analysis: List[Dict[str, Any]], date_str: str) -> Dict[str, List[Dict[str, Any]]]:
        buckets = {"today": [], "this_week": [], "this_month": []}
        for index, trend in enumerate(deep_analysis, start=1):
            target = self.ACTION_TARGETS.get(self._tag_from_trend(trend.get("trend_name", "")), "方向判断")
            buckets["today"].append({
                "id": "action_%s_today_%s" % (date_str, index),
                "target": target,
                "action": "记录并拆解 %s 的关键案例" % trend.get("trend_name", "该趋势"),
                "purpose": "形成当日判断，而不是只停留在看新闻。",
                "effort": "low",
                "source_reference": "trend:%s" % trend["id"],
            })
            buckets["this_week"].append({
                "id": "action_%s_this_week_%s" % (date_str, index),
                "target": target,
                "action": "围绕 %s 做一次最小实验或整理" % trend.get("trend_name", "该趋势"),
                "purpose": "验证趋势是否值得纳入长期关注清单。",
                "effort": "medium",
                "source_reference": "trend:%s" % trend["id"],
            })
            buckets["this_month"].append({
                "id": "action_%s_this_month_%s" % (date_str, index),
                "target": target,
                "action": "把 %s 转成一个可复用的方法或项目方向" % trend.get("trend_name", "该趋势"),
                "purpose": "形成中期行动方向，而不是只停留在阅读层。",
                "effort": "high",
                "source_reference": "trend:%s" % trend["id"],
            })
        return buckets

    def _build_internal_candidates(self, deep_analysis: List[Dict[str, Any]], date_str: str) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "trend_candidates": [
                {
                    "id": trend["id"],
                    "name": trend["trend_name"],
                    "summary": trend["summary"],
                    "why_keep": trend["impact_on_me"],
                }
                for trend in deep_analysis
            ],
            "opportunity_candidates": [
                {
                    "id": "daily_opp_%s_%s" % (date_str, index),
                    "name": "%s 对应的小机会" % trend["trend_name"],
                    "type": "product",
                    "summary": trend["impact_on_me"],
                    "validation_idea": "用一页笔记或一个最小 demo 验证 %s 的真实需求。" % trend["trend_name"],
                }
                for index, trend in enumerate(deep_analysis, start=1)
            ],
        }

    def _supporting_news_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "news_id": item.get("id", ""),
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "url": item.get("url", ""),
        }

    def _signal_summary(self, item: Dict[str, Any]) -> str:
        tags = "、".join(item.get("theme_tags", [])[:2]) or "AI 行业"
        return "%s 方向的变化开始从零散消息转向可操作信号。" % tags

    def _for_me_summary(self, item: Dict[str, Any]) -> str:
        primary_tag = item.get("theme_tags", ["general_ai"])[0]
        return "这提示我需要尽快更新对 %s 的理解，并判断是否值得做实验。" % self._trend_name(primary_tag)

    def _repeated_pattern(self, tag: str, items: List[Dict[str, Any]]) -> str:
        return "%s 在多条新闻中重复出现，说明不是单点噪音。" % self._trend_name(tag)

    def _driver_summary(self, item: Dict[str, Any]) -> str:
        return self._truncate(item.get("title", ""), 40)

    def _mechanism_summary(self, tag: str) -> str:
        return "%s 正在通过产品、能力和市场反馈的联动逐渐放大影响。" % self._trend_name(tag)

    def _short_term_impact(self, tag: str) -> str:
        return "短期内，%s 会提高相关信息的决策优先级。" % self._trend_name(tag)

    def _long_term_impact(self, tag: str) -> str:
        return "长期看，%s 可能重塑个人能力结构和项目选择。" % self._trend_name(tag)

    def _watch_point(self, item: Dict[str, Any]) -> str:
        return "继续观察 %s 的后续落地反馈。" % self._truncate(item.get("title", ""), 36)

    def _trend_name(self, tag: str) -> str:
        return {
            "ai_model": "模型能力升级",
            "ai_product": "AI 产品化加速",
            "workflow": "工作流自动化深化",
            "design": "设计工作流重构",
            "coding": "AI 编程协作强化",
            "business": "AI 商业化推进",
            "policy": "AI 政策约束增强",
            "research": "研究与评测密度提升",
            "general_ai": "AI 行业变化",
        }.get(tag, "AI 行业变化")

    def _tag_from_trend(self, trend_name: str) -> str:
        mapping = {
            "模型能力升级": "ai_model",
            "AI 产品化加速": "ai_product",
            "工作流自动化深化": "workflow",
            "设计工作流重构": "design",
            "AI 编程协作强化": "coding",
            "AI 商业化推进": "business",
            "AI 政策约束增强": "policy",
            "研究与评测密度提升": "research",
            "AI 行业变化": "general_ai",
        }
        return mapping.get(trend_name, "general_ai")

    def _truncate(self, text: str, max_length: int) -> str:
        text = " ".join(text.split())
        if len(text) <= max_length:
            return text
        return text[: max_length - 1] + "…"
