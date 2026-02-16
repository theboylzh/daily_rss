from push_manager import PushManager

# 测试模板字符串缩进
def test_template_indent():
    # 创建PushManager实例
    push_manager = PushManager()
    
    # 获取模板字符串
    html = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>每日新闻分析报告</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 0;
                }
                .container {
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 30px;
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    color: #2c3e50;
                    font-size: 24px;
                    margin-bottom: 20px;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #34495e;
                    font-size: 20px;
                    margin-top: 30px;
                    margin-bottom: 15px;
                }
                h3 {
                    color: #7f8c8d;
                    font-size: 16px;
                    margin-top: 20px;
                    margin-bottom: 10px;
                }
                p {
                    margin-bottom: 15px;
                    line-height: 1.8;
                }
                ul {
                    margin-bottom: 15px;
                    padding-left: 20px;
                }
                li {
                    margin-bottom: 8px;
                    line-height: 1.6;
                }
                .summary {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .event-analysis {
                    background-color: #f0f8ff;
                    padding: 20px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .analysis-section {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #999;
                    font-size: 14px;
                    text-align: center;
                }
                pre {
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 4px;
                    overflow-x: auto;
                }
                code {
                    font-family: 'Courier New', Courier, monospace;
                }
                strong {
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Daily RSS</h1>
                <p>日期: {{date}}</p>
                <p>新闻数量: {{news_count}} 条</p>
                
                <!-- 第一层分析 -->
                <div class="analysis-section">
                    <h1>Summary 是日要闻</h1>
                    {{first_layer}}
                </div>
                
                <!-- 第二层分析 -->
                <div class="analysis-section">
                    <h1>Advanced 深度分析</h1>
                    {{second_layer}}
                </div>
                
                <!-- 第三层分析 -->
                <div class="analysis-section">
                    <h1>Insights 洞察建议</h1>
                    {{third_layer}}
                </div>
                
                <!-- 新闻列表 -->
                <div class="analysis-section">
                    <h1>News 新闻列表</h1>
                    {{news_list}}
                </div>
                
                <div class="footer">
                    <p>此邮件由Daily RSS工具自动生成</p>
                    <p>生成时间: {{timestamp}}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    # 打印模板字符串的相关部分，显示确切的缩进
    print("模板字符串中的日期和新闻数量变量:")
    lines = html.split('\n')
    for i, line in enumerate(lines):
        if '{{date}}' in line or '{{news_count}}' in line:
            print(f"Line {i+1}: '{line}'")
            print(f"Indentation: {len(line) - len(line.lstrip())} spaces")
            print(f"Stripped line: '{line.strip()}'")
            print()
    
    # 测试替换
    test_date = "2026-02-16"
    test_news_count = "123"
    test_timestamp = "2026-02-16T18:37:23.018465"
    
    # 尝试不同的缩进
    for indent in ['                ', '            ', '        ']:
        test_html = html
        test_html = test_html.replace(f'{indent}{{date}}', test_date)
        test_html = test_html.replace(f'{indent}{{news_count}}', test_news_count)
        test_html = test_html.replace(f'{indent}{{timestamp}}', test_timestamp)
        
        if test_date in test_html:
            print(f"✓ 替换成功，使用缩进: '{indent}'")
            break
    else:
        print("✗ 替换失败，所有缩进都尝试过了")

if __name__ == "__main__":
    test_template_indent()
