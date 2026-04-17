# Trend Radar

AI 驱动的 RSS 情报日报，自动抓取、分析、推送。

## 快速复用

### 1. Fork 仓库

点击右上角 **Fork** → 复制到你自己的 GitHub

### 2. 配置 Secrets

进入你的仓库 **Settings → Secrets → Actions**，添加：

| Secret | 说明 |
|--------|------|
| `AI_API_KEY` | DeepSeek API Key（推荐） |
| `EMAIL_SENDER` | 发件人邮箱 |
| `EMAIL_RECEIVER` | 收件人邮箱 |
| `EMAIL_PASSWORD` | 邮箱授权码（不是密码） |
| `TAVILY_API_KEY` | Tavily API Key（可选） |

### 3. 启用 Actions

进入 **Actions** → 启用 workflow → 点击 **Run workflow** 测试

### 4. 完成

每日北京时间凌晨 4:00 自动运行，醒来即可查看邮件报告。

---

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写 API 密钥

# 运行
python main.py
```

---

## V3 邮件模板

基于 Figma 设计的 800px 深色主题邮件：

- **Key Insight**：主结论 + 为什么重要
- **Top Events**：3 个关键事件卡片
- **Six Dimensions**：6 维趋势简报
- **Trend Watch**：深度趋势分析
- **Actions**：今日/本周/本月行动建议

---

## 项目结构

```
daily_rss/
├── main.py              # 入口
├── config.py            # 配置
├── news_fetcher.py      # RSS 抓取
├── ai_analyzer_v3.py    # AI 分析
├── v3_email_renderer.py # 邮件渲染
├── push_manager.py      # 邮件推送
├── workflow_runner.py   # 流程编排
└── data/
    ├── news/            # 新闻数据
    └── report/daily/    # 分析报告
```

---

## 修改订阅源

编辑 `config.py` 的 `SUBSCRIPTIONS` 列表，或使用命令：

```bash
python main.py add <rss_url> <name>
python main.py list
python main.py remove <id>
```

---

## 修改运行时间

编辑 `.github/workflows/rss-tool.yml`：

| 北京时间 | cron |
|---------|------|
| 凌晨 4:00 | `'0 20 * * *'` |
| 早上 8:00 | `'0 0 * * *'` |

---

## 许可证

MIT