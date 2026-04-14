import logging
import traceback
from datetime import datetime

from daily_report_service import DailyReportService
from news_fetcher import NewsFetcher
from news_processor import NewsProcessor
from push_manager import PushManager
from storage_manager import StorageManager


logger = logging.getLogger(__name__)


class WorkflowRunner:
    """只保留 daily 主链路：抓取、过滤、分析、发送。"""

    def __init__(self):
        self.storage = StorageManager()
        self.daily_report_service = DailyReportService()

    def run_daily(self):
        logger.info("Daily RSS 工具启动")
        try:
            logger.info("开始抓取新闻...")
            news_fetcher = NewsFetcher()
            raw_news = news_fetcher.fetch_news()
            if not raw_news:
                logger.warning("无新闻可分析")
                return

            logger.info("开始处理新闻...")
            news_processor = NewsProcessor()
            filter_payload = news_processor.process_news(raw_news)
            if not filter_payload.get("news", []):
                logger.warning("处理后无有效新闻")
                return

            logger.info("开始生成 V3 日报...")
            daily_report = self.daily_report_service.build(
                filter_payload,
                raw_news_count=len(raw_news),
            )
            logger.info(
                "V3 日报已生成：date=%s filtered=%s candidates=%s",
                daily_report["meta"]["date"],
                daily_report["meta"]["filtered_count"],
                len(daily_report.get("internal_candidates", {}).get("trend_candidates", [])),
            )

            logger.info("开始推送 V3 日报...")
            push_manager = PushManager()
            push_success = push_manager.send_daily_analysis(daily_report)
            if not push_success:
                logger.warning("推送失败")
                return

            logger.info("开始清理过期数据...")
            news_fetcher.clean_old_news()
            logger.info("Daily RSS 工具执行完成")
        except Exception as exc:
            logger.error("执行失败：%s", exc, exc_info=True)
            self._send_error_email(exc)

    def send_v3_daily_email(self, date_str=None):
        push_manager = PushManager()
        payload = self.storage.read_json(self.storage.get_daily_report_path(date_str), default={})
        if not payload:
            logger.warning("未找到 V3 daily report，无法发送结构化模板邮件")
            return
        push_manager.send_daily_analysis(payload)

    def _send_error_email(self, exc):
        try:
            push_manager = PushManager()
            error_analysis = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "first_layer": "# 执行错误\n\n系统执行失败：%s" % str(exc),
                "second_layer": [],
                "third_layer": "# 错误详情\n\n%s" % traceback.format_exc(),
                "timestamp": datetime.now().isoformat(),
                "news_count": 0,
            }
            push_manager.send_daily_analysis(error_analysis)
        except Exception as notify_error:
            logger.error("发送错误通知失败：%s", notify_error)
