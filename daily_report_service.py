from typing import Any, Dict, Optional

from ai_analyzer_v3 import AIAnalyzerV3
from daily_report_builder import DailyReportBuilder


class DailyReportService:
    """负责日报生成策略：优先 AI，失败回退基础构建版。"""

    def __init__(self):
        self.ai_analyzer = AIAnalyzerV3()
        self.report_builder = DailyReportBuilder()

    def build(self, filter_payload: Dict[str, Any], raw_news_count: Optional[int] = None) -> Dict[str, Any]:
        report = self.ai_analyzer.analyze_daily_report_v3(
            filter_payload,
            raw_news_count=raw_news_count,
        )
        if report:
            return report
        return self.report_builder.build(
            filter_payload,
            raw_news_count=raw_news_count,
        )
