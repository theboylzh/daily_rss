import hashlib
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import httpx

from config import settings
from storage_manager import StorageManager


class NewsProcessor:
    """将 raw_news 处理为 AI 评分驱动的 filter_news。"""

    TRACKING_QUERY_PREFIXES = (
        "utm_",
        "spm",
        "from",
        "source",
        "ref",
        "track",
    )

    THEME_KEYWORDS = {
        "ai_model": ("模型", "llm", "gpt", "多模态", "推理模型", "foundation model"),
        "ai_product": ("产品", "agent", "助手", "copilot", "应用", "工作流"),
        "workflow": ("workflow", "自动化", "效率", "协作", "办公"),
        "design": ("设计", "交互", "ui", "ux", "体验"),
        "coding": ("编程", "代码", "开发", "codex", "cursor", "工程"),
        "business": ("融资", "营收", "商业", "市场", "客户", "增长"),
        "policy": ("监管", "政策", "合规", "安全", "版权"),
        "research": ("研究", "论文", "benchmark", "评测", "数据集"),
    }

    HIGH_SIGNAL_KEYWORDS = (
        "发布", "推出", "上线", "开源", "融资", "收购", "模型", "agent", "ai", "芯片",
        "平台", "政策", "监管", "增长", "合作", "研究", "论文", "benchmark"
    )

    def __init__(self):
        self.storage = StorageManager()

    def process_news(self, raw_news: List[Dict[str, Any]], date_str: Optional[str] = None) -> Dict[str, Any]:
        deduplicated = self._deduplicate(raw_news)
        ai_scores = self._score_news_with_ai(deduplicated)
        processed_news = []
        for index, item in enumerate(deduplicated):
            processed_item = self._build_filter_item(item, ai_scores.get(index))
            if processed_item["final_score"] >= settings.AI_SCORE_THRESHOLD:
                processed_news.append(processed_item)

        processed_news.sort(key=lambda item: item["final_score"], reverse=True)

        payload = {
            "date": date_str or datetime.now().strftime("%Y-%m-%d"),
            "news": processed_news,
        }
        self.storage.write_json(self.storage.get_filter_news_path(payload["date"]), payload)
        return payload

    def _deduplicate(self, raw_news: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_keys = set()
        result = []
        for item in raw_news:
            normalized_url = self._normalize_url(item.get("url", ""))
            dedupe_key = f"{normalized_url}|{self._normalize_text(item.get('title', ''))}"
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)
            result.append(item)
        return result

    def _build_filter_item(self, item: Dict[str, Any], ai_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        normalized_url = self._normalize_url(item.get("url", ""))
        theme_tags = self._normalize_theme_tags(ai_result.get("theme_tags")) if ai_result else self._infer_theme_tags(item)
        ai_scores = self._normalize_ai_scores(ai_result, item, theme_tags)
        final_score = round(
            ai_scores["importance"] * 0.35
            + ai_scores["relevance_to_me"] * 0.3
            + ai_scores["signal_strength"] * 0.2
            + ai_scores["actionability"] * 0.15,
            2,
        )

        return {
            "id": item.get("id") or self._generate_news_id(normalized_url, item),
            "title": item.get("title", "").strip(),
            "url": item.get("url", "").strip(),
            "content": self._clean_content(item.get("content", "")),
            "source": item.get("source", "").strip(),
            "published_at": item.get("published_at"),
            "collected_at": item.get("collected_at"),
            "theme_tags": theme_tags,
            "ai_scores": ai_scores,
            "final_score": final_score,
            "signal_level": self._map_signal_level(final_score),
            "score_reason": (ai_result or {}).get("reason", ""),
        }

    def _infer_theme_tags(self, item: Dict[str, Any]) -> List[str]:
        haystack = " ".join(
            [item.get("title", "").lower(), item.get("content", "").lower(), item.get("source", "").lower()]
        )
        tags = [tag for tag, keywords in self.THEME_KEYWORDS.items() if any(keyword in haystack for keyword in keywords)]
        if not tags:
            tags = ["general_ai"]
        return tags[:3]

    def _normalize_ai_scores(
        self,
        ai_result: Optional[Dict[str, Any]],
        item: Dict[str, Any],
        theme_tags: List[str],
    ) -> Dict[str, int]:
        if ai_result:
            return {
                "importance": self._clamp_score(ai_result.get("importance")),
                "relevance_to_me": self._clamp_score(ai_result.get("relevance_to_me")),
                "signal_strength": self._clamp_score(ai_result.get("signal_strength")),
                "actionability": self._clamp_score(ai_result.get("actionability")),
            }

        fallback_score = self._heuristic_score(item, theme_tags)
        return {
            "importance": fallback_score,
            "relevance_to_me": min(10, fallback_score + (1 if "workflow" in theme_tags or "design" in theme_tags else 0)),
            "signal_strength": fallback_score,
            "actionability": min(10, fallback_score + (1 if any(tag in theme_tags for tag in ("workflow", "coding", "design")) else 0)),
        }

    def _score_news_with_ai(self, news_items: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        if not news_items or not settings.AI_API_KEY:
            return {}

        prompt_items = []
        for index, item in enumerate(news_items[:30]):
            prompt_items.append({
                "index": index,
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "content": self._clean_content(item.get("content", ""))[:600],
                "published_at": item.get("published_at"),
            })

        prompt = f"""
任务：你是 Trend Radar 的新闻预处理器。请对输入新闻做 AI 评分，只输出 JSON。

目标用户：
- 关注 AI、产品、设计、技术与商业变化
- 需要帮助判断哪些信息值得进入 daily intelligence report

评分要求：
- importance: 新闻本身的重要性，1-10
- relevance_to_me: 对用户成长和行动价值的相关性，1-10
- signal_strength: 这条新闻是否代表更大变化，而不是孤立噪音，1-10
- actionability: 是否能引出后续判断、实验或跟踪动作，1-10
- theme_tags: 只能从以下标签中选择 1-3 个：
  ["ai_model","ai_product","workflow","design","coding","business","policy","research","general_ai"]

输出格式：
{{
  "items": [
    {{
      "index": 0,
      "importance": 8,
      "relevance_to_me": 9,
      "signal_strength": 8,
      "actionability": 7,
      "theme_tags": ["workflow", "ai_product"],
      "reason": "一句非常简短的评分理由"
    }}
  ]
}}

输入新闻：
{json.dumps(prompt_items, ensure_ascii=False, indent=2)}
"""
        result = self._call_ai_json(prompt)
        if not isinstance(result, dict):
            return {}

        score_map: Dict[int, Dict[str, Any]] = {}
        for item in result.get("items", []):
            if not isinstance(item, dict):
                continue
            index = item.get("index")
            if isinstance(index, int) and 0 <= index < len(news_items):
                score_map[index] = item
        return score_map

    def _call_ai_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        delay = settings.THIRD_LAYER_RETRY_DELAY
        for attempt in range(settings.THIRD_LAYER_RETRIES):
            try:
                with httpx.Client(
                    proxy=self._http_proxy(),
                    trust_env=False,
                ) as client:
                    response = client.post(
                        settings.AI_API_URL,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {settings.AI_API_KEY}",
                        },
                        json={
                            "model": settings.AI_MODEL,
                            "messages": [
                                {"role": "system", "content": "你是一个严格输出 JSON 的新闻评分助手。"},
                                {"role": "user", "content": prompt},
                            ],
                            "stream": False,
                            "max_tokens": 4096,
                        },
                        timeout=settings.THIRD_LAYER_TIMEOUT,
                    )
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"].strip()
                    parsed = self._extract_json(content)
                    if parsed is not None:
                        return parsed
            except Exception:
                pass

            if attempt < settings.THIRD_LAYER_RETRIES - 1:
                time.sleep(delay)
                delay *= 2
        return None

    def _http_proxy(self) -> Optional[str]:
        return os.environ.get("https_proxy") or os.environ.get("http_proxy") or None

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        text = text.strip()
        candidates = [text]
        if "```" in text:
            start = text.find("```")
            end = text.rfind("```")
            if end > start:
                snippet = text[start + 3:end].strip()
                if snippet.startswith("json"):
                    snippet = snippet[4:].strip()
                candidates.append(snippet)
        left = text.find("{")
        right = text.rfind("}")
        if left != -1 and right > left:
            candidates.append(text[left:right + 1])

        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue
        return None

    def _normalize_theme_tags(self, tags: Any) -> List[str]:
        if not isinstance(tags, list):
            return ["general_ai"]
        cleaned = [tag for tag in tags if tag in self.THEME_KEYWORDS or tag == "general_ai"]
        return cleaned[:3] or ["general_ai"]

    def _heuristic_score(self, item: Dict[str, Any], theme_tags: List[str]) -> int:
        haystack = f"{item.get('title', '')} {item.get('content', '')}".lower()
        score = 4
        if len(item.get("content", "")) >= 120:
            score += 1
        if any(keyword in haystack for keyword in self.HIGH_SIGNAL_KEYWORDS):
            score += 2
        if any(tag in theme_tags for tag in ("ai_model", "ai_product", "workflow", "coding", "design")):
            score += 1
        return self._clamp_score(score)

    def _map_signal_level(self, final_score: float) -> str:
        if final_score >= 8:
            return "S"
        if final_score >= 6:
            return "A"
        return "B"

    def _clean_content(self, content: str) -> str:
        return " ".join(content.split())

    def _normalize_url(self, url: str) -> str:
        if not url:
            return ""
        parsed = urlparse(url.strip().lower())
        filtered_query = [
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if not key.startswith(self.TRACKING_QUERY_PREFIXES)
        ]
        normalized_path = parsed.path.rstrip("/")
        return urlunparse((parsed.scheme, parsed.netloc, normalized_path, "", urlencode(filtered_query), ""))

    def _normalize_text(self, text: str) -> str:
        return " ".join(text.strip().lower().split())

    def _generate_news_id(self, normalized_url: str, item: Dict[str, Any]) -> str:
        if normalized_url:
            seed = normalized_url
        else:
            seed = "|".join(
                [
                    self._normalize_text(item.get("title", "")),
                    self._normalize_text(item.get("source", "")),
                    str(item.get("published_at", "")),
                ]
            )
        return f"news_{hashlib.md5(seed.encode('utf-8')).hexdigest()}"

    def _clamp_score(self, score: Any) -> int:
        try:
            return max(1, min(int(round(float(score))), 10))
        except (TypeError, ValueError):
            return 5
