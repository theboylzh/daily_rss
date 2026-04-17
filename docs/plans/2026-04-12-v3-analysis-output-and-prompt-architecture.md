# Trend Radar V3 Analysis Output And Prompt Architecture

**创建日期**: 2026-04-12
**更新日期**: 2026-04-15
**版本**: V3.5
**状态**: 当前基线

---

## 1. 架构目标

V3 现在只保留一条分析链：

```text
raw_news
-> filter_news
-> daily report
-> email
```

---

## 2. filter_news 的职责

`filter_news` 不是最终报告。

它的作用是把原始新闻转换成更适合 AI 分析的结构化输入。

当前包括：

1. 去重
2. 内容清洗
3. AI 评分
4. AI / fallback 主题标签

当前不包括：

1. 信息源分类
2. 规则评分
3. weekly / monthly 输入适配

---

## 3. filter_news 建议字段

每条新闻建议至少包含：

```json
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
  "score_reason": "模型能力变化已明显影响工作流。"
}
```

---

## 4. daily report 输出

daily report 输出结构如下：

```json
{
  “meta”: {},
  “signal_interpretation”: {},
  “deep_analysis”: [],
  “action_suggestions”: {},
  “internal_candidates”: {}
}
```

### `signal_interpretation`

回答：

1. 今天最重要的结论是什么
2. 为什么重要
3. 哪些是 top events（基于用户身份和目标筛选的 3 个最重要事件）

字段说明：
- `main_conclusion`: 今日最重要结论（1 句话）
- `why_it_matters`: 为什么重要（1-2 段）
- `top_events`: 3 个事件，每个包含 title（标题）、description（5W1H 描述）、so_what（对用户的具体影响）
- `six_dimension_briefs`: 6 个维度的一句判断，直接是字符串

### `deep_analysis`

输出 3-5 条趋势观察（trend_observation）。

每条包含 5 个字段：
- `title`: 趋势观察标题
- `evidence`: 观察到的现象/事件 + 这是单点事件还是模式雏形
- `news_ids`: 支撑新闻 ID 列表
- `reasoning`: 机制解释 + 适用条件 + 反证风险 + 验证路径（一大段，不分拆）
- `so_what_for_me`: 对用户的决策影响/行动建议

**逻辑链**：证据 → 机制 → 条件 → 反证 → 验证 → 行动

**重要**：
1. 3-5 条必须覆盖不同主题（模型/产品/技术/商业/政策）
2. reasoning 必须包含传导机制，不能只说”值得关注”
3. so_what_for_me 必须是具体行动，不能是”继续关注”

### `action_suggestions`

回答：

1. 今天可以做什么
2. 这周可以做什么
3. 这个月可以做什么

### `internal_candidates`

只作为日报内保留字段，用于记录：

1. `trend_candidates`
2. `opportunity_candidates`

它不再承担”流向下一层系统”的职责。

---

## 5. Prompt 设计原则

### 原则 1

Prompt 直接围绕 daily 产出，不再预埋 weekly / monthly / assets 逻辑。

### 原则 2

Prompt 要求 AI 对用户价值负责，不只是总结事实。

### 原则 3

Prompt 输出必须是严格 JSON，避免下游适配复杂化。

### 原则 4

Prompt 对 `supporting_news` 的引用必须来自输入新闻，禁止编造。

---

## 6. 评分 Prompt 目标

评分 Prompt 只做一件事：

**判断哪些新闻值得进入日报分析主视野。**

评分维度：

1. importance
2. relevance_to_me
3. signal_strength
4. actionability

---

## 7. 当前结论

V3 不再追求“完整情报系统架构”。

当前只追求：

1. daily 主链路足够稳定
2. AI 评分有效
3. daily 报告可用
