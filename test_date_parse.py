#!/usr/bin/env python3
from datetime import datetime
import feedparser

class TestDateParse:
    def test_feedparser_parse_date(self):
        """测试feedparser.parse_date的行为"""
        print("开始测试feedparser.parse_date...")
        
        test_cases = [
            ("2026-02-16T10:00:00Z", "ISO格式日期"),
            ("Mon, 16 Feb 2026 10:00:00 GMT", "RFC格式日期"),
            ("2026-02-16 10:00:00", "普通格式日期"),
            (None, "None值"),
            ("", "空字符串"),
            ("invalid_date", "无效日期字符串")
        ]
        
        for date_str, description in test_cases:
            print(f"\n测试: {description}")
            print(f"输入: {date_str}")
            
            try:
                result = feedparser.parse_date(date_str)
                print(f"结果: {result}")
                print(f"类型: {type(result)}")
                if isinstance(result, datetime):
                    print(f"ISO格式: {result.isoformat()}")
            except Exception as e:
                print(f"异常: {type(e).__name__}: {e}")
        
    def test_hasattr_behavior(self):
        """测试hasattr的行为"""
        print("\n\n测试hasattr行为...")
        
        class MockEntry:
            def __init__(self, published):
                self.published = published
        
        test_entries = [
            MockEntry("2026-02-16T10:00:00Z"),
            MockEntry(None),
            MockEntry(""),
            MockEntry("invalid_date")
        ]
        
        for i, entry in enumerate(test_entries):
            print(f"\n测试条目 {i+1}:")
            print(f"  published属性值: {entry.published}")
            print(f"  hasattr(entry, 'published'): {hasattr(entry, 'published')}")
            print(f"  'published' in dir(entry): {'published' in dir(entry)}")

if __name__ == "__main__":
    tester = TestDateParse()
    tester.test_feedparser_parse_date()
    tester.test_hasattr_behavior()
