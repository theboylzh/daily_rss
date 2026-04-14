import json
import os
from datetime import datetime
from typing import Any, Optional

from config import settings


class StorageManager:
    """V3 统一存储管理，集中处理目录、路径和 JSON 读写。"""

    def __init__(self):
        self._ensure_base_directories()

    def _ensure_base_directories(self):
        directories = [
            settings.DATA_DIR,
            settings.NEWS_DIR,
            settings.RAW_NEWS_DIR,
            settings.FILTER_NEWS_DIR,
            settings.REPORT_DIR,
            settings.DAILY_REPORT_DIR,
            settings.ANALYSIS_DIR,
            settings.DAILY_ANALYSIS_DIR,
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_raw_news_path(self, date_str: Optional[str] = None) -> str:
        return os.path.join(settings.RAW_NEWS_DIR, f"{self._resolve_date(date_str)}.json")

    def get_filter_news_path(self, date_str: Optional[str] = None) -> str:
        return os.path.join(settings.FILTER_NEWS_DIR, f"{self._resolve_date(date_str)}.json")

    def get_daily_report_path(self, date_str: Optional[str] = None) -> str:
        return os.path.join(settings.DAILY_REPORT_DIR, f"{self._resolve_date(date_str)}.json")

    def write_json(self, file_path: str, data: Any):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def read_json(self, file_path: str, default: Optional[Any] = None) -> Any:
        if not os.path.exists(file_path):
            return default
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def exists(self, file_path: str) -> bool:
        return os.path.exists(file_path)

    def list_json_files(self, directory: str) -> list[str]:
        if not os.path.exists(directory):
            return []
        return sorted(
            os.path.join(directory, filename)
            for filename in os.listdir(directory)
            if filename.endswith(".json")
        )

    def list_raw_news_files(self) -> list[str]:
        return self.list_json_files(settings.RAW_NEWS_DIR)

    def list_filter_news_files(self) -> list[str]:
        return self.list_json_files(settings.FILTER_NEWS_DIR)

    def list_daily_report_files(self) -> list[str]:
        return self.list_json_files(settings.DAILY_REPORT_DIR)

    def read_date_bucket(self, file_path: str, default_key: str) -> list[dict[str, Any]]:
        data = self.read_json(file_path, default={})
        if isinstance(data, dict):
            value = data.get(default_key, [])
            if isinstance(value, list):
                return value
        if isinstance(data, list):
            return data
        return []

    def _resolve_date(self, date_str: Optional[str]) -> str:
        return date_str or datetime.now().strftime("%Y-%m-%d")
