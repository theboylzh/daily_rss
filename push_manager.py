import os
import json
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from typing import Dict, Any, List
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

        # 生成邮件主题（兼容 V1 和 V2 格式）
        if 'date' in analysis:
            subject = f"News Daily - {analysis['date']}"
        elif 'summary' in analysis:
            # V2 格式，使用当前日期
            subject = f"News Daily - {datetime.now().strftime('%Y-%m-%d')}"
        else:
            # V1 格式，尝试从 first_layer 提取日期
            subject = f"News Daily - {datetime.now().strftime('%Y-%m-%d')}"

        # 判断是 V2 格式还是 V1 格式
        if 'summary' in analysis:
            html_content = self._generate_v2_html_content(analysis)
        else:
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

    def _generate_v2_html_content(self, analysis: Dict[str, Any]) -> str:
        """生成 V2.0.0 格式的 HTML 邮件内容"""
        # 读取模板文件
        template_path = os.path.join(os.path.dirname(__file__), 'email_template_v2.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html = f.read()
        except FileNotFoundError:
            print(f"模板文件未找到：{template_path}，使用备用模板")
            html = self._get_fallback_v2_template()

        # 渲染各个板块
        html = self._render_v2_summary(html, analysis.get('summary', {}))
        html = self._render_v2_key_news(html, analysis.get('key_news_brief', []), analysis.get('briefing', {}))
        html = self._render_v2_news_list(html)
        html = self._render_v2_opinions(html, analysis.get('perspectives', []))
        html = self._render_v2_insights(html, analysis.get('deep_analysis', []))
        html = self._render_v2_advices(html, analysis.get('suggestions', {}))

        # 替换通用变量
        html = html.replace('{{date}}', analysis.get('date', datetime.now().strftime('%Y-%m-%d')))
        html = html.replace('{{news_count}}', str(analysis.get('news_count', 0)))
        html = html.replace('{{timestamp}}', analysis.get('timestamp', datetime.now().isoformat()))

        return html

    def _render_v2_summary(self, html: str, summary: Dict[str, Any]) -> str:
        """渲染 Today Brief 板块"""
        one_liner = summary.get('one_liner', '未来难料，AI 局势依旧充满变数')
        digest = summary.get('digest', 'AI 领域动态频发，行业震动与巨头加速布局并存，同时油价上涨影响消费市场。')
        keywords = summary.get('keywords', ['震荡', '未知', '涨价'])

        # 生成关键词 HTML
        keywords_html = ''.join([f'<span class="keyword-item">{kw}</span>' for kw in keywords[:3]])

        html = html.replace('{{summary.one_liner}}', one_liner)
        html = html.replace('{{summary.digest}}', digest)
        html = html.replace('{{keywords_html}}', keywords_html)

        return html

    def _render_v2_key_news(self, html: str, key_news_brief: List[Dict], briefing: Dict[str, Any]) -> str:
        """渲染重点新闻高亮板块"""
        # 从 briefing 中获取四类新闻
        economy = briefing.get('economy', '暂无经济新闻')

        # 简单处理：取每类新闻的前 80 字
        economy_short = economy[:80] + '...' if len(economy) > 80 else economy

        # 从 key_news_brief 中获取标题
        highlight_tech_1 = key_news_brief[0].get('title', '科技新闻 1') if len(key_news_brief) > 0 else '暂无科技新闻'
        highlight_tech_2 = key_news_brief[1].get('title', '科技新闻 2') if len(key_news_brief) > 1 else '暂无科技新闻'

        html = html.replace('{{highlight_economy}}', economy_short)
        html = html.replace('{{highlight_tech_1}}', highlight_tech_1)
        html = html.replace('{{highlight_tech_2}}', highlight_tech_2)

        return html

    def _render_v2_news_list(self, html: str) -> str:
        """渲染新闻列表板块"""
        try:
            # 获取当前日期的新闻文件
            today = datetime.now().strftime('%Y-%m-%d')
            news_file = os.path.join('data', 'news', f'{today}.json')

            if not os.path.exists(news_file):
                return self._fill_empty_news_list(html)

            with open(news_file, 'r', encoding='utf-8') as f:
                news_items = json.load(f)

            if not news_items:
                return self._fill_empty_news_list(html)

            # 按类别分组（简化处理：随机分配）
            categories = {
                'politics': [],
                'economy': [],
                'industry': [],
                'tech': []
            }

            for i, news in enumerate(news_items[:12]):  # 最多 12 条
                category = list(categories.keys())[i % 4]
                title = news.get('title', '无标题')
                url = news.get('url', '#')
                categories[category].append(f'<li><a href="{url}" style="color: inherit; text-decoration: none;">{title}</a></li>')

            # 确保每个类别至少有内容
            for cat in categories:
                if not categories[cat]:
                    categories[cat] = ['<li>暂无相关新闻</li>']

            html = html.replace('{{news_politics_items}}', ''.join(categories['politics']))
            html = html.replace('{{news_economy_items}}', ''.join(categories['economy']))
            html = html.replace('{{news_industry_items}}', ''.join(categories['industry']))
            html = html.replace('{{news_tech_items}}', ''.join(categories['tech']))

            return html

        except Exception as e:
            print(f"渲染新闻列表失败：{e}")
            return self._fill_empty_news_list(html)

    def _fill_empty_news_list(self, html: str) -> str:
        """填充空新闻列表"""
        empty_item = '<li>暂无新闻数据</li>'
        html = html.replace('{{news_politics_items}}', empty_item)
        html = html.replace('{{news_economy_items}}', empty_item)
        html = html.replace('{{news_industry_items}}', empty_item)
        html = html.replace('{{news_tech_items}}', empty_item)
        return html

    def _render_v2_opinions(self, html: str, perspectives: List[Dict]) -> str:
        """渲染观点板块"""
        if not perspectives:
            html = html.replace('{{opinions_html}}', '<p class="body-2 text-secondary">暂无观点内容</p>')
            return html

        opinions_html = ''
        for i, p in enumerate(perspectives[:3]):
            opinion_html = f'''
            <div class="opinion-item">
                <p class="opinion-number">{str(i+1).zfill(2)}</p>
                <p class="opinion-title">{p.get('title', '观点标题')}</p>
                <p class="opinion-description">{p.get('description', '观点描述')}</p>
                <div class="opinion-quotes">
            '''
            # 添加引用
            refs = p.get('references', [])
            for ref in refs[:2]:
                opinion_html += f'''
                <div class="quote-item">
                    <div class="quote-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M12 4L14 6L10 10L14 14L12 16L6 10L12 4Z" fill="#B88459"/>
                        </svg>
                    </div>
                    <p class="quote-text">{ref.get('title', '引用标题')}</p>
                </div>
                '''
            opinion_html += '</div></div>'
            opinions_html += opinion_html

        html = html.replace('{{opinions_html}}', opinions_html)
        return html

    def _render_v2_insights(self, html: str, deep_analysis: List[Dict]) -> str:
        """渲染关键分析板块"""
        if not deep_analysis:
            html = html.replace('{{insights_html}}', '<p class="body-2 text-secondary">暂无分析内容</p>')
            return html

        insights_html = ''
        for a in deep_analysis[:3]:
            tags = a.get('tags', ['行业'])
            category = tags[0] if tags else '行业'

            insight_html = f'''
            <div class="insight-item">
                <p class="insight-category">{category}</p>
                <p class="insight-title">{a.get('title', '分析标题')}</p>

                <table class="insight-content-row" cellpadding="0" cellspacing="0">
                    <tr>
                        <td class="insight-subtitle">
                            <p class="insight-subtitle-number">01</p>
                            <p class="insight-subtitle-label">客观事实</p>
                        </td>
                        <td class="insight-subtitle-content body-2">{a.get('facts', '暂无事实描述')}</td>
                    </tr>
                </table>

                <table class="insight-content-row" cellpadding="0" cellspacing="0">
                    <tr>
                        <td class="insight-subtitle">
                            <p class="insight-subtitle-number">02</p>
                            <p class="insight-subtitle-label">整体观点</p>
                        </td>
                        <td class="insight-subtitle-content body-2">{a.get('viewpoint', '暂无观点')}</td>
                    </tr>
                </table>

                <table class="insight-content-row" cellpadding="0" cellspacing="0">
                    <tr>
                        <td class="insight-subtitle">
                            <p class="insight-subtitle-number">03</p>
                            <p class="insight-subtitle-label">发生原因</p>
                        </td>
                        <td class="insight-subtitle-content body-2">{a.get('causes', '暂无原因分析')}</td>
                    </tr>
                </table>

                <table class="insight-content-row" cellpadding="0" cellspacing="0">
                    <tr>
                        <td class="insight-subtitle">
                            <p class="insight-subtitle-number">04</p>
                            <p class="insight-subtitle-label">后续预测</p>
                        </td>
                        <td class="insight-subtitle-content body-2">{a.get('prediction', '暂无预测')}</td>
                    </tr>
                </table>

                <table class="insight-content-row" cellpadding="0" cellspacing="0">
                    <tr>
                        <td class="insight-subtitle">
                            <p class="insight-subtitle-number">05</p>
                            <p class="insight-subtitle-label">个体建议</p>
                        </td>
                        <td class="insight-subtitle-content body-2">{a.get('advice', '暂无建议')}</td>
                    </tr>
                </table>
            </div>
            '''
            insights_html += insight_html

        html = html.replace('{{insights_html}}', insights_html)
        return html

    def _render_v2_advices(self, html: str, suggestions: Dict[str, Any]) -> str:
        """渲染建议板块"""
        if not suggestions:
            html = html.replace('{{advices_html}}', '<p class="body-2 text-secondary">暂无建议内容</p>')
            return html

        advices_html = ''

        # 思维启发
        thinking = suggestions.get('thinking', {})
        advices_html += self._render_single_advice(
            '思维启发',
            thinking.get('title', '暂无'),
            thinking.get('content', '暂无内容')
        )

        # 投资建议
        investment = suggestions.get('investment', {})
        advices_html += self._render_single_advice(
            '投资建议',
            investment.get('title', '暂无'),
            investment.get('content', '暂无内容')
        )

        # 个人提升
        self_improvement = suggestions.get('self_improvement', {})
        advices_html += self._render_single_advice(
            '个人提升',
            self_improvement.get('title', '暂无'),
            self_improvement.get('content', '暂无内容')
        )

        # 机遇风险
        opp_risk = suggestions.get('opportunities_risks', {})
        advices_html += self._render_single_advice(
            '机遇风险',
            opp_risk.get('title', '暂无'),
            opp_risk.get('content', '暂无内容')
        )

        html = html.replace('{{advices_html}}', advices_html)
        return html

    def _render_single_advice(self, category: str, title: str, content: str) -> str:
        """渲染单个建议项"""
        # 将换行符转换为 <p> 标签
        content_paragraphs = content.split('\n')
        content_html = ''.join([f'<p>{p.strip()}</p>' for p in content_paragraphs if p.strip()])

        return f'''
        <table class="advice-item" cellpadding="0" cellspacing="0">
            <tr>
                <td class="advice-category">{category}</td>
                <td class="advice-content">
                    <p class="advice-title">{title}</p>
                    <div class="advice-description body-2">{content_html}</div>
                </td>
            </tr>
        </table>
        '''

    def _get_fallback_v2_template(self) -> str:
        """备用 V2 模板"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>News Daily</title>
</head>
<body>
    <h1>News Daily</h1>
    <p>日期：{{date}}</p>
    <p>新闻数量：{{news_count}}</p>
    <hr>
    <p>模板加载失败，请使用完整模板</p>
</body>
</html>'''


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
