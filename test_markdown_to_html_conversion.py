#!/usr/bin/env python3
"""
测试 Markdown 到 HTML 的转换功能
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def read_markdown_file(file_path):
    """读取 Markdown 文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

def parse_three_layer_analysis_from_markdown(markdown_content):
    """从 Markdown 内容中解析三层分析结果"""
    try:
        # 初始化结果结构
        analysis_result = {
            "first_layer": "",
            "second_layer": [],
            "third_layer": ""
        }
        
        # 分割内容为部分
        lines = markdown_content.split('\n')
        current_section = None
        current_event = []
        
        for line in lines:
            line = line.rstrip('\n')
            
            # 识别不同部分
            if "## 第一层分析：整体摘要分析" in line:
                current_section = "first_layer"
                current_event = []
            elif "## 第二层分析：关键事件深度分析" in line:
                current_section = "second_layer"
                current_event = []
            elif "## 第三层分析：综合分析" in line:
                current_section = "third_layer"
                current_event = []
            elif current_section == "second_layer" and line.startswith("### 事件 ") and " 分析" in line:
                # 保存之前的事件（如果有）
                if current_event:
                    analysis_result["second_layer"].append('\n'.join(current_event))
                    current_event = []
            elif current_section:
                # 收集当前部分的内容
                if current_section == "second_layer":
                    current_event.append(line)
                else:
                    if current_section == "first_layer":
                        analysis_result["first_layer"] += line + '\n'
                    elif current_section == "third_layer":
                        analysis_result["third_layer"] += line + '\n'
        
        # 保存最后一个事件
        if current_section == "second_layer" and current_event:
            analysis_result["second_layer"].append('\n'.join(current_event))
        
        # 清理空白
        analysis_result["first_layer"] = analysis_result["first_layer"].strip()
        analysis_result["third_layer"] = analysis_result["third_layer"].strip()
        
        return analysis_result
        
    except Exception as e:
        print(f"解析 Markdown 失败: {e}")
        return None

def test_markdown_to_html_conversion():
    """测试 Markdown 到 HTML 的转换功能"""
    print("====================================")
    print("测试 Markdown 到 HTML 的转换功能")
    print("====================================")
    
    # 检查报告目录
    report_dir = "data/analysis/daily/reports"
    if not os.path.exists(report_dir):
        print(f"报告目录不存在: {report_dir}")
        return False
    
    # 列出 Markdown 文件
    markdown_files = [f for f in os.listdir(report_dir) if f.endswith('.md')]
    if not markdown_files:
        print("报告目录中没有 Markdown 文件")
        return False
    
    print(f"发现 {len(markdown_files)} 个 Markdown 文件:")
    for f in markdown_files:
        print(f"- {f}")
    
    # 选择第一个文件进行测试
    test_file = markdown_files[0]
    test_file_path = os.path.join(report_dir, test_file)
    print(f"\n使用文件进行测试: {test_file}")
    
    # 读取 Markdown 内容
    markdown_content = read_markdown_file(test_file_path)
    if not markdown_content:
        return False
    
    # 解析三层分析结果
    analysis_result = parse_three_layer_analysis_from_markdown(markdown_content)
    if not analysis_result:
        return False
    
    # 验证解析结果
    print("\n验证解析结果:")
    print(f"✅ 第一层分析: {'存在' if analysis_result['first_layer'] else '缺失'}")
    print(f"✅ 第二层分析事件数量: {len(analysis_result['second_layer'])}")
    print(f"✅ 第三层分析: {'存在' if analysis_result['third_layer'] else '缺失'}")
    
    if len(analysis_result['second_layer']) < 3:
        print(f"⚠️  第二层分析事件数量不足，只有 {len(analysis_result['second_layer'])} 个")
    
    # 添加必要的字段
    from datetime import datetime
    analysis_result["date"] = datetime.now().strftime('%Y-%m-%d')
    analysis_result["news_count"] = len(analysis_result['second_layer'])
    analysis_result["timestamp"] = datetime.now().isoformat()
    
    # 测试 HTML 转换
    print("\n测试 HTML 转换...")
    
    try:
        from push_manager import PushManager
        
        # 初始化推送管理器
        push_manager = PushManager()
        
        # 生成 HTML 内容
        html_content = push_manager._generate_html_content(analysis_result)
        
        if html_content:
            print("✅ HTML 转换成功")
            
            # 保存 HTML 到文件
            html_output_file = os.path.join(report_dir, f"{os.path.splitext(test_file)[0]}.html")
            with open(html_output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTML 结果已保存到: {html_output_file}")
            
            # 验证 HTML 内容
            print("\n验证 HTML 内容:")
            
            # 检查是否包含必要的部分
            required_sections = [
                "第一层分析：整体摘要分析",
                "第二层分析：关键事件深度分析",
                "第三层分析：综合分析"
            ]
            
            for section in required_sections:
                if section in html_content:
                    print(f"✅ 包含 '{section}' 部分")
                else:
                    print(f"❌ 缺少 '{section}' 部分")
                    return False
            
            # 检查事件分析部分
            event_count = len(analysis_result['second_layer'])
            for i in range(event_count):
                if f"事件 {i+1} 分析" in html_content:
                    print(f"✅ 包含 '事件 {i+1} 分析' 部分")
                else:
                    print(f"❌ 缺少 '事件 {i+1} 分析' 部分")
                    return False
            
            return True
        else:
            print("❌ HTML 转换失败，返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_legacy_format_compatibility():
    """测试对旧格式的兼容性"""
    print("\n====================================")
    print("测试对旧格式的兼容性")
    print("====================================")
    
    try:
        from push_manager import PushManager
        
        # 模拟旧格式分析结果
        legacy_analysis = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "daily_summary": "# 今日新闻总结\n\n今日共分析 10 条新闻\n\n## 主要事件\n\n### 热点关键词\n\n- 技术 (3)\n- AI (2)\n- 商业 (2)\n\n## 事件分析\n\n这里是对今日主要事件的详细分析...",
            "event_analysis": "# 事件发展脉络分析\n\n## 今日重要事件\n\n### 技术\n\n- 技术新闻1\n- 技术新闻2\n- 技术新闻3\n\n## 横向分析\n\n这里是对今日事件的横向分析...",
            "timestamp": datetime.now().isoformat(),
            "news_count": 10
        }
        
        # 初始化推送管理器
        push_manager = PushManager()
        
        # 生成 HTML 内容
        html_content = push_manager._generate_html_content(legacy_analysis)
        
        if html_content:
            print("✅ 旧格式兼容性测试成功")
            
            # 验证 HTML 内容
            if "今日新闻总结" in html_content:
                print("✅ 包含旧格式的每日摘要内容")
            if "事件发展脉络分析" in html_content:
                print("✅ 包含旧格式的事件分析内容")
            
            return True
        else:
            print("❌ 旧格式兼容性测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 兼容性测试失败: {e}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    
    # 测试 Markdown 到 HTML 转换
    markdown_test_result = test_markdown_to_html_conversion()
    
    # 测试旧格式兼容性
    legacy_test_result = test_legacy_format_compatibility()
    
    # 总结
    print("\n====================================")
    print("测试总结")
    print("====================================")
    
    if markdown_test_result and legacy_test_result:
        print("🎉 所有测试通过！")
        print("\n测试结果:")
        print("- ✅ Markdown 到 HTML 转换功能正常")
        print("- ✅ 三层分析结构解析正常")
        print("- ✅ HTML 结果保存成功")
        print("- ✅ 旧格式兼容性测试通过")
        sys.exit(0)
    else:
        print("❌ 部分测试失败！")
        sys.exit(1)
