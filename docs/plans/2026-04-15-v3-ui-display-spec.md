# Trend Radar V3 UI Display Specification

创建日期：2026-04-15
更新日期：2026-04-15
版本：V3.5

---

## 设计原则

1. 一个模块只展示一个核心信息
2. 不折叠任何信息，全部平铺展示
3. 内部字段不上 UI（id、purpose、effort 等）
4. 本文件是 UI 设计的唯一数据源

---

## 模块 0: Header

- 小标题：每日情报
- 大标题：TREND RADAR
- 描述：为 Builder 生成的 AI 情报日报
- 日期：meta.date，格式 "2026-04-14 星期一"
- 新闻数量：meta.filtered_count，格式 "18 条新闻"

---

## 模块 1: Key Insight

- 主结论：signal_interpretation.main_conclusion（1 句话）
- 为什么重要：signal_interpretation.why_it_matters（1-2 段，单独区域显示）

---

## 模块 2: Top Events

3 个事件卡片，每条包含：

- 序号：01, 02, 03
- 事件标题：top_events[].title
- 事件描述：top_events[].description（5W1H，2-3 行）
- 对我意味着什么：top_events[].so_what（单独一行，带箭头）

---

## 模块 3: Six Dimensions Brief

6 行维度简报，每行包含：

- 图标：固定 emoji（见下方映射）
- 维度名：固定名称
- 一句判断：six_dimension_briefs[key]（直接是字符串）

维度映射：
- model_and_capability → 🧠 Models
- ai_product_and_interaction → 💬 AI Products
- design_and_experience → 🎨 Design
- technology_and_platform → ⚙️ Platform
- business_and_monetization → 💼 Business
- policy_and_ethics → 📜 Policy

---

## 模块 4: Deep Analysis

3-5 个趋势观察卡片，每条包含：

- 序号：01, 02, 03...
- 标题：deep_analysis[].title
- 证据：deep_analysis[].evidence（现象/事件 + 单点还是模式）
- 推理：deep_analysis[].reasoning（机制 + 条件 + 反证 + 验证，一大段）
- 对我的影响：deep_analysis[].so_what_for_me（单独一行，带箭头）
- 支撑新闻：deep_analysis[].news_ids[]（每条显示 title + source，最多 5 条）

---

## 模块 5: Action Suggestions

3 列行动建议：

- Today：action_suggestions.today[]（2-3 条，显示 action）
- This Week：action_suggestions.this_week[]（2-3 条，显示 action）
- This Month：action_suggestions.this_month[]（2-3 条，显示 action）

---

## 模块 6: Internal Candidates

完全不展示。

---

## 字段来源总览

meta → Header
- date, filtered_count

signal_interpretation → Key Insight + Top Events + Six Dimensions
- main_conclusion, why_it_matters
- top_events[]: title, description, so_what
- six_dimension_briefs{}: [key] 直接是字符串

deep_analysis[] → Deep Analysis
- trend_observation 类型：title, evidence, news_ids, reasoning, so_what_for_me

action_suggestions{} → Action Suggestions
- today[], this_week[], this_month[]: [].action
