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

    DEFAULT_DIMENSION_VALUE = "今日无显著动态"

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
任务：基于给定的 filter_news，为 Trend Radar 生成"信号解读"模块。

输出要求：
1. 只能输出 JSON，不要 Markdown，不要解释。
2. 必须严格包含以下字段：
{{
  "main_conclusion": "今日最重要的结论",
  "why_it_matters": "为什么重要",
  "top_events": [
    {{
      "title": "事件标题",
      "description": "5W1H 描述事件关键",
      "so_what": "对用户的具体影响或行动建议"
    }}
  ],
  "six_dimension_briefs": {{
    "model_and_capability": "一句话事实简报",
    "ai_product_and_interaction": "一句话事实简报",
    "design_and_experience": "一句话事实简报",
    "technology_and_platform": "一句话事实简报",
    "business_and_monetization": "一句话事实简报",
    "policy_and_ethics": "一句话事实简报"
  }}
}}

硬性要求：
1. top_events 固定 3 条，基于用户身份和目标筛选。
2. top_events 的 title 必须使用新闻原标题风格，只陈述事实，不要出现"重塑"、"范式"、"演进"、"趋势"等总结性词汇。
3. top_events 的 description 用 5W1H 讲述事件关键（何时/谁/发生了什么/为什么/如何），不要出现"模式"、"趋势"、"范式"等词。
4. top_events 的 so_what 必须具体，不能是"值得关注"等空话。
5. six_dimension_briefs 每个维度用一句话组合该维度下的 2-3 个事实，例如"事实 A，事实 B，事实 C"。不要做趋势判断（如"正从...转向..."）。
6. six_dimension_briefs 某维度无内容时写"今日无显著动态"。

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
任务：基于信号解读和 filter_news，生成"深度分析"模块。
本模块输出 3-5 条趋势观察（trend_observation）。

输出要求：
1. 只能输出 JSON 数组，不要 Markdown。
2. 固定输出 3 到 5 条 trend_observation。
3. 每条必须包含以下字段：

[
  {{
    "type": "trend_observation",
    "id": "obs_2026-04-15_1",
    "title": "趋势观察标题",
    "evidence": "观察到的现象/事件 + 这是单点事件还是模式雏形",
    "news_ids": ["news_xxx", "news_yyy"],
    "reasoning": "传导机制解释 + 适用条件 + 反证风险 + 验证路径",
    "so_what_for_me": "对用户的决策影响/行动建议"
  }}
]

硬性要求：
1. 3-5 条必须覆盖不同主题（模型/产品/技术/商业/政策），避免重复。
2. evidence 必须说明是"单点事件"还是"模式雏形"。
3. reasoning 必须用一大段话解释传导机制（变化如何通过产品/能力/市场反馈联动），并说明适用条件、反证风险（什么情况下这个判断不成立）和验证路径（未来何时观察什么信号）。不要只说"值得关注"，要解释具体如何传导。
4. so_what_for_me 必须是具体行动，不能是"继续关注"。
5. news_ids 只能引用输入新闻的 id。

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
            "top_events": [],
            "six_dimension_briefs": {},
        }

        # Normalize top_events
        events = result.get("top_events", [])
        fallback_events = fallback.get("top_events", [])
        for index in range(3):
            source = events[index] if index < len(events) and isinstance(events[index], dict) else (
                fallback_events[index] if index < len(fallback_events) else {}
            )
            fallback_source = fallback_events[index] if index < len(fallback_events) else {}
            normalized["top_events"].append({
                "title": source.get("title") or fallback_source.get("title", "未命名事件"),
                "description": source.get("description") or fallback_source.get("description", ""),
                "so_what": source.get("so_what") or fallback_source.get("so_what", ""),
            })

        # Normalize six_dimension_briefs
        source_dimensions = result.get("six_dimension_briefs", {})
        fallback_dimensions = fallback.get("six_dimension_briefs", {})
        for key in self.DIMENSION_KEYS:
            item = source_dimensions.get(key, "") if isinstance(source_dimensions, dict) else ""
            fallback_item = fallback_dimensions.get(key, self.DEFAULT_DIMENSION_VALUE)
            normalized["six_dimension_briefs"][key] = item or fallback_item
        return normalized

    def _normalize_deep_analysis(
        self,
        result: List[Dict[str, Any]],
        fallback: List[Dict[str, Any]],
        date_str: str,
    ) -> List[Dict[str, Any]]:
        """Normalize deep_analysis: 3-5 trend observations."""
        normalized = []
        source = result[:5] if result else []
        # 确保至少 3 条
        while len(source) < 3 and len(fallback) > 0:
            source.append(fallback[len(source)] if len(source) < len(fallback) else {})

        for index, item in enumerate(source[:5], start=1):
            fallback_item = fallback[index - 1] if index - 1 < len(fallback) else {}
            news_ids = item.get("news_ids") or fallback_item.get("news_ids", [])
            normalized.append({
                "type": "trend_observation",
                "id": fallback_item.get("id") or f"obs_{date_str}_{index}",
                "title": item.get("title") or fallback_item.get("title", f"趋势观察 {index}"),
                "evidence": item.get("evidence") or fallback_item.get("evidence", ""),
                "news_ids": news_ids if isinstance(news_ids, list) else [],
                "reasoning": item.get("reasoning") or fallback_item.get("reasoning", ""),
                "so_what_for_me": item.get("so_what_for_me") or fallback_item.get("so_what_for_me", ""),
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
