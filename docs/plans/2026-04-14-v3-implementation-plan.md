# Trend Radar V3 Implementation Plan

**创建日期**: 2026-04-14
**更新日期**: 2026-04-14
**版本**: V3.1
**状态**: 当前执行计划

---

## 1. 目标

重新开始，只做一个最小可用版本：

**daily-only AI intelligence pipeline**

---

## 2. 范围

### 在范围内

1. RSS 抓取
2. `raw_news` 保存
3. `filter_news` AI 评分
4. `daily report` AI 分析
5. daily 邮件发送

### 不在范围内

1. weekly
2. monthly
3. assets
4. 信息源分类
5. 规则评分
6. 界面设计

---

## 3. 实现步骤

### 步骤 1

清理旧范围代码：

- 删 weekly / monthly / assets builder
- 删 CLI 入口
- 删 workflow 中的分支逻辑

### 步骤 2

重建 `filter_news`：

- 保留去重和清洗
- 改成 AI 评分
- 只保留对 daily 有用的字段

### 步骤 3

收敛 `daily report` schema：

- 保留 `signal_interpretation`
- 保留 `deep_analysis`
- 保留 `action_suggestions`
- 保留 `internal_candidates`

### 步骤 4

验证 daily 主链路：

- `python main.py daily`
- `python main.py send-v3-daily`

### 步骤 5

最后再调 prompt 和邮件模板。

---

## 4. 验收标准

1. daily 可以独立跑通
2. 生成的 `filter_news` 可读且字段稳定
3. 生成的 `daily report` 满足 schema
4. 没有 weekly / monthly / assets 入口残留在主链路
