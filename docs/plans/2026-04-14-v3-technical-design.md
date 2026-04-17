# Trend Radar V3 Technical Design

**创建日期**: 2026-04-14
**更新日期**: 2026-04-14
**版本**: V3.1
**状态**: 当前基线

---

## 1. 系统边界

当前系统只保留 daily：

```text
NewsFetcher
-> NewsProcessor
-> DailyReportService
-> PushManager
```

---

## 2. 模块职责

### `news_fetcher.py`

负责抓取原始新闻并保存到 `raw_news`。

### `news_processor.py`

负责：

1. 去重
2. 清洗
3. AI 评分
4. 输出 `filter_news`

不再负责：

1. 信息源分类
2. 规则评分
3. 资产候选升级逻辑

### `daily_report_service.py`

负责日报生成策略：

1. 优先走 `AIAnalyzerV3`
2. AI 失败时回退 `DailyReportBuilder`

### `ai_analyzer_v3.py`

负责调用模型，生成：

1. `signal_interpretation`
2. `deep_analysis`
3. `action_suggestions`
4. `internal_candidates`

### `push_manager.py`

负责 daily 邮件发送。

### `workflow_runner.py`

只编排 daily 流程。

---

## 3. 评分设计

评分采用 AI-only：

1. importance
2. relevance_to_me
3. signal_strength
4. actionability

综合分 `final_score` 由以上维度加权得到。

当前没有：

1. source_category
2. rule_score
3. rule + AI 混合

---

## 4. DailyReportBuilder 的定位

`DailyReportBuilder` 不再代表“规则系统”。

它现在承担的是：

1. schema fallback
2. 当 AI 调用失败时，生成最低可用的日报结构

---

## 5. internal_candidates 的定位

`internal_candidates` 只做日报内部保留：

1. `trend_candidates`
2. `opportunity_candidates`

它不再参与：

1. 周聚合
2. 月聚合
3. 资产沉淀

---

## 6. 当前技术原则

1. 主链路优先，扩展层后置
2. 用 AI 减少规则维护成本
3. 所有 JSON 输出都尽量严格和稳定
4. 让每个模块单独可测试
