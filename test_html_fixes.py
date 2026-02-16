import json
from push_manager import PushManager

# 测试所有HTML修复
def test_all_fixes():
    # 加载分析数据
    with open('data/analysis/daily/2026-02-16.json', 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # 创建PushManager实例
    push_manager = PushManager()
    
    # 生成HTML内容
    html_content = push_manager._generate_html_content(analysis_data)
    
    # 检查HTML是否包含所有修复
    print("检查HTML修复...")
    
    # 1. 检查页面标题
    if "<h1>Daily RSS</h1>" in html_content:
        print("✓ 页面标题已改为 'Daily RSS'")
    else:
        print("✗ 页面标题修改失败")
    
    # 2. 检查标题层级
    if "<h1>Summary 是日要闻</h1>" in html_content:
        print("✓ Summary 使用一级标题")
    else:
        print("✗ Summary 标题层级错误")
    
    if "<h1>Advanced 深度分析</h1>" in html_content:
        print("✓ Advanced 使用一级标题")
    else:
        print("✗ Advanced 标题层级错误")
    
    if "<h1>Insights 洞察建议</h1>" in html_content:
        print("✓ Insights 使用一级标题")
    else:
        print("✗ Insights 标题层级错误")
    
    if "<h1>News 新闻列表</h1>" in html_content:
        print("✓ News 使用一级标题")
    else:
        print("✗ News 标题层级错误")
    
    # 3. 检查第二层分析是否移除了事件标题
    if "事件 1 分析" not in html_content:
        print("✓ 第二层分析已移除事件标题")
    else:
        print("✗ 第二层分析仍包含事件标题")
    
    # 4. 检查日期和新闻数量是否正确显示
    if analysis_data['date'] in html_content:
        print("✓ 日期显示正确")
    else:
        print("✗ 日期显示错误")
    
    if str(analysis_data['news_count']) in html_content:
        print("✓ 新闻数量显示正确")
    else:
        print("✗ 新闻数量显示错误")
    
    # 5. 检查AI分析内容是否存在
    if "今日摘要" in html_content:
        print("✓ 第一层分析内容已包含")
    else:
        print("✗ 第一层分析内容缺失")
    
    if "全球最大镍矿" in html_content:
        print("✓ 第二层分析内容已包含")
    else:
        print("✗ 第二层分析内容缺失")
    
    if "思维启发" in html_content:
        print("✓ 第三层分析内容已包含")
    else:
        print("✗ 第三层分析内容缺失")
    
    # 保存生成的HTML到文件，方便查看
    with open('test_fixes_output.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\nHTML内容已保存到 test_fixes_output.html，请打开查看完整内容")

if __name__ == "__main__":
    test_all_fixes()
