#!/usr/bin/env python3
from datetime import datetime, timedelta
import json
import os
from news_fetcher import NewsFetcher

class TestFilter:
    def test_filter_recent_news(self):
        """测试24小时过滤功能"""
        print("开始测试24小时过滤功能...")
        
        # 创建测试新闻数据
        test_news = []
        
        # 创建不同时间的新闻
        now = datetime.now()
        
        # 1. 2小时前的新闻（应该保留）
        test_news.append({
            "id": "news1",
            "title": "2小时前的新闻",
            "url": "http://example.com/news1",
            "content": "这是2小时前的新闻内容",
            "source": "test_source",
            "published_at": (now - timedelta(hours=2)).isoformat(),
            "collected_at": now.isoformat()
        })
        
        # 2. 20小时前的新闻（应该保留）
        test_news.append({
            "id": "news2",
            "title": "20小时前的新闻",
            "url": "http://example.com/news2",
            "content": "这是20小时前的新闻内容",
            "source": "test_source",
            "published_at": (now - timedelta(hours=20)).isoformat(),
            "collected_at": now.isoformat()
        })
        
        # 3. 25小时前的新闻（应该被过滤）
        test_news.append({
            "id": "news3",
            "title": "25小时前的新闻",
            "url": "http://example.com/news3",
            "content": "这是25小时前的新闻内容",
            "source": "test_source",
            "published_at": (now - timedelta(hours=25)).isoformat(),
            "collected_at": now.isoformat()
        })
        
        # 4. 48小时前的新闻（应该被过滤）
        test_news.append({
            "id": "news4",
            "title": "48小时前的新闻",
            "url": "http://example.com/news4",
            "content": "这是48小时前的新闻内容",
            "source": "test_source",
            "published_at": (now - timedelta(hours=48)).isoformat(),
            "collected_at": now.isoformat()
        })
        
        # 5. 日期解析失败的新闻（应该保留）
        test_news.append({
            "id": "news5",
            "title": "日期解析失败的新闻",
            "url": "http://example.com/news5",
            "content": "这是日期解析失败的新闻内容",
            "source": "test_source",
            "published_at": "invalid_date",
            "collected_at": now.isoformat()
        })
        
        # 6. 空日期的新闻（应该保留）
        test_news.append({
            "id": "news6",
            "title": "空日期的新闻",
            "url": "http://example.com/news6",
            "content": "这是空日期的新闻内容",
            "source": "test_source",
            "published_at": "",
            "collected_at": now.isoformat()
        })
        
        print(f"测试数据总量: {len(test_news)}")
        print("测试数据详情:")
        for news in test_news:
            status = "应该保留" if news['id'] in ['news1', 'news2', 'news5', 'news6'] else "应该被过滤"
            print(f"  - {news['title']} ({news['published_at']}) - {status}")
        
        # 测试过滤功能
        fetcher = NewsFetcher()
        filtered_news = fetcher._filter_recent_news(test_news)
        
        print(f"\n过滤后剩余: {len(filtered_news)}")
        print("过滤结果:")
        for news in filtered_news:
            print(f"  ✅ 保留: {news['title']} ({news['published_at']})")
        
        # 验证结果
        expected_kept = ['news1', 'news2', 'news5', 'news6']
        actual_kept = [news['id'] for news in filtered_news]
        
        print(f"\n验证结果:")
        print(f"期望保留: {expected_kept}")
        print(f"实际保留: {actual_kept}")
        
        # 检查是否正确
        if set(expected_kept) == set(actual_kept):
            print("✅ 测试通过！24小时过滤功能正常工作")
            return True
        else:
            print("❌ 测试失败！24小时过滤功能有问题")
            
            # 检查哪些应该保留但被过滤了
            missing = set(expected_kept) - set(actual_kept)
            if missing:
                print(f"  应该保留但被过滤的新闻: {missing}")
            
            # 检查哪些应该被过滤但保留了
            extra = set(actual_kept) - set(expected_kept)
            if extra:
                print(f"  应该被过滤但保留的新闻: {extra}")
            
            return False
    
    def test_parse_published_date(self):
        """测试日期解析功能"""
        print("\n开始测试日期解析功能...")
        
        fetcher = NewsFetcher()
        
        # 模拟feedparser的entry对象
        class MockEntry:
            def __init__(self, published):
                self.published = published
        
        test_cases = [
            ("2026-02-16T10:00:00Z", "ISO格式日期"),
            ("Mon, 16 Feb 2026 10:00:00 GMT", "RFC格式日期"),
            (None, "None日期"),
            ("", "空字符串日期")
        ]
        
        all_passed = True
        for published, description in test_cases:
            entry = MockEntry(published)
            result = fetcher._parse_published_date(entry)
            print(f"  {description}: {published} -> {result}")
            
            # 验证结果是否为ISO格式
            try:
                datetime.fromisoformat(result)
                print(f"    ✅ 解析结果是有效的ISO格式")
            except Exception as e:
                print(f"    ❌ 解析结果不是有效的ISO格式: {e}")
                all_passed = False
        
        if all_passed:
            print("✅ 日期解析功能测试通过")
        else:
            print("❌ 日期解析功能测试失败")
        
        return all_passed

if __name__ == "__main__":
    tester = TestFilter()
    
    # 运行测试
    filter_result = tester.test_filter_recent_news()
    parse_result = tester.test_parse_published_date()
    
    print(f"\n{'='*60}")
    print("测试总结:")
    print(f"24小时过滤功能: {'✅ 通过' if filter_result else '❌ 失败'}")
    print(f"日期解析功能: {'✅ 通过' if parse_result else '❌ 失败'}")
    print(f"{'='*60}")
