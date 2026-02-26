# Daily RSS 工具

一个简易的RSS工具，用于抓取订阅源的最新新闻，通过AI进行分析，并以美观的HTML格式推送到邮箱。

## 功能特性

- **订阅源管理**：支持OPML导入、手动添加/删除订阅源
- **新闻抓取**：自动抓取24小时内的最新新闻，支持去重
- **AI分析**：使用AI模型对新闻进行分析，支持并行分析
- **推送功能**：将分析结果以美观的HTML格式推送到邮箱
- **自动化操作**：支持每日定时任务，通过 GitHub Actions 调度
- **数据管理**：自动清理过期数据，保留2个月的新闻数据

## 技术栈

- 开发语言：Python 3.10+
- 核心库：feedparser、requests、BeautifulSoup4、python-dotenv、schedule
- 数据存储：JSON文件
- 自动化：本地使用schedule库，云端使用GitHub Actions

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制`.env.example`文件为`.env`，并填写相关配置：

```bash
cp .env.example .env
```

编辑`.env`文件，填写以下内容：

```
# AI配置
AI_API_KEY="your_ai_api_key_here"
AI_MODEL="glm-4"
AI_API_URL="https://open.bigmodel.cn/api/mcp/text2text"

# 邮箱配置
EMAIL_SENDER="your_email@163.com"
EMAIL_RECEIVER="theboylzh@163.com"
EMAIL_PASSWORD="your_email_password_or_app_password"
EMAIL_SMTP_SERVER="smtp.163.com"
EMAIL_SMTP_PORT=465
```

### 3. 配置订阅源

- **方法一**：在`config.py`的`SUBSCRIPTIONS`列表中添加订阅源URL
- **方法二**：使用命令行添加订阅源

```bash
python main.py add <url> [name]
```

- **方法三**：将OPML文件放在`data`目录下，命名为`subscriptions.opml`

### 4. 运行工具

#### 手动运行每日任务

```bash
python main.py
```

#### 查看订阅源列表

```bash
python main.py list
```

#### 删除订阅源

```bash
python main.py remove <subscription_id>
```

## 部署方案

### 本地部署

1. 按照上述步骤配置环境
2. 使用`schedule`库实现定时任务（可选）

### 云端部署（推荐）

使用GitHub Actions实现稳定的定时任务：

#### 1. 准备工作

1. **创建GitHub仓库**：创建一个新的GitHub仓库，或使用现有仓库
2. **上传代码**：将项目代码推送到GitHub仓库

#### 2. 配置GitHub Secrets

在仓库的`Settings > Secrets and variables > Actions`中添加以下密钥：

| Secret名称 | 描述 | 必需 |
|-----------|------|------|
| `AI_API_KEY` | AI模型的API密钥（如DeepSeek） | ✓ |
| `EMAIL_SENDER` | 发送邮件的邮箱地址 | ✓ |
| `EMAIL_RECEIVER` | 接收邮件的邮箱地址 | ✓ |
| `EMAIL_PASSWORD` | 发送邮件的邮箱密码（建议使用应用密码） | ✓ |
| `TAVILY_API_KEY` | Tavily搜索的API密钥（可选） | ✗ |

#### 3. 邮箱应用密码设置

为了安全起见，建议使用邮箱的应用密码而不是主密码：

**163邮箱设置**：
1. 登录163邮箱
2. 进入「设置」>「POP3/SMTP/IMAP」
3. 开启「IMAP/SMTP服务」
4. 点击「客户端授权密码」，按照提示设置

**Gmail设置**：
1. 登录Gmail
2. 进入「管理您的Google账户」
3. 选择「安全性」>「应用密码」
4. 按照提示创建应用密码

#### 4. 启用GitHub Actions

1. 进入仓库的「Actions」标签页
2. 确认工作流文件已正确加载
3. 手动触发工作流测试：点击「Run workflow」

#### 5. 验证部署

1. **检查工作流执行状态**：在「Actions」标签页查看执行状态
2. **验证邮件推送**：检查接收邮箱是否收到分析报告
3. **查看日志**：如果执行失败，查看详细日志进行排查

#### 6. 部署测试

运行以下命令测试部署配置：

```bash
# 测试配置验证
python validate_config.py

# 测试本地运行
python main.py
```

#### 7. 定时任务配置

GitHub Actions工作流默认配置：
- **每日任务**：每天UTC时间8:00（北京时间16:00）
- **每周任务**：每周一UTC时间8:00（北京时间16:00）
- **每月任务**：每月1日UTC时间8:00（北京时间16:00）

如需调整时间，修改`.github/workflows/rss-tool.yml`文件中的cron表达式。

