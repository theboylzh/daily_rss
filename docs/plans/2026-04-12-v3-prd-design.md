# Trend Radar V3 PRD

**创建日期**: 2026-04-12
**更新日期**: 2026-04-14
**版本**: V3.1
**状态**: 当前基线

---

## 1. 产品定位

Trend Radar 只做一件事：

**把每天抓到的 AI / 科技新闻，转换成对用户有判断价值和行动价值的 daily intelligence report。**

它不是知识库，不是资产池，也不是周报/月报系统。

当前版本只服务 daily 场景。

---

## 2. 当前目标

当前 V3 的目标收敛为：

1. 抓取每日新闻
2. 去重和清洗
3. 用 AI 对新闻做评分
4. 用 AI 生成 daily report
5. 通过邮件发送 daily report

不做：

1. weekly
2. monthly
3. 长期资产层
4. 信息源分类体系
5. 规则评分体系

---

## 3. 用户价值

用户需要的不是“看更多新闻”，而是：

1. 快速知道今天最值得注意的变化
2. 理解这些变化为什么重要
3. 判断这些变化对自己意味着什么
4. 获得少量但有用的后续动作

---

## 4. 产品输入输出

### 输入

- RSS / Atom 抓取到的原始新闻

### 输出

- `filter_news`
- `daily report`
- daily 邮件

---

## 5. 数据层范围

当前只保留下面这些目录：

```text
data/
  news/
    raw_news/
    filter_news/
  report/
    daily/
```

说明：

- `raw_news`：原始抓取结果
- `filter_news`：去重、清洗、AI 评分后的新闻
- `report/daily`：最终日报 JSON

---

## 6. daily report 结构

当前日报保留四个一级字段：

1. `meta`
2. `signal_interpretation`
3. `deep_analysis`
4. `action_suggestions`
5. `internal_candidates`

其中：

- `signal_interpretation` 是当天最重要结论和关键变化
- `deep_analysis` 是 2-3 条更高层的趋势解释
- `action_suggestions` 是 today / this_week / this_month 的行动建议
- `internal_candidates` 只作为日报内部保留字段，不再喂给 weekly / monthly / assets

---

## 7. 评分原则

评分完全由 AI 主导。

当前不再使用：

- 信息源分类加权
- 规则评分
- 规则评分 + AI 评分混合

AI 评分需要回答四个问题：

1. 这条新闻本身重不重要
2. 对用户有没有相关性
3. 是否代表更大的变化
4. 是否能引出后续判断或动作

---

## 8. 非目标

以下内容明确不在本轮范围：

1. 趋势池 / 机会池
2. 周报和月报的聚合分析
3. 设计稿和界面系统
4. 打印版式
5. 复杂的运营后台

---

## 9. 当前产品原则

1. 只做 daily 主链路
2. 尽量把复杂性留给 AI，不把复杂性写成规则
3. 减少人为维护成本
4. 让代码结构能快速调整 prompt 和 schema
