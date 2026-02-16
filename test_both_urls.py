#!/usr/bin/env python3
"""测试两种URL格式"""

from ai_analyzer import AIAnalyzer
from config import settings

# 测试两种URL格式
def test_both_urls():
    print("测试两种URL格式...")
    
    # 保存原始URL
    original_url = settings.AI_API_URL
    print(f"原始URL: {original_url}")
    
    # 测试不带v1的URL
    print("\n=== 测试不带v1的URL ===")
    test_url_without_v1(original_url)
    
    # 测试带v1的URL
    print("\n=== 测试带v1的URL ===")
    test_url_with_v1(original_url)

# 测试不带v1的URL
def test_url_without_v1(base_url):
    print(f"测试URL: {base_url}")
    
    # 创建分析器实例
    analyzer = AIAnalyzer()
    
    # 创建API客户端
    client = analyzer.DeepSeekAPIClient(settings.AI_API_KEY, base_url)
    
    # 测试简单请求
    test_messages = [
        {
            "role": "system",
            "content": "你是一个助手"
        },
        {
            "role": "user",
            "content": "测试请求"
        }
    ]
    
    try:
        response = client.call_api(test_messages, max_tokens=50)
        print("✅ 不带v1的URL测试成功！")
        print(f"状态码: 200")
        print(f"响应ID: {response.get('id')}")
        print(f"模型: {response.get('model')}")
        return True
    except Exception as e:
        print(f"❌ 不带v1的URL测试失败: {e}")
        return False

# 测试带v1的URL
def test_url_with_v1(base_url):
    url_with_v1 = f"{base_url}/v1"
    print(f"测试URL: {url_with_v1}")
    
    # 创建分析器实例
    analyzer = AIAnalyzer()
    
    # 创建API客户端
    client = analyzer.DeepSeekAPIClient(settings.AI_API_KEY, url_with_v1)
    
    # 测试简单请求
    test_messages = [
        {
            "role": "system",
            "content": "你是一个助手"
        },
        {
            "role": "user",
            "content": "测试请求"
        }
    ]
    
    try:
        response = client.call_api(test_messages, max_tokens=50)
        print("✅ 带v1的URL测试成功！")
        print(f"状态码: 200")
        print(f"响应ID: {response.get('id')}")
        print(f"模型: {response.get('model')}")
        return True
    except Exception as e:
        print(f"❌ 带v1的URL测试失败: {e}")
        return False

if __name__ == "__main__":
    test_both_urls()
