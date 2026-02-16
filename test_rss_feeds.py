#!/usr/bin/env python3
import requests
import feedparser
import ssl
import time
from datetime import datetime

# 测试的RSS源
TEST_FEEDS = [
    "https://www.ifanr.com/feed",
    "https://moonvy.com/blog/rss.xml",
    "http://rss1.smashingmagazine.com/feed/",
    "https://quail.ink/dingyi/feed/atom"
]

def test_rss_feed(url):
    """测试单个RSS源"""
    print(f"\n{'='*80}")
    print(f"测试RSS源: {url}")
    print(f"测试时间: {datetime.now().isoformat()}")
    print(f"{'='*80}")
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # 1. 测试使用requests获取内容
        print("\n1. 使用requests获取内容...")
        response = requests.get(url, timeout=30, verify=False, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        # 检查编码
        print(f"原始编码: {response.encoding}")
        print(f"推测编码: {response.apparent_encoding}")
        
        # 明确指定编码
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding
        print(f"使用编码: {response.encoding}")
        
        # 输出响应内容前1000字符
        print("\n2. 响应内容前1000字符:")
        print(response.text[:1000])
        print("...")
        
        # 2. 测试使用feedparser直接解析URL
        print("\n3. 使用feedparser直接解析URL...")
        feed1 = feedparser.parse(url)
        print(f"feed1 状态: {feed1.get('status', 'N/A')}")
        print(f"feed1 条目数: {len(feed1.entries)}")
        if 'bozo_exception' in feed1:
            print(f"feed1 错误: {type(feed1['bozo_exception']).__name__}: {feed1['bozo_exception']}")
        
        # 3. 测试使用feedparser解析响应内容
        print("\n4. 使用feedparser解析响应内容...")
        feed2 = feedparser.parse(response.text)
        print(f"feed2 状态: {feed2.get('status', 'N/A')}")
        print(f"feed2 条目数: {len(feed2.entries)}")
        if 'bozo_exception' in feed2:
            print(f"feed2 错误: {type(feed2['bozo_exception']).__name__}: {feed2['bozo_exception']}")
        
        # 4. 尝试不同的解析方法
        print("\n5. 尝试其他解析方法...")
        
        # 尝试去除可能的BOM
        content = response.text
        if content.startswith('\ufeff'):
            content = content[1:]
            print("去除了BOM标记")
        
        # 再次解析
        feed3 = feedparser.parse(content)
        print(f"feed3 条目数: {len(feed3.entries)}")
        if 'bozo_exception' in feed3:
            print(f"feed3 错误: {type(feed3['bozo_exception']).__name__}: {feed3['bozo_exception']}")
        
        # 5. 分析feed结构
        print("\n6. 分析feed结构...")
        if feed2.entries:
            print("找到条目，第一个条目的结构:")
            first_entry = feed2.entries[0]
            print(f"标题: {first_entry.get('title', 'N/A')}")
            print(f"链接: {first_entry.get('link', 'N/A')}")
            print(f"发布时间: {first_entry.get('published', 'N/A')}")
            print(f"摘要: {first_entry.get('summary', 'N/A')[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("开始测试RSS源...")
    print(f"测试时间: {datetime.now().isoformat()}")
    print(f"共测试 {len(TEST_FEEDS)} 个RSS源")
    
    results = []
    for feed_url in TEST_FEEDS:
        success = test_rss_feed(feed_url)
        results.append((feed_url, success))
        # 避免请求过快
        time.sleep(2)
    
    print(f"\n{'='*80}")
    print("测试结果汇总:")
    print(f"{'='*80}")
    for feed_url, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status}: {feed_url}")
    print(f"{'='*80}")
