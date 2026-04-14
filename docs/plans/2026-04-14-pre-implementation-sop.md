# Trend Radar V3 Pre-Implementation SOP

**更新日期**: 2026-04-14
**版本**: V3.1

---

## 1. 当前执行范围

只执行下面这条链路：

```text
抓取 -> filter_news -> daily report -> 发送
```

---

## 2. 开发前确认项

1. 不做 weekly
2. 不做 monthly
3. 不做 assets
4. 不做信息源分类
5. 不做规则评分

---

## 3. 开发顺序

1. 先保证 `raw_news` 保存稳定
2. 再保证 `filter_news` 的 AI 评分输出稳定
3. 再保证 `daily report` schema 稳定
4. 最后再优化 prompt 和邮件模板

---

## 4. 验收顺序

1. 能抓到新闻
2. 能生成 `data/news/filter_news/*.json`
3. 能生成 `data/report/daily/*.json`
4. 能发送 daily 邮件

---

## 5. 注意事项

1. 如果 AI 评分失败，要有 fallback，不能导致主链路直接中断
2. 所有复杂性优先放进 AI 输出，不优先堆规则
3. 文档、代码、schema 必须同步
