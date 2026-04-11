# Daily RSS V2.0.0 PRD 设计文档

**创建日期**: 2026-04-11
**版本**: V2.0.0
**状态**: 待审批

---

## 一、版本概述

### 1.1 变更动机

V1.0.0 版本存在以下问题：
- AI 分析流程较为简单，缺乏深度观点输出
- 输出格式为 Markdown，不利于后端结构化处理
- 邮件内容结构单一，缺少多维度的分析视角

### 1.2 V2.0.0 核心目标

1. **结构化输出**: 从 Markdown 改为 JSON 格式，便于后端处理和邮件模板渲染
2. **四层分析流程**: 重构 AI 工作流，增加观点生成和建议生成环节
3. **内容升级**: 新增「观点」「建议」板块，提供更深入的分析视角
4. **降级处理**: 完善 JSON 解析失败的降级策略，提高系统稳定性

---

## 二、输出 JSON Schema

### 2.1 完整数据结构

```json
{
  "summary": {
    "one_liner": "一句话总结（20-30 字，抽象理性）",
    "digest": "今日摘要（2-3 句话概括今日事件）",
    "keywords": ["关键词 1", "关键词 2", "关键词 3"]
  },
  "key_news_brief": [
    {
      "title": "新闻标题",
      "tags": ["标签 1", "标签 2"]
    }
  ],
  "briefing": {
    "politics": "政治时事简报内容",
    "economy": "宏观经济简报内容",
    "industry": "行业动态简报内容",
    "tech": "科技新闻简报内容"
  },
  "perspectives": [
    {
      "title": "观点标题",
      "description": "观点描述（基于重点新闻生成的结构化内容）",
      "references": [
        {"title": "引用文章标题 1", "url": "https://..."},
        {"title": "引用文章标题 2", "url": "https://..."}
      ]
    }
  ],
  "deep_analysis": [
    {
      "tags": ["政治"],
      "title": "事件标题",
      "facts": "客观事实描述",
      "viewpoint": "整体观点",
      "causes": "发生原因",
      "prediction": "后续预测",
      "advice": "个体建议"
    }
  ],
  "suggestions": {
    "thinking": {
      "title": "思维启发标题",
      "content": "思维启发内容"
    },
    "investment": {
      "title": "投资建议标题",
      "content": "投资建议内容"
    },
    "self_improvement": {
      "title": "个人提升标题",
      "content": "个人提升内容"
    },
    "opportunities_risks": {
      "title": "机遇风险标题",
      "content": "机遇风险内容"
    }
  }
}
```

### 2.2 字段说明

| 字段 | 类型 | 说明 | 来源 |
|------|------|------|------|
| `summary.one_liner` | string | 一句话总结，抽象理性，20-30 字 | 阶段 1 |
| `summary.digest` | string | 今日摘要，2-3 句话描述今日事件 | 阶段 1 |
| `summary.keywords` | string[] | 三个关键词，AI 生成 | 阶段 1 |
| `key_news_brief` | array | 三个关键新闻，用于「今日概要」展示 | 阶段 1 |
| `briefing.*` | string | 四类新闻简报（政治/经济/行业/科技） | 阶段 1 |
| `perspectives` | array | 三个观点，每个包含标题、描述、引用 | 阶段 2 |
| `deep_analysis` | array | 三个关键事件的深度分析 | 阶段 3 |
| `suggestions.*` | object | 四类建议（思维/投资/个人提升/机遇风险） | 阶段 4 |

---

## 三、AI 工作流设计

### 3.1 整体流程

