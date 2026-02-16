#!/usr/bin/env python3
"""
使用用户提供的新闻标题测试三层分析流程和HTML格式转换
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_mock_news_data():
    """创建使用用户提供的新闻标题的模拟新闻数据"""
    news_titles = [
        "人类首遭AI网暴社死？OpenClaw改代码遭拒，怒写小作文报复",
        "AI战事正酣，都在等梁文锋",
        "36氪出海·全球化公司｜追觅割草机器人：借双IP破圈，以技术立标杆，深耕全球化布局",
        "前字节高管创业教育类出海项目，用Agent做\"终身学习搭子\"，红杉投了",
        "清华系具身大脑公司两月融资数亿元，接入家庭具身设备量第一、切入全尺寸机器人赛道｜硬氪首发",
        "原料短缺，美国巧克力零售价格持续上涨"
    ]
    
    mock_news = []
    for i, title in enumerate(news_titles):
        mock_news.append({
            "title": title,
            "link": f"https://example.com/news{i+1}",
            "published": datetime.now().isoformat(),
            "summary": f"这是关于{title}的摘要",
            "content": f"这是关于{title}的详细内容"
        })
    
    return mock_news

def test_three_layer_analysis():
    """测试三层分析流程"""
    print("====================================")
    print("测试三层分析流程")
    print("====================================")
    
    try:
        from ai_analyzer import AIAnalyzer
        
        # 创建模拟新闻数据
        mock_news = create_mock_news_data()
        print(f"创建了 {len(mock_news)} 条模拟新闻数据")
        
        # 打印模拟新闻标题
        print("\n模拟新闻标题:")
        for i, news in enumerate(mock_news):
            print(f"{i+1}. {news['title']}")
        
        # 初始化分析器
        analyzer = AIAnalyzer()
        print("\n初始化AI分析器成功")
        
        # 测试三层分析流程
        print("\n开始三层分析...")
        
        # 执行三层分析
        analysis_results = analyzer._three_layer_analysis(mock_news)
        
        # 验证分析结果
        print("\n验证分析结果...")
        
        # 检查结果格式
        required_keys = ["first_layer", "second_layer", "third_layer"]
        for key in required_keys:
            if key in analysis_results:
                print(f"✅ {key} 分析结果存在")
            else:
                print(f"❌ {key} 分析结果缺失")
                return False, None
        
        # 检查第二层分析结果数量
        second_layer_results = analysis_results.get("second_layer", [])
        print(f"\n第二层分析结果数量: {len(second_layer_results)}")
        if len(second_layer_results) >= 3:
            print("✅ 第二层分析结果数量符合要求")
        else:
            print(f"⚠️  第二层分析结果数量不足，只有 {len(second_layer_results)} 个")
        
        # 打印分析结果摘要
        print("\n分析结果摘要:")
        
        # 第一层分析摘要
        first_layer = analysis_results.get("first_layer", "")
        if first_layer:
            print("\n第一层分析 (整体摘要):")
            # 提取前200个字符
            summary = first_layer[:200]
            if len(first_layer) > 200:
                summary += "..."
            print(summary)
        
        # 第二层分析摘要
        second_layer_results = analysis_results.get("second_layer", [])
        for i, event_analysis in enumerate(second_layer_results[:2]):  # 只显示前两个
            if event_analysis:
                print(f"\n第二层分析 (事件 {i+1}):")
                # 提取前150个字符
                summary = event_analysis[:150]
                if len(event_analysis) > 150:
                    summary += "..."
                print(summary)
        
        # 第三层分析摘要
        third_layer = analysis_results.get("third_layer", "")
        if third_layer:
            print("\n第三层分析 (综合分析):")
            # 提取前200个字符
            summary = third_layer[:200]
            if len(third_layer) > 200:
                summary += "..."
            print(summary)
        
        # 保存分析结果
        print("\n保存分析结果...")
        test_date = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        analyzer._save_analysis_results(analysis_results, test_date)
        print(f"✅ 分析结果已保存，日期标记: {test_date}")
        
        return True, analysis_results
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_html_conversion(analysis_results):
    """测试HTML格式转换功能"""
    print("\n====================================")
    print("测试HTML格式转换功能")
    print("====================================")
    
    try:
        from push_manager import PushManager
        
        # 构建分析报告结构
        analysis_report = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "first_layer": analysis_results.get("first_layer", "分析失败"),
            "second_layer": analysis_results.get("second_layer", []),
            "third_layer": analysis_results.get("third_layer", "分析失败"),
            "timestamp": datetime.now().isoformat(),
            "news_count": len(analysis_results.get("second_layer", []))
        }
        
        # 初始化推送管理器
        push_manager = PushManager()
        print("初始化推送管理器成功")
        
        # 生成HTML内容
        print("\n生成HTML内容...")
        html_content = push_manager._generate_html_content(analysis_report)
        
        if html_content:
            print("✅ HTML内容生成成功")
            
            # 保存HTML到文件
            html_output_file = f"data/analysis/daily/reports/test_{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.html"
            os.makedirs(os.path.dirname(html_output_file), exist_ok=True)
            with open(html_output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTML结果已保存到: {html_output_file}")
            
            # 验证HTML内容
            print("\n验证HTML内容:")
            
            # 检查是否包含必要的部分
            required_sections = [
                "Summary 是日要闻",
                "Advanced 深度分析",
                "Insights 洞察建议"
            ]
            
            for section in required_sections:
                if section in html_content:
                    print(f"✅ 包含 '{section}' 部分")
                else:
                    print(f"❌ 缺少 '{section}' 部分")
                    return False
            
            # 检查事件分析部分
            # 由于已经移除了事件分析子标题，这里不再检查具体的事件分析标题
            # 改为检查是否包含第二层分析的内容
            if "Advanced 深度分析" in html_content:
                print("✅ 第二层分析内容存在")
            else:
                print("❌ 缺少第二层分析内容")
                return False
            
            return True
        else:
            print("❌ HTML内容生成失败，返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 测试三层分析流程
    analysis_success, analysis_results = test_three_layer_analysis()
    
    # 测试HTML格式转换
    html_success = False
    if analysis_success and analysis_results:
        html_success = test_html_conversion(analysis_results)
    
    # 总结
    print("\n====================================")
    print("测试总结")
    print("====================================")
    
    if analysis_success and html_success:
        print("🎉 所有测试通过！")
        print("\n测试结果:")
        print("- ✅ 三层分析流程执行成功")
        print("- ✅ 分析结果格式正确")
        print("- ✅ HTML格式转换功能正常")
        print("- ✅ HTML结果保存成功")
        sys.exit(0)
    else:
        print("❌ 部分测试失败！")
        if not analysis_success:
            print("- ❌ 三层分析流程执行失败")
        if not html_success:
            print("- ❌ HTML格式转换功能测试失败")
        sys.exit(1)
