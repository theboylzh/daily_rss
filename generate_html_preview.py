import json
import os
from push_manager import PushManager

"""
基于已有的新闻和AI分析生成HTML预览

此脚本会加载最新的分析数据，生成HTML内容，并保存到文件中，方便在浏览器中预览
"""

def generate_html_preview(date=None):
    """
    生成HTML预览
    
    Args:
        date (str): 日期，格式为 'YYYY-MM-DD'，默认为今天
    """
    # 如果没有指定日期，使用今天的日期
    if date is None:
        from datetime import datetime
        date = datetime.now().strftime('%Y-%m-%d')
    
    # 分析数据文件路径
    analysis_file = os.path.join('data', 'analysis', 'daily', f'{date}.json')
    
    # 检查文件是否存在
    if not os.path.exists(analysis_file):
        print(f"错误：分析数据文件不存在: {analysis_file}")
        print("请先运行完整的工作流程生成分析数据")
        return False
    
    # 加载分析数据
    print(f"加载分析数据: {analysis_file}")
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # 创建PushManager实例
    push_manager = PushManager()
    
    # 生成HTML内容
    print("生成HTML内容...")
    html_content = push_manager._generate_html_content(analysis_data)
    
    # 保存HTML到文件
    output_file = f'preview_{date}.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nHTML预览已生成:")
    print(f"文件路径: {os.path.abspath(output_file)}")
    print(f"\n请在浏览器中打开此文件查看预览")
    print(f"例如：在终端中运行: open {output_file}")
    
    return True

def list_available_analysis():
    """
    列出可用的分析数据文件
    """
    analysis_dir = os.path.join('data', 'analysis', 'daily')
    
    if not os.path.exists(analysis_dir):
        print(f"错误：分析数据目录不存在: {analysis_dir}")
        return []
    
    # 获取所有JSON文件
    json_files = [f for f in os.listdir(analysis_dir) if f.endswith('.json')]
    
    if not json_files:
        print("没有找到分析数据文件")
        return []
    
    print("可用的分析数据文件:")
    for file in sorted(json_files, reverse=True):  # 按日期倒序显示
        date = file[:-5]  # 移除 .json 后缀
        print(f"- {date}")
    
    return json_files

if __name__ == "__main__":
    print("基于已有的新闻和AI分析生成HTML预览")
    print("=" * 60)
    
    # 列出可用的分析数据
    available_files = list_available_analysis()
    
    if available_files:
        # 询问用户是否使用最新的分析数据
        print("\n使用最新的分析数据生成预览？(y/n)")
        use_latest = input().strip().lower()
        
        if use_latest == 'y':
            # 使用最新的日期
            latest_file = sorted(available_files, reverse=True)[0]
            latest_date = latest_file[:-5]
            print(f"\n使用日期: {latest_date}")
            generate_html_preview(latest_date)
        else:
            # 让用户输入日期
            print("\n请输入要使用的日期 (格式: YYYY-MM-DD):")
            date_input = input().strip()
            generate_html_preview(date_input)
    else:
        print("\n请先运行完整的工作流程生成分析数据:")
        print("python3 main.py")
