# V2.0.0 测试工具包使用说明

**创建日期**: 2026-04-11
**更新日期**: 2026-04-11 (架构重构 + 阶段 2 优化)
**用途**: 提供多种测试工具，支持不同场景下的验收需求

---

## 工具总览

| 工具 | 用途 | 适用场景 | 耗时 |
|------|------|----------|------|
| `.test/stage_debug_tool.py` | 分阶段调试 | 单独测试某个阶段 | 30-60 秒/阶段 |
| `.test/quick_debug.py` | 快速调试 | 修改提示词后快速验证 | 30-60 秒 |
| `.test/manual_test_step2.py` | 完整流程测试 | 验收前完整验证 | 2-3 分钟 (优化后) |
| `.test/manual_test_step3.py` | 邮件渲染测试 | 验证邮件样式 | <1 秒 |
| `.test/test_*.py` | 自动化测试 | CI/CD、回归测试 | <10 秒 |

---

## 1. 分阶段调试工具 - `.test/stage_debug_tool.py`

**适用场景**:
- 想单独测试阶段 1/2/3/4 中的某一个
- 调试某个阶段的提示词
- 查看某个阶段的中间结果

**使用方法**:

```bash
python3 .test/stage_debug_tool.py
```

**交互界面**:
```
命令:
  1 - 测试阶段 1：概要生成
  2 - 测试阶段 2：观点生成 (批量摘要优化)
  3 - 测试阶段 3：深度分析
  4 - 测试阶段 4：建议生成
  all - 运行所有阶段
  q - 退出
```

**输出文件**:
- `stage1_result.json` - 阶段 1 结果
- `stage2_result.json` - 阶段 2 结果
- `stage3_result.json` - 阶段 3 结果
- `stage4_result.json` - 阶段 4 结果

**技巧**:
- 阶段 2/3/4 会自动使用前一阶段的缓存结果
- 可以只运行阶段 1，然后单独调试阶段 3
- 每次修改提示词后，只需运行对应阶段的测试
- **阶段 2 已优化**：使用批量摘要，1 次 API 调用处理多条新闻，耗时从 100 秒降至 30 秒

---

## 2. 快速调试工具 - `.test/quick_debug.py`

**适用场景**:
- 刚修改了阶段 1 的提示词，想快速看效果
- 不想等待完整流程，只想验证 AI 输出质量
- 调试 one_liner、keywords 等字段的生成

**使用方法**:

```bash
python3 .test/quick_debug.py
```

**输出**:
- 控制台显示 one_liner、digest、keywords
- 保存完整结果到 `debug_stage1_result.json`
- 显示 AI 原始输出（方便调试解析问题）

**耗时**: 约 30 秒

---

## 3. 完整流程测试 - `.test/manual_test_step2.py`

**适用场景**:
- 验收前的完整验证
- 测试四个阶段的串联
- 生成用于邮件渲染的完整数据

**使用方法**:

```bash
python3 .test/manual_test_step2.py
```

**输出**:
- 控制台显示各阶段摘要
- 保存完整结果到 `test_v2_result.json`

**耗时**: 2-3 分钟 (阶段 2 优化后)

---

## 4. 邮件渲染测试 - `.test/manual_test_step3.py`

**适用场景**:
- 验证邮件模板渲染效果
- 检查样式和布局
- 生成用于人工检查的 HTML 文件

**使用方法**:

```bash
python3 .test/manual_test_step3.py
```

**输出**:
- `test_email_v2_output.html` - 可在浏览器中打开查看

**耗时**: <1 秒（使用已有数据）

---

## 5. 自动化测试套件

**文件列表**:
- `.test/test_email_render.py` - 邮件渲染单元测试
- `.test/test_integration.py` - 集成测试
- `.test/test_styles.py` - 样式测试

**运行方法**:

```bash
# 运行单个测试
python3 .test/test_email_render.py

# 运行所有测试
python3 -m unittest discover -s .test -p "test_*.py" -v
```

---

## 典型工作流

### 场景 1：调优阶段 1 提示词

