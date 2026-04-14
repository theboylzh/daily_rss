from pydantic_settings import BaseSettings
from typing import List
from datetime import time


class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "Daily RSS"
    DATA_DIR: str = "data"

    # 订阅源配置
    SUBSCRIPTION_FILE: str = "subscriptions.json"
    OPML_FILE: str = "subscriptions.opml"

    # V3 数据目录配置
    NEWS_DIR: str = "data/news"
    RAW_NEWS_DIR: str = "data/news/raw_news"
    FILTER_NEWS_DIR: str = "data/news/filter_news"
    REPORT_DIR: str = "data/report"
    DAILY_REPORT_DIR: str = "data/report/daily"

    # 新闻抓取配置
    NEWS_RETENTION_DAYS: int = 60  # 2个月

    # 历史分析配置（V2 兼容）
    ANALYSIS_DIR: str = "data/analysis"
    DAILY_ANALYSIS_DIR: str = "data/analysis/daily"
    
    # AI配置
    AI_API_KEY: str = ""
    AI_MODEL: str = "deepseek-chat"  # 默认使用DeepSeek模型
    AI_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    AI_SCORE_THRESHOLD: float = 5.5
    
    # 第三层分析配置
    THIRD_LAYER_TIMEOUT: int = 120  # 超时时间（秒）
    THIRD_LAYER_RETRIES: int = 3  # 重试次数
    THIRD_LAYER_RETRY_DELAY: int = 3  # 初始重试延迟（秒）
    
    # Tavily配置
    TAVILY_API_KEY: str = ""
    
    # 推送配置
    EMAIL_SENDER: str = ""
    EMAIL_RECEIVER: str = "theboylzh@163.com"
    EMAIL_PASSWORD: str = ""
    EMAIL_SMTP_SERVER: str = "smtp.163.com"
    EMAIL_SMTP_PORT: int = 465
    
    # 定时任务配置
    DAILY_SCHEDULE_TIME: time = time(8, 0, 0)  # 每天早上8点
    
    # 订阅源列表（示例）
    SUBSCRIPTIONS: List[str] = [
        "https://sanhua.himrr.com/daily-news/feed",
        "https://www.ifanr.com/feed",
        "https://www.tmtpost.com/feed",
        "https://www.woshipm.com/feed",
        "https://quail.ink/dingyi/feed/atom",
        "https://www.decohack.com/feed"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