```
输入：新闻列表（10-50 条）
        ↓
    ┌─────────────────────────────────────┐
    │  阶段 1：概要生成                      │
    │  - 一句话总结                         │
    │  - 今日摘要                           │
    │  - 三个关键词                         │
    │  - 重点新闻列表（5-10 条，给阶段 2 用）   │
    │  - 三个关键新闻（带标签，给阶段 3 用）   │
    │  - 新闻简报（政治/经济/行业/科技）      │
    └─────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │  阶段 2：观点生成                      │
    │  1. 阅读重点新闻标题 + 正文            │
    │  2. 生成结构化摘要（每条 100 字）        │
    │  3. 汇总 → 观点素材包（约 300-500 字）   │
    │  4. 生成 3 个观点框架                    │
    │  5. 输出完整观点（标题 + 描述 + 引用）   │
    └─────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │  阶段 3：关键事件深度分析              │
    │  - 输入：阶段 1 的三个关键新闻          │
    │  - 输出：标签 + 事实 + 观点 + 原因 +     │
    │         预测 + 建议                    │
    └─────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │  阶段 4：建议生成                      │
    │  - 思维启发                           │
    │  - 投资建议                           │
    │  - 个人提升                           │
    │  - 机遇风险                           │
    └─────────────────────────────────────┘
        ↓
    JSON 输出 → 降级处理 → 邮件模板渲染
```

### 3.2 阶段 1：概要生成

**输入**: 新闻列表（10-50 条，每条包含标题、正文、来源、时间）

**输出**:
```json
{
  "one_liner": "...",
  "digest": "...",
  "keywords": ["...", "...", "..."],
  "key_news_list": [
    {"title": "...", "content": "...", "url": "...", "source": "..."}
  ],
  "key_news_brief": [
    {"title": "...", "tags": ["...", "..."]}
  ],
  "briefing": {
    "politics": "...",
    "economy": "...",
    "industry": "...",
    "tech": "..."
  }
}
```

**Prompt 设计要点**:
- 一次性生成所有字段，减少 API 调用次数
- `key_news_list` 和 `key_news_brief` 是两个不同的列表：
  - `key_news_list`: 5-10 条，包含完整标题 + 正文，供阶段 2 使用
  - `key_news_brief`: 3 条，带标签，用于展示和阶段 3 使用
- 标签从预设标签库中选择：["政治", "经济", "科技", "商业", "金融", "国际", "政策", "创新"]

---

### 3.3 阶段 2：观点生成

**输入**: 阶段 1 的 `key_news_list`（5-10 条重点新闻，含标题 + 正文）

**处理流程**:

```python
# 步骤 1：为每条重点新闻生成结构化摘要
summaries = []
for news in key_news_list:
    summary = ai_generate_summary(news, max_length=100)
    summaries.append(summary)

# 步骤 2：汇总摘要形成观点素材包
summary_package = "\n---\n".join(summaries)
# 总长度约 500-1000 字，控制在上下文窗口内

# 步骤 3：基于素材包生成 3 个观点框架
frameworks = ai_generate_frameworks(summary_package)
# 输出：[{"title": "...", "core_argument": "..."}, ...]

# 步骤 4：为每个观点生成完整描述
perspectives = []
for framework in frameworks:
    perspective = ai_expand_description(framework, summary_package)
    perspectives.append(perspective)
```

**输出**:
```json
{
  "perspectives": [
    {
      "title": "观点标题",
      "description": "观点描述（200-300 字）",
      "references": [
        {"title": "新闻标题 1", "url": "https://..."},
        {"title": "新闻标题 2", "url": "https://..."}
      ]
    }
  ]
}
```

**注意**: V2.0.0 暂不使用 Tavily 搜索，观点的引用文章直接来自原始新闻列表。

---

### 3.4 阶段 3：关键事件深度分析

**输入**: 阶段 1 的 `key_news_brief`（3 条关键新闻）

**输出**:
```json
{
  "deep_analysis": [
    {
      "tags": ["政治"],
      "title": "事件标题",
      "facts": "客观事实描述（谁在什么场合/时间做了什么）",
      "viewpoint": "整体观点（重点/亮点/影响级/好坏程度）",
      "causes": "发生原因（主体 + 动机）",
      "prediction": "后续预测（观点鲜明）",
      "advice": "个体建议（投资/消费/就业/生活角度）"
    }
  ]
}
```

