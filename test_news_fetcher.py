#!/usr/bin/env python3
"""测试新闻抓取功能"""

from news_fetcher import NewsFetcher

# 测试新闻抓取
def test_news_fetcher():
    print("测试新闻抓取功能...")
    
    # 创建新闻抓取器实例
    fetcher = NewsFetcher()
    
    # 获取最近1天的新闻
    print("获取最近1天的新闻...")
    news_items = fetcher.get_recent_news(days=1)
    
    print(f"成功抓取 {len(news_items)} 条新闻")
    
    # 打印前5条新闻标题
    if news_items:
        print("\n前5条新闻标题：")
        for i, news in enumerate(news_items[:5]):
            print(f"{i+1}. {news['title']}")
    else:
        print("未抓取到任何新闻")

if __name__ == "__main__":
    test_news_fetcher()
