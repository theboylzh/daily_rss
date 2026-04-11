"""
手动测试步骤 3：邮件渲染测试
"""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from push_manager import PushManager

# 加载 V2 分析结果
with open('../test_v2_result.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

# 添加日期信息
analysis['date'] = datetime.now().strftime('%Y-%m-%d')
analysis['timestamp'] = datetime.now().isoformat()
analysis['news_count'] = len(analysis.get('key_news_brief', [])) + 3  # 估算

print("=" * 60)
print("步骤 3：邮件渲染测试")
print("=" * 60)

# 创建推送管理器
push_manager = PushManager()

# 渲染邮件
print("\n开始渲染邮件 HTML...")
html = push_manager._generate_v2_html_content(analysis)

print(f"渲染成功！HTML 大小：{len(html)} 字节")

# 保存渲染结果
output_file = 'test_email_v2_output.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n邮件 HTML 已保存到：{output_file}")
print("\n=== 请在浏览器中打开此文件查看渲染效果 ===")
print(f"命令：open {output_file}")

# 简单检查
print("\n=== 渲染内容检查 ===")
checks = [
    ("Header", '<header class="header">' in html or 'class="header"' in html),
    ("Today Brief", 'class="today-brief"' in html),
    ("关键词", 'class="keyword-item"' in html),
    ("观点板块", 'class="opinion-item"' in html),
    ("分析板块", 'class="insight-item"' in html),
    ("建议板块", 'class="advice-item"' in html),
]

for name, passed in checks:
    status = "✓" if passed else "✗"
    print(f"  {status} {name}")

print("\n下一步：在浏览器中打开 HTML 文件，检查视觉效果")
