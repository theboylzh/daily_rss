# Signal Interpretation Schema Update

**创建日期**: 2026-04-16
**版本**: V3.6
**状态**: 待实施

---

## 1. 修改目标

解决当前实现中"信号"与"趋势"边界不清的问题，避免内容重复感，让用户价值分层更清晰。

---

## 2. top_events 修改

### 当前问题

`top_events` 的 title 使用趋势性总结（如"Chrome 推出 Skills 功能，Agent 重塑上网方式"），与 `deep_analysis` 的 trend_observation 标题风格重叠。

### 修改方案

| 字段 | 当前 | 修改后 |
|------|------|--------|
| `title` | 趋势性总结 | 新闻原标题，信息密度高 |
| `description` | 5W1H + 趋势判断 | 5W1H 描述事实，不出现"模式/趋势/范式"等词 |
| `so_what` | 行动建议 | 保持不变 |

### 示例

**修改前**：
```json
{
  "title": "Chrome 推出 Skills 功能，Agent 重塑上网方式",
  "description": "2026 年 4 月 14 日，Google 为 Chrome 浏览器添加了 Skills 功能。这是浏览器从'展示窗口'向'AI 代理'范式转变的关键一步。",
  "so_what": "产品经理和开发者应关注并学习使用此类 AI 原生交互功能..."
}
```

**修改后**：
```json
{
  "title": "Google 为 Chrome 浏览器添加 Skills 功能，允许用户保存和复用 AI 提示词",
  "description": "2026 年 4 月 14 日，Google 为 Chrome 浏览器添加了 Skills 功能，允许用户保存和复用 AI 提示词。",
  "so_what": "产品经理和开发者应关注并学习使用此类 AI 原生交互功能，将其融入日常工作流。"
}
```

---

## 3. six_dimension_briefs 修改

### 当前问题

每个维度输出趋势判断（如"AI 产品正从功能插件进化为智能代理..."），这是深度分析的职责，不应出现在简报层。

### 修改方案

每个维度改为**一句话事实简报**，由该维度下多个新闻事实组合而成。

**格式要求**：
- 用逗号连接 2-3 个相关事实
- 不做趋势判断（不出现"正从...转向..."）
- 无显著动态的维度保持"今日无显著动态"

### 示例

**修改前**：
```json
{
  "ai_product_and_interaction": "AI 产品正从功能插件进化为智能代理，重塑基础工具（如浏览器）的交互范式，追求无缝的工作流集成与能力固化。"
}
```

**修改后**：
```json
{
  "ai_product_and_interaction": "Chrome Skills 功能上线，人形机器人产品收入占比超 40%，企业级 AI 智能体进入规模化落地。"
}
```

---

## 4. deep_analysis reasoning 优化

### 当前问题

部分 reasoning 只说"值得关注"，没有解释具体传导机制。

### 修改方案

**仅修改 prompt 表述**，代码逻辑不变。

**修改前 prompt**：
```
reasoning: 机制解释（变化如何传导）+ 适用条件 + 反证风险（什么情况下判断不成立）+ 验证路径（何时观察什么信号）
```

**修改后 prompt**：
```
reasoning: 用一大段话解释传导机制（变化如何通过产品/能力/市场反馈联动），并说明适用条件、反证风险（什么情况下这个判断不成立）和验证路径（未来何时观察什么信号）。不要只说"值得关注"，要解释具体如何传导。
```

---

## 5. 修改文件

- `ai_analyzer_v3.py`: `_generate_signal_interpretation` 和 `_generate_deep_analysis` 方法的 prompt

---

## 6. 验收标准

1. `top_events` 的 title 使用新闻原标题风格，不包含"重塑"、"范式"、"演进"等趋势词
2. `six_dimension_briefs` 每个维度是一句话事实组合，如"事实 A，事实 B，事实 C"
3. `deep_analysis` reasoning 字段包含具体的传导机制解释
