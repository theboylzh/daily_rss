import json
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from config import settings
from daily_report_builder import DailyReportBuilder
from storage_manager import StorageManager


class AIAnalyzerV3:
    """V3 Daily AI 分析器，优先产出符合 v3 schema 的日报 JSON。"""

    DIMENSION_KEYS = [
        "model_and_capability",
        "ai_product_and_interaction",
        "design_and_experience",
        "technology_and_platform",
        "business_and_monetization",
        "policy_and_ethics",
    ]

    DEFAULT_DIMENSION_VALUE = {
        "summary": "今日无显著动态",
        "brief": "今日无显著动态",
        "related_news": [],
    }

    def __init__(self):
        self.api_url = settings.AI_API_URL
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL
        self.storage = StorageManager()
        self.daily_builder = DailyReportBuilder()

    def analyze_daily_report_v3(
        self,
        filter_payload: Dict[str, Any],
        raw_news_count: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        news_items = filter_payload.get("news", [])
        if not news_items or not self.api_key:
            return None

        date_str = filter_payload.get("date") or datetime.now().strftime("%Y-%m-%d")
        fallback_report = self.daily_builder.build(filter_payload, raw_news_count=raw_news_count)

        signal_interpretation = self._generate_signal_interpretation(news_items, fallback_report)
        if not signal_interpretation:
            return None

        deep_analysis = self._generate_deep_analysis(signal_interpretation, news_items, fallback_report)
        if not deep_analysis:
            return None

        action_suggestions = self._generate_action_suggestions(deep_analysis, fallback_report)
        if not action_suggestions:
            return None

        report = {
            "meta": {
                "report_type": "daily",
                "date": date_str,
                "news_count": raw_news_count if raw_news_count is not None else len(news_items),
                "filtered_count": len(news_items),
            },
            "signal_interpretation": signal_interpretation,
            "deep_analysis": deep_analysis,
            "action_suggestions": action_suggestions,
            "internal_candidates": self._build_internal_candidates(deep_analysis, date_str),
        }
        self.storage.write_json(self.storage.get_daily_report_path(date_str), report)
        return report

    def _generate_signal_interpretation(
        self,
        news_items: List[Dict[str, Any]],
        fallback_report: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        prompt = f"""
任务：基于给定的 filter_news，为 Trend Radar 生成“信号解读”模块。

输出要求：
1. 只能输出 JSON，不要 Markdown，不要解释。
2. 必须严格包含以下字段：
{{
  "main_conclusion": "今日最重要的结论",
  "why_it_matters": "为什么重要",
  "top_signals": [
    {{
      "title": "战略信号标题",
      "event": "发生了什么",
      "signal": "真正说明了什么变化",
      "for_me": "对我意味着什么",
      "score": 9,
      "supporting_news": [
        {{
          "news_id": "news_xxx",
          "title": "标题",
          "source": "来源",
          "url": "https://..."
        }}
      ]
    }}
  ],
  "six_dimension_briefs": {{
    "model_and_capability": {{"summary": "一句判断", "brief": "一段简报", "related_news": []}},
    "ai_product_and_interaction": {{"summary": "一句判断", "brief": "一段简报", "related_news": []}},
    "design_and_experience": {{"summary": "一句判断", "brief": "一段简报", "related_news": []}},
    "technology_and_platform": {{"summary": "一句判断", "brief": "一段简报", "related_news": []}},
    "business_and_monetization": {{"summary": "一句判断", "brief": "一段简报", "related_news": []}},
    "policy_and_ethics": {{"summary": "一句判断", "brief": "一段简报", "related_news": []}}
  }}
}}

硬性要求：
1. top_signals 固定 3 条。
2. six_dimension_briefs 固定 6 个字段，缺内容也要保留并写“今日无显著动态”。
3. supporting_news 和 related_news 只能引用输入新闻中的 news_id/title/source/url。
4. 结论必须围绕用户的判断和行动价值，而不是泛泛行业总结。

输入新闻：
{json.dumps(self._compact_news_for_prompt(news_items), ensure_ascii=False, indent=2)}
"""
        result = self._call_json(prompt)
        if not isinstance(result, dict):
            return None
        return self._normalize_signal_interpretation(
            result,
            fallback_report["signal_interpretation"],
        )

    def _generate_deep_analysis(
        self,
        signal_interpretation: Dict[str, Any],
        news_items: List[Dict[str, Any]],
        fallback_report: Dict[str, Any],
    ) -> Optional[List[Dict[str, Any]]]:
        prompt = f"""
任务：基于信号解读和 filter_news，生成 2-3 条“深度分析”趋势。

输出要求：
1. 只能输出 JSON 数组，不要 Markdown。
2. 固定输出 2 到 3 条。
3. 每条必须包含以下字段：
[
  {{
    "trend_name": "趋势名称",
    "summary": "趋势概述",
    "related_signals": ["相关信号标题1", "相关信号标题2"],
    "repeated_patterns": ["重复模式1", "重复模式2"],
    "drivers": ["驱动因素1", "驱动因素2"],
    "mechanism": "变化机制",
    "short_term_impact": "短期影响",
    "long_term_impact": "长期影响",
    "impact_on_me": "对我的影响",
    "risks": ["风险1", "风险2"],
    "opportunities": ["机会1", "机会2"],
    "watch_points": ["观察点1", "观察点2"],
    "supporting_news": [
      {{
        "news_id": "news_xxx",
        "title": "标题",
        "source": "来源",
        "url": "https://..."
      }}
    ]
  }}
]

硬性要求：
1. 重点是解释趋势，不是复述新闻。
2. supporting_news 只能引用输入新闻。
3. related_signals 应优先引用 top_signals 的 title。

信号解读：
{json.dumps(signal_interpretation, ensure_ascii=False, indent=2)}

输入新闻：
{json.dumps(self._compact_news_for_prompt(news_items), ensure_ascii=False, indent=2)}
"""
        result = self._call_json(prompt)
        if not isinstance(result, list):
            return None
        return self._normalize_deep_analysis(
            result,
            fallback_report["deep_analysis"],
            fallback_report["meta"]["date"],
        )

    def _generate_action_suggestions(
        self,
        deep_analysis: List[Dict[str, Any]],
        fallback_report: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        prompt = f"""
任务：基于深度分析结果，生成行动建议。

输出要求：
1. 只能输出 JSON。
2. 必须包含 today、this_week、this_month 三个字段。
3. 每个字段至少 2 条建议。
4. 每条建议必须包含 target、action、purpose、effort。

输出结构：
{{
  "today": [{{"target": "对象", "action": "动作", "purpose": "目的", "effort": "low"}}],
  "this_week": [{{"target": "对象", "action": "动作", "purpose": "目的", "effort": "medium"}}],
  "this_month": [{{"target": "对象", "action": "动作", "purpose": "目的", "effort": "high"}}]
}}

深度分析：
{json.dumps(deep_analysis, ensure_ascii=False, indent=2)}
"""
        result = self._call_json(prompt)
        if not isinstance(result, dict):
            return None
        return self._normalize_action_suggestions(
            result,
            fallback_report["action_suggestions"],
            fallback_report["meta"]["date"],
        )

    def _call_json(self, prompt: str) -> Optional[Any]:
        text = self._call_ai_api(prompt)
        if not text:
            return None
        return self._extract_json(text)

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个严格遵守 JSON 输出格式的 AI 行业分析师。"},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "max_tokens": 4096,
        }

        delay = settings.THIRD_LAYER_RETRY_DELAY
        for attempt in range(settings.THIRD_LAYER_RETRIES):
            try:
                with httpx.Client(
                    proxy=self._http_proxy(),
                    trust_env=False,
                ) as client:
                    response = client.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=settings.THIRD_LAYER_TIMEOUT,
                    )

                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                print(f"V3 AI 调用失败：{response.status_code} {response.text[:300]}")
            except Exception as exc:
                print(f"V3 AI 调用异常：{exc}")

            if attempt < settings.THIRD_LAYER_RETRIES - 1:
                time.sleep(delay)
                delay *= 2
        return None

    def _http_proxy(self) -> Optional[str]:
        return os.environ.get("https_proxy") or os.environ.get("http_proxy") or None

    def _extract_json(self, text: str) -> Optional[Any]:
        text = text.strip()
        for candidate in (text, self._extract_markdown_json(text), self._extract_bracket_json(text)):
            if not candidate:
                continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        return None

    def _extract_markdown_json(self, text: str) -> Optional[str]:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_bracket_json(self, text: str) -> Optional[str]:
        for opener, closer in (("{", "}"), ("[", "]")):
            start = text.find(opener)
            end = text.rfind(closer)
            if start != -1 and end != -1 and end > start:
                return text[start:end + 1]
        return None

    def _normalize_signal_interpretation(
        self,
        result: Dict[str, Any],
        fallback: Dict[str, Any],
    ) -> Dict[str, Any]:
        normalized = {
            "main_conclusion": result.get("main_conclusion") or fallback.get("main_conclusion", ""),
            "why_it_matters": result.get("why_it_matters") or fallback.get("why_it_matters", ""),
            "top_signals": [],
            "six_dimension_briefs": {},
        }

        signals = result.get("top_signals", [])
        fallback_signals = fallback.get("top_signals", [])
        for index in range(3):
            source = signals[index] if index < len(signals) and isinstance(signals[index], dict) else (
                fallback_signals[index] if index < len(fallback_signals) else {}
            )
            fallback_source = fallback_signals[index] if index < len(fallback_signals) else {}
            normalized["top_signals"].append({
                "id": source.get("id") or fallback_source.get("id", ""),
                "title": source.get("title") or fallback_source.get("title", "未命名信号"),
                "event": source.get("event") or fallback_source.get("event", ""),
                "signal": source.get("signal") or fallback_source.get("signal", ""),
                "for_me": source.get("for_me") or fallback_source.get("for_me", ""),
                "score": source.get("score") or fallback_source.get("score", 7),
                "supporting_news": self._normalize_news_refs(
                    source.get("supporting_news"),
                    fallback_source.get("supporting_news", []),
                ),
            })

        source_dimensions = result.get("six_dimension_briefs", {})
        fallback_dimensions = fallback.get("six_dimension_briefs", {})
        for key in self.DIMENSION_KEYS:
            item = source_dimensions.get(key, {}) if isinstance(source_dimensions, dict) else {}
            fallback_item = fallback_dimensions.get(key, self.DEFAULT_DIMENSION_VALUE)
            normalized["six_dimension_briefs"][key] = {
                "summary": item.get("summary") or fallback_item.get("summary", "今日无显著动态"),
                "brief": item.get("brief") or fallback_item.get("brief", "今日无显著动态"),
                "related_news": self._normalize_news_refs(
                    item.get("related_news"),
                    fallback_item.get("related_news", []),
                ),
            }
        return normalized

    def _normalize_deep_analysis(
        self,
        result: List[Dict[str, Any]],
        fallback: List[Dict[str, Any]],
        date_str: str,
    ) -> List[Dict[str, Any]]:
        normalized = []
        source = result[:3] if result else []
        if len(source) < 2:
            source = source + fallback[: 2 - len(source)]
        for index, item in enumerate(source[:3], start=1):
            fallback_item = fallback[index - 1] if index - 1 < len(fallback) else {}
            normalized.append({
                "id": fallback_item.get("id") or f"daily_trend_{date_str}_{index}",
                "trend_name": item.get("trend_name") or fallback_item.get("trend_name", f"趋势 {index}"),
                "summary": item.get("summary") or fallback_item.get("summary", ""),
                "related_signals": self._ensure_list(item.get("related_signals"))[:3],
                "repeated_patterns": self._prefer_list(item.get("repeated_patterns"), fallback_item.get("repeated_patterns", [])),
                "drivers": self._prefer_list(item.get("drivers"), fallback_item.get("drivers", [])),
                "mechanism": item.get("mechanism") or fallback_item.get("mechanism", ""),
                "short_term_impact": item.get("short_term_impact") or fallback_item.get("short_term_impact", ""),
                "long_term_impact": item.get("long_term_impact") or fallback_item.get("long_term_impact", ""),
                "impact_on_me": item.get("impact_on_me") or fallback_item.get("impact_on_me", ""),
                "risks": self._ensure_list(item.get("risks"))[:3],
                "opportunities": self._ensure_list(item.get("opportunities"))[:3],
                "watch_points": self._prefer_list(item.get("watch_points"), fallback_item.get("watch_points", [])),
                "supporting_news": self._normalize_news_refs(
                    item.get("supporting_news"),
                    fallback_item.get("supporting_news", []),
                ),
            })
        return normalized

    def _normalize_action_suggestions(
        self,
        result: Dict[str, Any],
        fallback: Dict[str, Any],
        date_str: str,
    ) -> Dict[str, Any]:
        normalized = {}
        for scope, effort in (("today", "low"), ("this_week", "medium"), ("this_month", "high")):
            source_items = self._ensure_dict_list(result.get(scope))
            fallback_items = fallback.get(scope, [])
            if len(source_items) < 2:
                source_items.extend(fallback_items[: 2 - len(source_items)])
            normalized[scope] = []
            for index, item in enumerate(source_items[:3], start=1):
                fallback_item = fallback_items[index - 1] if index - 1 < len(fallback_items) else {}
                normalized[scope].append({
                    "id": fallback_item.get("id") or f"action_{date_str}_{scope}_{index}",
                    "target": item.get("target") or fallback_item.get("target", "重点方向"),
                    "action": item.get("action") or fallback_item.get("action", "继续跟踪"),
                    "purpose": item.get("purpose") or fallback_item.get("purpose", "形成更稳定的判断。"),
                    "effort": item.get("effort") if item.get("effort") in ("low", "medium", "high") else (
                        fallback_item.get("effort", effort)
                    ),
                    "source_reference": fallback_item.get("source_reference", ""),
                })
        return normalized

    def _build_internal_candidates(self, deep_analysis: List[Dict[str, Any]], date_str: str) -> Dict[str, Any]:
        return self.daily_builder.build_internal_candidates(deep_analysis, date_str)

    def _compact_news_for_prompt(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        compact = []
        for item in news_items[:20]:
            compact.append({
                "news_id": item.get("id"),
                "title": item.get("title"),
                "source": item.get("source"),
                "url": item.get("url"),
                "content": item.get("content", "")[:280],
                "theme_tags": item.get("theme_tags", []),
                "final_score": item.get("final_score"),
                "signal_level": item.get("signal_level"),
            })
        return compact

    def _normalize_news_refs(self, value: Any, fallback: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        refs = self._ensure_dict_list(value)
        if not refs:
            refs = fallback
        normalized = []
        for item in refs[:3]:
            normalized.append({
                "news_id": item.get("news_id", ""),
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
            })
        return normalized

    def _ensure_list(self, value: Any) -> List[Any]:
        return value if isinstance(value, list) else []

    def _ensure_dict_list(self, value: Any) -> List[Dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)]

    def _prefer_list(self, value: Any, fallback: List[Any]) -> List[Any]:
        items = self._ensure_list(value)
        return items if items else fallback
