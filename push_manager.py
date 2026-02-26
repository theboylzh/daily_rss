import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from typing import Dict, Any
from config import settings


class PushManager:
    def __init__(self):
        self.email_sender = settings.EMAIL_SENDER
        self.email_receiver = settings.EMAIL_RECEIVER
        self.email_password = settings.EMAIL_PASSWORD
        self.email_smtp_server = settings.EMAIL_SMTP_SERVER
        self.email_smtp_port = settings.EMAIL_SMTP_PORT
    
    def send_daily_analysis(self, analysis: Dict[str, Any]):
        """发送每日分析报告"""
        if not analysis:
            print("无分析报告可发送")
            return False
        
        print("开始发送每日分析报告...")
        
        # 生成邮件内容
        subject = f"每日新闻分析报告 - {analysis['date']}"
        html_content = self._generate_html_content(analysis)
        
        # 发送邮件
        try:
            self._send_email(subject, html_content)
            print("每日分析报告发送成功")
            return True
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
    
    def _markdown_to_html(self, markdown: str) -> str:
        """将Markdown转换为HTML"""
        if not markdown:
            return ""
        
        try:
            import markdown2
            # 使用markdown2库进行转换，启用常用扩展
            html = markdown2.markdown(markdown, extras=[
                "fenced-code-blocks",  # 支持代码块
                "tables",              # 支持表格
                "header-ids",          # 为标题添加ID
                "break-on-newline"      # 支持换行
            ])
            return html
        except Exception as e:
            print(f"Markdown解析失败，使用备用方法: {e}")
            # 保留原有的备用实现
            # 处理换行
            html = markdown.replace('\n\n', '<p></p>')
            html = html.replace('\n', '<br>')
            
            # 处理标题
            import re
            html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
            html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
            html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
            
            # 处理列表
            html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
            html = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
            
            # 处理粗体
            html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
            
            # 处理代码块
            html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
            
            return html
    
    def _generate_html_content(self, analysis: Dict[str, Any]) -> str:
        """生成每日分析报告的HTML内容"""
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
        
        # 处理新的三层分析格式
        if 'first_layer' in analysis and 'second_layer' in analysis and 'third_layer' in analysis:
            # 转换第一层分析
            first_layer_html = self._markdown_to_html(analysis['first_layer'])
            
            # 转换第二层分析
            second_layer_html = ""
            for event_analysis in analysis['second_layer']:
                second_layer_html += self._markdown_to_html(event_analysis)
            
            # 转换第三层分析
            third_layer_html = self._markdown_to_html(analysis['third_layer'])
            
            # 替换模板变量
            html = html.replace('            {{first_layer}}', first_layer_html)
            html = html.replace('            {{second_layer}}', second_layer_html)
            html = html.replace('            {{third_layer}}', third_layer_html)
        else:
            # 保持对旧格式的兼容性
            daily_summary_html = self._markdown_to_html(analysis.get('daily_summary', ''))
            event_analysis_html = self._markdown_to_html(analysis.get('event_analysis', ''))
            
            # 替换为旧格式内容
            html = html.replace('            {{first_layer}}', daily_summary_html)
            html = html.replace('            {{second_layer}}', event_analysis_html)
            html = html.replace('            {{third_layer}}', '<p>无综合分析数据</p>')
        
        # 生成新闻列表HTML
        news_list_html = self._generate_news_list()
        html = html.replace('            {{news_list}}', news_list_html)
        
        # 替换通用变量
        html = html.replace('{{date}}', analysis['date'])
        html = html.replace('{{news_count}}', str(analysis['news_count']))
        html = html.replace('{{timestamp}}', analysis['timestamp'])
        
        return html
    
    def _generate_news_list(self) -> str:
        """生成新闻列表HTML"""
        try:
            # 获取当前日期的新闻文件
            today = datetime.now().strftime('%Y-%m-%d')
            news_file = os.path.join('data', 'news', f'{today}.json')
            
            if not os.path.exists(news_file):
                return '<p>暂无新闻数据</p>'
            
            # 加载新闻数据
            with open(news_file, 'r', encoding='utf-8') as f:
                news_items = json.load(f)
            
            if not news_items:
                return '<p>暂无新闻数据</p>'
            
            # 生成新闻列表HTML
            html = '<ul>'
            for news in news_items:
                title = news.get('title', '')
                url = news.get('url', '')
                if title and url:
                    # 创建可点击的链接，链接文本就是标题
                    html += f'<li><a href="{url}" target="_blank">{title}</a></li>'
            html += '</ul>'
            
            return html
        except Exception as e:
            print(f"生成新闻列表失败: {e}")
            return '<p>生成新闻列表失败</p>'
    
    def _send_email(self, subject: str, html_content: str):
        """发送邮件"""
        if not self.email_sender or not self.email_receiver or not self.email_password:
            raise Exception("邮箱配置未完成")
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['From'] = Header(self.email_sender, 'utf-8')
        msg['To'] = Header(self.email_receiver, 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        
        # 添加HTML内容
        part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part)
        
        # 发送邮件
        with smtplib.SMTP_SSL(self.email_smtp_server, self.email_smtp_port) as server:
            server.login(self.email_sender, self.email_password)
            server.sendmail(self.email_sender, self.email_receiver, msg.as_string())


if __name__ == "__main__":
    # 测试推送功能
    push_manager = PushManager()
    
    # 模拟分析结果
    mock_analysis = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "daily_summary": "# 今日新闻总结\n\n今日共分析 10 条新闻\n\n## 主要事件\n\n### 热点关键词\n\n- 技术 (3)\n- AI (2)\n- 商业 (2)\n\n## 事件分析\n\n这里是对今日主要事件的详细分析...",
        "event_analysis": "# 事件发展脉络分析\n\n## 今日重要事件\n\n### 技术\n\n- 技术新闻1\n- 技术新闻2\n- 技术新闻3\n\n## 横向分析\n\n这里是对今日事件的横向分析...",
        "timestamp": datetime.now().isoformat(),
        "news_count": 10
    }
    
    # 发送测试邮件
    push_manager.send_daily_analysis(mock_analysis)
