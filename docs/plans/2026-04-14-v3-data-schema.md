# Trend Radar V3 Data Schema

**创建日期**: 2026-04-14
**更新日期**: 2026-04-14
**版本**: V3.1
**状态**: 当前基线

---

## 1. 目录结构

```text
data/
  news/
    raw_news/
    filter_news/
  report/
    daily/
```

---

## 2. raw_news schema

```json
{
  "date": "2026-04-14",
  "news": [
    {
      "id": "news_xxx",
      "title": "标题",
      "url": "https://...",
      "content": "正文",
      "source": "来源",
      "published_at": "2026-04-14T08:00:00",
      "collected_at": "2026-04-14T08:30:00"
    }
  ]
}
```

---

## 3. filter_news schema

```json
{
  "date": "2026-04-14",
  "news": [
    {
      "id": "news_xxx",
      "title": "标题",
      "url": "https://...",
      "content": "正文摘要",
      "source": "来源",
      "published_at": "2026-04-14T08:00:00",
      "collected_at": "2026-04-14T08:30:00",
      "theme_tags": ["workflow", "ai_product"],
      "ai_scores": {
        "importance": 8,
        "relevance_to_me": 9,
        "signal_strength": 8,
        "actionability": 7
      },
      "final_score": 8.1,
      "signal_level": "S",
      "score_reason": "一句简短评分理由"
    }
  ]
}
```

说明：

1. 不再有 `source_category`
2. 不再有 `rule_score`
3. 不再有 `weekly/monthly/assets` 相关字段

---

## 4. daily report schema

```json
{
  "meta": {
    "report_type": "daily",
    "date": "2026-04-14",
    "news_count": 42,
    "filtered_count": 16
  },
  "signal_interpretation": {
    "main_conclusion": "今日最重要结论",
    "why_it_matters": "为什么重要",
    "top_signals": [
      {
        "id": "signal_2026-04-14_1",
        "title": "信号标题",
        "event": "发生了什么",
        "signal": "说明了什么变化",
        "for_me": "对我意味着什么",
        "score": 8.8,
        "supporting_news": []
      }
    ],
    "six_dimension_briefs": {
      "model_and_capability": {"summary": "", "brief": "", "related_news": []},
      "ai_product_and_interaction": {"summary": "", "brief": "", "related_news": []},
      "design_and_experience": {"summary": "", "brief": "", "related_news": []},
      "technology_and_platform": {"summary": "", "brief": "", "related_news": []},
      "business_and_monetization": {"summary": "", "brief": "", "related_news": []},
      "policy_and_ethics": {"summary": "", "brief": "", "related_news": []}
    }
  },
  "deep_analysis": [
    {
      "id": "daily_trend_2026-04-14_1",
      "trend_name": "趋势名称",
      "summary": "趋势概述",
      "related_signals": [],
      "repeated_patterns": [],
      "drivers": [],
      "mechanism": "",
      "short_term_impact": "",
      "long_term_impact": "",
      "impact_on_me": "",
      "risks": [],
      "opportunities": [],
      "watch_points": [],
      "supporting_news": []
    }
  ],
  "action_suggestions": {
    "today": [],
    "this_week": [],
    "this_month": []
  },
  "internal_candidates": {
    "trend_candidates": [],
    "opportunity_candidates": []
  }
}
```

---

## 5. internal_candidates schema

```json
{
  "trend_candidates": [
    {
      "id": "daily_trend_2026-04-14_1",
      "name": "工作流自动化深化",
      "summary": "趋势概述",
      "why_keep": "为什么值得保留"
    }
  ],
  "opportunity_candidates": [
    {
      "id": "daily_opp_2026-04-14_1",
      "name": "工作流自动化深化 对应的小机会",
      "type": "product",
      "summary": "机会摘要",
      "validation_idea": "如何验证"
    }
  ]
}
```

说明：

`internal_candidates` 只用于 daily 内部记录，不再作为下游聚合系统输入。
