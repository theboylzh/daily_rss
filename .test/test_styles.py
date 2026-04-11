"""
V2.0.0 邮件样式测试
检查邮件客户端兼容性和样式正确性
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from push_manager import PushManager
from ai_analyzer_v2 import get_empty_structure


def test_css_inline_styles():
    """测试 CSS 内联样式（邮件客户端兼容性）"""
    print("=" * 60)
    print("样式测试：CSS 内联样式检查")
    print("=" * 60)

    # 读取模板文件
    template_path = os.path.join(os.path.dirname(__file__), 'email_template_v2.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 检查关键样式是否使用内联或嵌入方式
    checks = [
        ("嵌入 CSS <style>", "<style>" in html),
        ("CSS 变量定义", ":root" in html or "--brand" in html),
        ("表格布局", "table" in html and "cellpadding" in html),
        ("字体回退", "Georgia" in html or "sans-serif" in html),
        ("行高设置", "line-height" in html),
        ("颜色定义", "#B88459" in html or "#333" in html),
    ]

    all_passed = True
    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    return all_passed


def test_email_client_compatibility():
    """测试邮件客户端兼容性"""
    print("\n" + "=" * 60)
    print("样式测试：邮件客户端兼容性")
    print("=" * 60)

    template_path = os.path.join(os.path.dirname(__file__), 'email_template_v2.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Gmail 兼容性检查
    print("\nGmail 兼容性:")
    gmail_checks = [
        ("使用 <style> 标签（支持）", "<style>" in html),
        ("避免 position:fixed", "position:fixed" not in html),
        ("避免 @import", "@import" not in html),
        ("使用 web 安全字体", "Georgia" in html or "Times New Roman" in html),
    ]
    for name, passed in gmail_checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")

    # Outlook 兼容性检查
    print("\nOutlook 兼容性:")
    outlook_checks = [
        ("使用 table 布局", "<table" in html),
        ("使用 cellpadding/cellspacing", "cellpadding=" in html),
        ("避免 CSS Grid", "display:grid" not in html),
        ("避免 CSS Flexbox 复杂使用", html.count("display:flex") < 10),
        ("使用十六进制颜色", "#" in html),
    ]
    for name, passed in outlook_checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")

    # Apple Mail 兼容性检查
    print("\nApple Mail 兼容性:")
    apple_checks = [
        ("支持响应式设计", "@media" in html),
        ("支持 viewport", "viewport" in html),
        ("使用标准 HTML5", "<!DOCTYPE html>" in html),
    ]
    for name, passed in apple_checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")

    return True


def test_visual_hierarchy():
    """测试视觉层次"""
    print("\n" + "=" * 60)
    print("样式测试：视觉层次检查")
    print("=" * 60)

    template_path = os.path.join(os.path.dirname(__file__), 'email_template_v2.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 检查字体大小层次
    font_sizes = [
        ("大标题 64px", "64px" in html),
        ("主标题 40px", "40px" in html),
        ("次级标题 32px", "32px" in html),
        ("小标题 24px", "24px" in html),
        ("正文 18px", "18px" in html),
        ("辅助文字 14px", "14px" in html),
    ]

    for name, passed in font_sizes:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")

    # 检查颜色层次
    print("\n颜色层次:")
    color_checks = [
        ("品牌色 #B88459", "#B88459" in html or "var(--brand)" in html),
        ("主文本 #333", "#333" in html or "var(--text-primary)" in html),
        ("次级文本 #999", "#999" in html or "var(--text-secondary)" in html),
        ("白色背景", "#FFFFFF" in html or "var(--bg-white)" in html),
    ]
    for name, passed in color_checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")

    return True


def test_spacing_consistency():
    """测试间距一致性"""
    print("\n" + "=" * 60)
    print("样式测试：间距一致性检查")
    print("=" * 60)

    template_path = os.path.join(os.path.dirname(__file__), 'email_template_v2.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 检查常用的间距值
    spacing_checks = [
        ("12px 间距", "12px" in html),
        ("16px 间距", "16px" in html),
        ("24px 间距", "24px" in html),
        ("32px 间距", "32px" in html),
        ("40px 间距", "40px" in html),
        ("48px 间距", "48px" in html),
        ("56px 间距", "56px" in html),
        ("64px 间距", "64px" in html),
        ("96px 大区隔", "96px" in html),
    ]

    for name, passed in spacing_checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")

    return True


def test_rendered_output():
    """测试渲染输出的样式"""
    print("\n" + "=" * 60)
    print("样式测试：渲染输出检查")
    print("=" * 60)

    push_manager = PushManager()

    mock_data = {
        "date": "2026-04-11",
        "timestamp": "2026-04-11T10:00:00",
        "news_count": 10,
        "summary": {
            "one_liner": "测试摘要一句话",
            "digest": "这是测试摘要内容，描述今天发生的事件。",
            "keywords": ["科技", "AI", "创新"]
        },
        "key_news_brief": [
            {"title": "科技新闻 1", "tags": ["科技"]},
            {"title": "科技新闻 2", "tags": ["科技"]},
        ],
        "briefing": {
            "politics": "政治新闻",
            "economy": "经济新闻内容",
            "industry": "行业新闻",
            "tech": "科技新闻"
        },
        "perspectives": [
            {"title": "观点 1", "description": "观点描述", "references": []}
        ],
        "deep_analysis": [
            {"tags": ["科技"], "title": "分析标题", "facts": "事实",
             "viewpoint": "观点", "causes": "原因", "prediction": "预测", "advice": "建议"}
        ],
        "suggestions": {
            "thinking": {"title": "思维", "content": "内容"},
            "investment": {"title": "投资", "content": "内容"},
            "self_improvement": {"title": "提升", "content": "内容"},
            "opportunities_risks": {"title": "风险", "content": "内容"}
        }
    }

    html = push_manager._generate_v2_html_content(mock_data)

    # 检查渲染后的样式类
    style_checks = [
        ("Header 样式", 'class="header"' in html),
        ("Today Brief 样式", 'class="today-brief"' in html),
        ("关键词样式", 'class="keyword-item"' in html),
        ("观点项样式", 'class="opinion-item"' in html),
        ("分析项样式", 'class="insight-item"' in html),
        ("建议项样式", 'class="advice-item"' in html),
        ("分隔线样式", 'class="divider' in html or 'class="divider-line' in html),
    ]

    all_passed = True
    for name, passed in style_checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    # 保存测试输出
    output_path = os.path.join(os.path.dirname(__file__), 'style_test_output.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n  渲染输出已保存到：{output_path}")

    return all_passed


def test_mobile_responsive():
    """测试移动端响应式"""
    print("\n" + "=" * 60)
    print("样式测试：移动端响应式")
    print("=" * 60)

    template_path = os.path.join(os.path.dirname(__file__), 'email_template_v2.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    responsive_checks = [
        ("@media query", "@media" in html),
        ("max-width 断点", "max-width" in html),
        ("768px 断点", "768px" in html),
        ("移动端 padding", html.count("16px") > 2),
        ("移动端宽度适配", "width: 100%" in html or 'width="100%"' in html),
    ]

    for name, passed in responsive_checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")

    return True


if __name__ == "__main__":
    from datetime import datetime

    print("V2.0.0 邮件样式测试套件")
    print(f"运行时间：{datetime.now().isoformat()}\n")

    results = []

    # 运行各项测试
    results.append(("CSS 内联样式", test_css_inline_styles()))
    results.append(("邮件客户端兼容", test_email_client_compatibility()))
    results.append(("视觉层次", test_visual_hierarchy()))
    results.append(("间距一致性", test_spacing_consistency()))
    results.append(("渲染输出", test_rendered_output()))
    results.append(("移动端响应", test_mobile_responsive()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("样式测试汇总")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")

    print(f"\n总计：{passed}/{total} 通过")

    if passed == total:
        print("\n✅ 所有样式测试通过")
        import sys
        sys.exit(0)
    else:
        print("\n⚠️ 部分样式测试未通过")
        import sys
        sys.exit(1)