#### 8. 常见部署问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 邮件发送失败 | 邮箱密码错误或未开启SMTP服务 | 检查邮箱设置，使用应用密码 |
| AI分析失败 | API密钥错误或余额不足 | 检查API密钥，确保余额充足 |
| 工作流执行失败 | Secrets未配置或配置错误 | 检查Secrets配置，确保名称正确 |
| 新闻抓取失败 | 网络连接问题或订阅源无效 | 检查网络连接，验证订阅源URL |

#### 9. 部署最佳实践

1. **定期更新依赖**：每季度更新一次`requirements.txt` 中的依赖版本
2. **监控执行状态**：定期检查工作流执行状态和日志
3. **备份配置**：定期备份`.env` 文件和 GitHub Secrets 配置
4. **安全管理**：定期轮换 API 密钥和密码（建议每 3-6 个月）
5. **性能优化**：根据实际情况调整订阅源数量和分析深度
6. **配置验证**：部署后运行`python validate_config.py` 验证配置

## 项目结构

```
daily_rss/
├── .github/
│   └── workflows/
│       └── rss-tool.yml      # GitHub Actions配置
├── data/
│   ├── news/                 # 新闻存储目录
│   ├── analysis/
│   │   ├── daily/            # 每日分析结果
│   │   ├── weekly/           # 每周分析结果（已废弃）
│   │   └── monthly/          # 每月分析结果（已废弃）
│   └── subscriptions.json    # 订阅源配置
├── .env.example              # 环境变量示例
├── .gitignore                # Git忽略文件
├── config.py                 # 配置管理
├── subscription_manager.py   # 订阅源管理
├── news_fetcher.py           # 新闻抓取
├── ai_analyzer.py            # AI分析
├── push_manager.py           # 推送管理
├── main.py                   # 主程序
├── requirements.txt          # 依赖文件
├── README.md                 # 项目说明
└── PRD.md                    # 产品需求文档
```

## 配置说明

### 核心配置（config.py）

- `PROJECT_NAME`：项目名称
- `DATA_DIR`：数据存储目录
- `SUBSCRIPTION_FILE`：订阅源配置文件
- `OPML_FILE`：OPML文件路径
- `NEWS_DIR`：新闻存储目录
- `NEWS_RETENTION_DAYS`：新闻保留天数（默认60天）
- `ANALYSIS_DIR`：分析结果存储目录
- `DAILY_ANALYSIS_DIR`：每日分析结果目录
- `AI_API_KEY`：AI模型的API密钥
- `AI_MODEL`：AI模型名称（默认glm-4）
- `AI_API_URL`：AI模型的API地址
- `EMAIL_SENDER`：发送邮件的邮箱地址
- `EMAIL_RECEIVER`：接收邮件的邮箱地址
- `EMAIL_PASSWORD`：发送邮件的邮箱密码
- `EMAIL_SMTP_SERVER`：SMTP服务器地址
- `EMAIL_SMTP_PORT`：SMTP服务器端口
- `DAILY_SCHEDULE_TIME`：每日任务的执行时间
- `SUBSCRIPTIONS`：订阅源列表

### 环境变量（.env）

环境变量会覆盖`config.py`中的默认配置，建议将敏感信息放在环境变量中。

## 使用指南

### 添加订阅源

```bash
python main.py add https://example.com/rss "Example RSS"
```

### 删除订阅源

```bash
python main.py remove <subscription_id>
```

### 查看订阅源列表

```bash
python main.py list
```

### 手动运行每日任务

```bash
python main.py
```

## 注意事项

1. **AI API密钥**：需要配置有效的AI模型API密钥才能进行分析
2. **邮箱配置**：需要配置有效的邮箱信息才能发送邮件
3. **GitHub Actions**：需要将代码上传到GitHub仓库并配置Secrets
4. **数据存储**：数据存储在`data`目录下，建议定期备份
5. **API调用限制**：注意AI模型的API调用频率和token消耗

## 故障排除

### 常见问题

1. **邮件发送失败**：检查邮箱配置是否正确，特别是密码（建议使用应用密码）
2. **AI分析失败**：检查AI API密钥是否正确，以及API调用是否达到限制
3. **新闻抓取失败**：检查网络连接，以及订阅源URL是否有效
4. **GitHub Actions执行失败**：检查Secrets配置是否正确，以及workflow文件是否有语法错误

### 日志查看

工具会生成`rss_tool.log`文件，记录运行过程中的日志信息，可用于排查问题。

### 配置验证

运行以下命令验证配置是否正确：

```bash
python validate_config.py
```

此脚本会检查：
- 环境变量配置
- 依赖项安装情况
- 文件结构完整性
- GitHub Actions workflow 配置
- .gitignore 配置

## 后续优化

- 支持更多推送方式（如Telegram、飞书等）
- 增加数据分析和可视化功能
- 支持更多AI模型和分析维度
- 优化AI分析的准确性和效率
- 减少token消耗
- 提高系统稳定性和容错能力

## 许可证

MIT
