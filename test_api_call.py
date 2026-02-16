#!/usr/bin/env python3
"""测试API调用"""

import sys
from ai_analyzer import AIAnalyzer
from config import settings

# 测试API调用
def test_api_call():
    print("测试API调用...")
    print(f"API URL: {settings.AI_API_URL}")
    print(f"API Key: {settings.AI_API_KEY[:10]}...")
    print(f"Model: {settings.AI_MODEL}")
    
    # 创建分析器实例
    analyzer = AIAnalyzer()
    
    # 创建API客户端
    client = analyzer.DeepSeekAPIClient(settings.AI_API_KEY, settings.AI_API_URL)
    print(f"客户端API URL: {client.api_url}")
    
    # 测试简单请求
    print("\n发送测试请求...")
    
    test_messages = [
        {
            "role": "system",
            "content": "你是一个助手"
        },
        {
            "role": "user",
            "content": "你好，测试请求"
        }
    ]
    
    try:
        response = client.call_api(test_messages, max_tokens=50)
        print("✅ API调用成功！")
        print(f"状态码: 200")
        print(f"响应ID: {response.get('id')}")
        print(f"模型: {response.get('model')}")
        
        # 提取内容
        content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f"回复: {content}")
        
        return True
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return False

if __name__ == "__main__":
    success = test_api_call()
    sys.exit(0 if success else 1)
