#!/usr/bin/env python3
"""
Tavily 搜索结果调试工具
用于测试不同搜索关键词并查看详细结果
"""
import os
from ai_analyzer import AIAnalyzer

def debug_tavily_search():
    """调试 Tavily 搜索功能"""
    print("=====================================")
    print("Tavily 搜索结果调试工具")
    print("=====================================")
    
    # 初始化 AI 分析器
    analyzer = AIAnalyzer()
    
    # 检查 Tavily 客户端是否初始化成功
    if not analyzer.tavily_client:
        print("❌ Tavily 客户端初始化失败，请检查 API 密钥配置")
        return
    
    print("✅ Tavily 客户端初始化成功")
    
    # 测试几个预设的搜索关键词
    test_keywords = [
        "AI网暴事件 OpenClaw",
        "清华系具身大脑公司融资",
        "追觅科技割草机器人全球化"
    ]
    
    for keyword in test_keywords:
        print("\n" + "="*50)
        print(f"测试搜索关键词: {keyword}")
        
        # 生成优化后的搜索查询词
        optimized_query = analyzer._generate_search_query(keyword)
        print(f"优化后的搜索查询词: {optimized_query}")
        
        # 执行搜索
        print("\n执行搜索中...")
        results = analyzer._search_with_tavily(optimized_query, max_results=5)
        
        # 显示搜索结果
        print(f"\n搜索完成，共获得 {len(results)} 个结果:")
        print("-"*80)
        
        for i, result in enumerate(results):
            print(f"\n结果 {i+1}:")
            print(f"标题: {result.get('title', '无标题')}")
            print(f"URL: {result.get('url', '无URL')}")
            content = result.get('content', '无内容')
            print(f"内容: {content[:300]}..." if content else "内容: 无内容")
            print("-"*80)

if __name__ == "__main__":
    debug_tavily_search()
