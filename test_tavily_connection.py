#!/usr/bin/env python3
"""
测试Tavily连接和搜索功能
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tavily_connection():
    """测试Tavily连接"""
    print("开始测试Tavily连接...")
    
    # 检查API密钥是否配置
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        print("❌ Tavily API密钥未配置")
        return False
    
    print(f"✅ Tavily API密钥已配置: {api_key[:10]}...")
    
    # 尝试初始化Tavily客户端
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        print("✅ Tavily客户端初始化成功")
        
        # 尝试执行一个简单的搜索
        test_query = "人工智能最新发展"
        print(f"\n尝试搜索: {test_query}")
        
        results = client.search(
            query=test_query,
            max_results=2,
            search_depth="basic"
        )
        
        print("✅ Tavily搜索成功")
        print(f"获得 {len(results.get('results', []))} 个结果")
        
        # 打印搜索结果
        if results.get('results'):
            print("\n搜索结果:")
            for i, result in enumerate(results['results'][:2]):
                print(f"\n{i+1}. {result.get('title')}")
                print(f"   URL: {result.get('url')}")
                if result.get('content'):
                    print(f"   摘要: {result.get('content')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Tavily连接失败: {e}")
        return False

def test_ai_analyzer_tavily_integration():
    """测试AI分析器中的Tavily集成"""
    print("\n开始测试AI分析器中的Tavily集成...")
    
    try:
        from ai_analyzer import AIAnalyzer
        
        # 初始化分析器
        analyzer = AIAnalyzer()
        
        # 测试Tavily客户端是否初始化成功
        if analyzer.tavily_client:
            print("✅ AI分析器中Tavily客户端初始化成功")
            
            # 测试搜索功能
            test_query = "科技新闻"
            search_results = analyzer._search_with_tavily(test_query, max_results=1)
            
            if search_results:
                print("✅ AI分析器中Tavily搜索功能正常")
                print(f"获得 {len(search_results)} 个搜索结果")
            else:
                print("⚠️  AI分析器中Tavily搜索未返回结果")
        else:
            print("❌ AI分析器中Tavily客户端初始化失败")
            
    except Exception as e:
        print(f"❌ 测试AI分析器Tavily集成失败: {e}")

if __name__ == "__main__":
    print("====================================")
    print("Tavily连接测试")
    print("====================================")
    
    # 测试直接连接
    direct_test_result = test_tavily_connection()
    
    # 测试AI分析器集成
    test_ai_analyzer_tavily_integration()
    
    print("\n====================================")
    print("测试完成")
    print("====================================")
    
    if direct_test_result:
        print("🎉 Tavily连接测试通过！")
        sys.exit(0)
    else:
        print("❌ Tavily连接测试失败！")
        sys.exit(1)
