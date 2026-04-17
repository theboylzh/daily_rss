# Trend Radar V3 Data Schema

**创建日期**: 2026-04-14
**更新日期**: 2026-04-15
**版本**: V3.5
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
    "top_events": [
      {
        "title": "事件标题",
        "description": "5W1H 描述事件关键（何时/发生了什么/谁/为什么/如何）",
        "so_what": "对用户的具体影响或行动建议"
      }
    ],
    "six_dimension_briefs": {
      "model_and_capability": "一句判断",
      "ai_product_and_interaction": "一句判断",
      "design_and_experience": "一句判断",
      "technology_and_platform": "一句判断",
      "business_and_monetization": "一句判断",
      "policy_and_ethics": "一句判断"
    }
  },
  "deep_analysis": [
    {
      "type": "trend_observation",
      "id": "obs_2026-04-14_1",
      "title": "趋势观察标题",
      "evidence": "观察到的现象/事件 + 这是单点事件还是模式雏形",
      "news_ids": ["news_xxx", "news_yyy"],
      "reasoning": "机制解释（变化如何传导）+ 适用条件 + 反证风险（什么情况下判断不成立）+ 验证路径（何时观察什么信号）",
      "so_what_for_me": "对用户的决策影响/行动建议"
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
