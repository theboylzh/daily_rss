"""
手动测试 V2 AI 分析流程
"""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from ai_analyzer_v2 import AIAnalyzerV2, validate_v2_structure

# 加载新闻数据
with open('../data/news/2026-02-26.json', 'r', encoding='utf-8') as f:
    news_items = json.load(f)

print(f"加载了 {len(news_items)} 条新闻")
print(f"第一条：{news_items[0].get('title', '无标题')[:50]}...")
print()

# 创建分析器
analyzer = AIAnalyzerV2()

# 运行完整分析
print("=" * 60)
print("开始 V2 四层分析...")
print("=" * 60)

result = analyzer.analyze_daily_news_v2(news_items)

# 打印结果摘要
print("\n" + "=" * 60)
print("分析完成！结果摘要:")
print("=" * 60)

print(f"\n【一句话总结】")
print(result.get('summary', {}).get('one_liner', '缺失'))

print(f"\n【关键词】")
print(result.get('summary', {}).get('keywords', []))

print(f"\n【重点新闻 (3 条)】")
for i, news in enumerate(result.get('key_news_brief', [])[:3], 1):
    print(f"  {i}. {news.get('title', '无标题')}")

print(f"\n【观点 (3 个)】")
for i, p in enumerate(result.get('perspectives', [])[:3], 1):
    print(f"  {i}. {p.get('title', '无标题')}")

print(f"\n【深度分析 (3 个)】")
for i, a in enumerate(result.get('deep_analysis', [])[:3], 1):
    print(f"  {i}. [{a.get('tags', [])}] {a.get('title', '无标题')}")

print(f"\n【建议】")
suggestions = result.get('suggestions', {})
print(f"  思维启发：{suggestions.get('thinking', {}).get('title', '缺失')}")
print(f"  投资建议：{suggestions.get('investment', {}).get('title', '缺失')}")
print(f"  个人提升：{suggestions.get('self_improvement', {}).get('title', '缺失')}")
print(f"  机遇风险：{suggestions.get('opportunities_risks', {}).get('title', '缺失')}")

# 保存结果
output_file = '../test_v2_result.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\n完整结果已保存到：{output_file}")

# 验证结构
from ai_analyzer_v2 import AIAnalyzerV2, validate_v2_structure
is_valid, errors = validate_v2_structure(result)
if is_valid:
    print("\n✅ 数据结构验证通过")
else:
    print(f"\n❌ 数据结构验证失败：{errors}")