```bash
# 1. 修改 ai_analyzer_v2.py 中的 _get_stage1_prompt()

# 2. 快速验证
python3 .test/quick_debug.py

# 3. 查看输出，检查 one_liner、keywords 等

# 4. 不满意？继续修改提示词，回到步骤 2

# 5. 满意后，运行完整阶段 1 测试
python3 .test/stage_debug_tool.py
# 选择 "1"
```

### 场景 2：调试阶段 3 分析质量

```bash
# 1. 确保有阶段 1 的缓存（运行过阶段 1）
python3 .test/stage_debug_tool.py
# 选择 "1" （如果还没有 stage1_result.json）

# 2. 单独测试阶段 3
python3 .test/stage_debug_tool.py
# 选择 "3"

# 3. 查看生成的分析结果
cat stage3_result.json | jq .
```

### 场景 3：验收前完整验证

```bash
# 1. 运行完整流程
python3 .test/manual_test_step2.py

# 2. 渲染邮件
python3 .test/manual_test_step3.py

# 3. 在浏览器中查看邮件
open test_email_v2_output.html

# 4. 运行自动化测试
python3 -m unittest discover -s .test -p "test_*.py" -v
```

---

## 文件结构

```
daily_rss/
├── ai_analyzer_v2.py          # V2 分析器（含提示词、解析器、Schema 定义）
├── push_manager.py            # 推送管理器
├── email_template_v2.html     # 邮件模板
│
├── .test/                     # 测试工具目录
│   ├── stage_debug_tool.py        # 分阶段调试工具
│   ├── quick_debug.py             # 快速调试工具
│   ├── manual_test_step2.py       # 完整流程测试
│   ├── manual_test_step3.py       # 邮件渲染测试
│   ├── test_email_render.py       # 单元测试
│   ├── test_integration.py        # 集成测试
│   └── test_styles.py             # 样式测试
│
├── stage1_result.json         # 阶段 1 缓存
├── stage2_result.json         # 阶段 2 缓存
├── stage3_result.json         # 阶段 3 缓存
├── stage4_result.json         # 阶段 4 缓存
├── test_v2_result.json        # 完整测试结果
│
└── docs/plans/
    ├── 2026-04-11-v2-manual-acceptance-guide.md   # 人工验收指南
    ├── 2026-04-11-v2-prompt-tuning-guide.md       # 提示词调优指南
    └── 2026-04-11-v2-test-tools-guide.md          # 测试工具指南
```

---

## 常见问题

### Q: 为什么阶段 1 测试显示"结构验证警告"？

A: 阶段 1 只负责生成 `summary`、`key_news_brief`、`briefing` 字段，不负责 `perspectives`、`deep_analysis`、`suggestions`。这是正常的，后续阶段会补充这些字段。

### Q: 如何只测试某一条新闻的分析？

A: 编辑 `quick_debug.py`，修改 `news_items[:10]` 为 `news_items[:1]`。

### Q: 测试数据从哪来？

A: 自动从 `data/news/` 目录加载最新的新闻文件。

### Q: 如何清理测试缓存？

A: 删除 `stage*_result.json` 和 `debug*_result.json` 文件即可。

### Q: 阶段 2 的优化是什么？

A: 阶段 2 使用批量摘要优化，将 10 条新闻的摘要生成从 10 次 API 调用减少到 1 次，耗时从约 100 秒降至约 30 秒。如果批量摘要失败，会自动降级为单条生成模式。

---

## 提示词修改位置

| 阶段 | 方法名 | 文件位置 |
|------|--------|----------|
| 阶段 1 | `_get_stage1_prompt()` | `ai_analyzer_v2.py` |
| 阶段 2 | `_get_stage2_prompt()` | `ai_analyzer_v2.py` |
| 阶段 2 批量摘要 | `_get_batch_news_summary_prompt()` | `ai_analyzer_v2.py` |
| 阶段 3 | `_get_stage3_prompt()` | `ai_analyzer_v2.py` |
| 阶段 4 | `_get_stage4_prompt()` | `ai_analyzer_v2.py` |

---

**提示**: 建议调优提示词时使用 `quick_debug.py`，验收时使用 `manual_test_step2.py`，日常调试使用 `stage_debug_tool.py`。