**实现**: 沿用 V1.0.0 的第二层分析逻辑，改为 JSON 输出格式。

---

### 3.5 阶段 4：建议生成

**输入**: 阶段 1 + 阶段 2 + 阶段 3 的综合信息

**输出**:
```json
{
  "suggestions": {
    "thinking": {"title": "...", "content": "..."},
    "investment": {"title": "...", "content": "..."},
    "self_improvement": {"title": "...", "content": "..."},
    "opportunities_risks": {"title": "...", "content": "..."}
  }
}
```

---

## 四、JSON 解析降级策略

### 4.1 四层降级流程

```
┌─────────────────────────────────────────┐
│ 第 1 层：直接 JSON 解析                      │
│ json.loads(ai_response_text)            │
└─────────────────────────────────────────┘
                ↓ 失败
┌─────────────────────────────────────────┐
│ 第 2 层：提取 Markdown 代码块               │
│ 正则提取 ```json ... ``` 内容再解析        │
└─────────────────────────────────────────┘
                ↓ 失败
┌─────────────────────────────────────────┐
│ 第 3 层：正则提取 JSON 片段                 │
│ 用正则匹配 {.*} 或 \[.*\] 尝试提取         │
└─────────────────────────────────────────┘
                ↓ 失败
┌─────────────────────────────────────────┐
│ 第 4 层：返回空结构 + 记录错误日志          │
│ 发送错误通知邮件                          │
└─────────────────────────────────────────┘
```

### 4.2 实现代码框架

```python
def parse_ai_json_response(text: str) -> dict:
    """解析 AI 输出的 JSON，带降级处理"""
    
    # 第 1 层：直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 第 2 层：提取 Markdown 代码块
    markdown_pattern = r'```json\s*(.*?)\s*```'
    match = re.search(markdown_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # 第 3 层：正则提取 JSON 对象
    json_pattern = r'\{[^{}]*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # 第 4 层：返回空结构
    logger.error(f"JSON 解析失败：{text[:500]}...")
    return get_empty_structure()
```

---

## 五、标签体系

### 5.1 预设标签库

```python
TAGS_LIBRARY = [
    "政治",      # 政府、政策、国际关系
    "经济",      # 宏观经济、GDP、通胀
    "科技",      # 技术突破、前沿科技
    "商业",      # 公司动态、商业合作
    "金融",      # 银行、证券、保险
    "国际",      # 国际时事
    "政策",      # 行业政策、监管
    "创新",      # 新产品、新技术
    "行业",      # 行业动态、供需变化
    "市场"       # 市场波动、股价变化
]
```

### 5.2 AI 标签选择

在 Prompt 中明确要求：
- 从预设标签库中选择 1-2 个标签
- 不要自创标签
- 优先选择最匹配的标签

---

## 六、邮件模板渲染

### 6.1 HTML 模板结构

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    /* CSS 样式 */
  </style>
