#!/usr/bin/env python3
"""
测试HTML生成功能
"""
import json
from push_manager import PushManager

# 读取分析结果
with open('data/analysis/daily/2026-02-16.json', 'r', encoding='utf-8') as f:
    analysis_result = json.load(f)

# 创建PushManager实例
push_manager = PushManager()

# 生成HTML内容
html_content = push_manager._generate_html_content(analysis_result)

# 保存HTML文件
with open('data/analysis/daily/test_html_output.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML文件生成成功: data/analysis/daily/test_html_output.html")
print("\nHTML结构分析:")

# 分析HTML结构
if 'Summary 是日要闻' in html_content:
    print("✅ 第一层分析部分存在")
else:
    print("❌ 第一层分析部分缺失")

if 'Advanced 深度分析' in html_content:
    print("✅ 第二层分析部分存在")
else:
    print("❌ 第二层分析部分缺失")

if 'Insights 洞察建议' in html_content:
    print("✅ 第三层分析部分存在")
else:
    print("❌ 第三层分析部分缺失")

# 检查事件分析数量
if '<h3>事件 1 分析</h3>' in html_content:
    print("✅ 事件1分析存在")
else:
    print("❌ 事件1分析缺失")

if '<h3>事件 2 分析</h3>' in html_content:
    print("✅ 事件2分析存在")
else:
    print("❌ 事件2分析缺失")

if '<h3>事件 3 分析</h3>' in html_content:
    print("✅ 事件3分析存在")
else:
    print("❌ 事件3分析缺失")
