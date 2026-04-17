"""
AI 提示词快速调试工具
修改提示词后，用这个工具快速验证效果
"""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import httpx
from config import settings
from ai_analyzer_v2 import AIAnalyzerV2, parse_ai_json_response


def test_stage1_prompt():
    """快速测试阶段 1 提示词"""
    print("=" * 60)
    print("阶段 1 提示词快速测试")
    print("=" * 60)

    # 加载少量新闻
    news_file = 'data/news/2026-02-26.json'
    if not os.path.exists(news_file):
        print("❌ 新闻文件不存在")
        return

    with open(news_file, 'r', encoding='utf-8') as f:
        news_items = json.load(f)[:10]  # 只取 10 条

    # 从 ai_analyzer_v2.py 读取提示词
    from ai_analyzer_v2 import AIAnalyzerV2
    analyzer = AIAnalyzerV2()

    # 准备 prompt
    news_text = analyzer._format_news_for_prompt(news_items)
    prompt = analyzer.prompts["stage1_summary"] + "\n\n新闻列表:\n" + news_text

    print(f"\n新闻数量：{len(news_items)}")
    print(f"Prompt 长度：{len(prompt)} 字符")
    print(f"模型：{settings.AI_MODEL}")
    print(f"API URL: {settings.AI_API_URL}")

    # 调用 AI
    print("\n发送请求...")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.AI_API_KEY}"
    }

    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个专业的新闻分析师"},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "max_tokens": 4096
    }

    try:
        with httpx.Client(trust_env=False) as client:
            response = client.post(
                settings.AI_API_URL,
                headers=headers,
                json=payload,
                timeout=settings.THIRD_LAYER_TIMEOUT
            )

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            print(f"AI 响应长度：{len(content)}")

            # 解析并显示结果
            result = parse_ai_json_response(content)

            print("\n=== 结果 ===")
            print(f"one_liner: {result.get('summary', {}).get('one_liner', '缺失')}")
            print(f"digest: {result.get('summary', {}).get('digest', '缺失')[:80]}...")
            print(f"keywords: {result.get('summary', {}).get('keywords', [])}")

            # 保存完整结果
            with open('debug_stage1_result.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("\n完整结果已保存到：debug_stage1_result.json")

            # 显示原始 AI 输出（前 1000 字符）
            print("\n=== 原始 AI 输出（前 1000 字符）===")
            print(content[:1000])

        else:
            print(f"❌ API 请求失败：{response.status_code}")

    except Exception as e:
        print(f"❌ 请求失败：{e}")


if __name__ == "__main__":
    test_stage1_prompt()