</head>
<body>
  <h1>{{ summary.one_liner }}</h1>
  
  <section class="summary">
    <h2>今日摘要</h2>
    <p>{{ summary.digest }}</p>
    <div class="keywords">
      <span class="keyword">{{ summary.keywords[0] }}</span>
      <span class="keyword">{{ summary.keywords[1] }}</span>
      <span class="keyword">{{ summary.keywords[2] }}</span>
    </div>
  </section>
  
  <section class="key-news">
    <h2>关键新闻</h2>
    {% for news in key_news_brief %}
    <div class="news-item">
      <h3>{{ news.title }}</h3>
      <div class="tags">
        {% for tag in news.tags %}
        <span class="tag">{{ tag }}</span>
        {% endfor %}
      </div>
    </div>
    {% endfor %}
  </section>
  
  <section class="briefing">
    <h2>新闻简报</h2>
    <div class="briefing-item">
      <h3>政治时事</h3>
      <p>{{ briefing.politics }}</p>
    </div>
    <div class="briefing-item">
      <h3>宏观经济</h3>
      <p>{{ briefing.economy }}</p>
    </div>
    <div class="briefing-item">
      <h3>行业动态</h3>
      <p>{{ briefing.industry }}</p>
    </div>
    <div class="briefing-item">
      <h3>科技新闻</h3>
      <p>{{ briefing.tech }}</p>
    </div>
  </section>
  
  <section class="perspectives">
    <h2>观点</h2>
    {% for perspective in perspectives %}
    <div class="perspective">
      <h3>{{ perspective.title }}</h3>
      <p>{{ perspective.description }}</p>
      <div class="references">
        {% for ref in perspective.references %}
        <a href="{{ ref.url }}">{{ ref.title }}</a>
        {% endfor %}
      </div>
    </div>
    {% endfor %}
  </section>
  
  <section class="deep-analysis">
    <h2>关键分析</h2>
    {% for analysis in deep_analysis %}
    <div class="analysis-item">
      <h3>{{ analysis.title }}</h3>
      <div class="tags">
        {% for tag in analysis.tags %}
        <span class="tag">{{ tag }}</span>
        {% endfor %}
      </div>
      <div class="analysis-content">
        <h4>客观事实</h4>
        <p>{{ analysis.facts }}</p>
        <h4>整体观点</h4>
        <p>{{ analysis.viewpoint }}</p>
        <h4>发生原因</h4>
        <p>{{ analysis.causes }}</p>
        <h4>后续预测</h4>
        <p>{{ analysis.prediction }}</p>
        <h4>个体建议</h4>
        <p>{{ analysis.advice }}</p>
      </div>
    </div>
    {% endfor %}
  </section>
  
  <section class="suggestions">
    <h2>建议</h2>
    <div class="suggestion-item">
      <h3>思维启发</h3>
      <p>{{ suggestions.thinking.content }}</p>
    </div>
    <div class="suggestion-item">
      <h3>投资建议</h3>
      <p>{{ suggestions.investment.content }}</p>
    </div>
    <div class="suggestion-item">
      <h3>个人提升</h3>
      <p>{{ suggestions.self_improvement.content }}</p>
    </div>
    <div class="suggestion-item">
      <h3>机遇风险</h3>
      <p>{{ suggestions.opportunities_risks.content }}</p>
    </div>
  </section>
</body>
</html>
```

---

## 七、验收标准

### 7.1 功能验收

| 验收项 | 标准 |
|--------|------|
| JSON 输出 | AI 能稳定输出符合 Schema 的 JSON |
| 降级处理 | 解析失败时能正确降级，不崩溃 |
| 四层分析 | 四个阶段按顺序执行，数据正确传递 |
| 标签体系 | AI 从预设标签库中选择标签 |
| 邮件渲染 | HTML 模板能正确渲染所有字段 |

### 7.2 性能验收

| 指标 | 目标 |
|------|------|
| 总耗时 | < 5 分钟（含 4 次 AI 调用） |
| Token 消耗 | < 50,000 tokens/次 |
| 成功率 | > 95%（含降级处理） |

---

## 八、后续优化方向

1. **Tavily 搜索集成** - 在阶段 2 中引入外部搜索，增强观点的可信度
2. **智能评分机制** - 对新闻进行重要性评分，辅助筛选关键新闻
3. **并行处理优化** - 阶段 2、3、4 可以部分并行执行
4. **标签自学习** - 根据用户反馈优化标签体系

---

## 九、待确认事项

- [ ] PRD 审批通过
- [ ] JSON Schema 最终确认
- [ ] 邮件模板 UI 设计确认
- [ ] Prompt 调优策略确认

---

**下一步**: PRD 审批通过后，进入实现计划阶段。
