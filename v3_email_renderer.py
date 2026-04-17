"""
V3 Email Renderer - Production Module

用于将 V3 JSON report 数据渲染为 Figma 设计稿对应的 HTML 邮件模板。
800px 固定宽度，深色主题，table-based layout 适配邮件客户端。
"""

import os
import base64
from datetime import datetime
from typing import Dict, Any, List


def get_header_bg_base64() -> str:
    """获取 Header 背景图的 base64 data URI"""
    img_path = os.path.join(os.path.dirname(__file__), 'assets/images/header_bg.png')
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return ""


def load_template() -> str:
    """加载 HTML 模板文件"""
    template_path = os.path.join(os.path.dirname(__file__), 'email_template_v3.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_day_of_week(date_str: str) -> str:
    """获取星期几英文"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[date_obj.weekday()]


def render_top_events(events: List[Dict]) -> str:
    """渲染 Top Events 模块"""
    # 标题部分
    title_html = """
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="192" style="margin-bottom: 48px;">
        <tr>
            <td style="padding-bottom: 11px;">
                <p style="color: #787878; font-size: 18px; font-weight: 500; margin: 0;">Key Events</p>
            </td>
        </tr>
        <tr>
            <td>
                <p style="color: #F5F5F5; font-size: 32px; font-weight: 500; margin: 0;">关键事件</p>
            </td>
        </tr>
    </table>
    """

    # 事件列表
    events_html = ""
    for i, event in enumerate(events[:3], 1):
        events_html += _render_top_event_item(i, event)

    return title_html + events_html


def _render_top_event_item(index: int, event: Dict) -> str:
    """渲染单个 Top Event 卡片"""
    number = str(index).zfill(2)
    return f"""
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 48px;">
        <tr>
            <td width="40" valign="top" style="padding-right: 48px;">
                <p style="color: #F5F5F5; font-size: 24px; font-weight: 500; margin: 0;"><nobr>{number}</nobr></p>
            </td>
            <td valign="top">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                    <tr>
                        <td style="padding-bottom: 16px;">
                            <p style="color: #F5F5F5; font-size: 24px; font-weight: 500; margin: 0;">{event.get('title', '未命名事件')}</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding-bottom: 16px;">
                            <p style="color: #B0B0B0; font-size: 18px; font-weight: 400; margin: 0; line-height: 1.5;">{event.get('description', '')}</p>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%"
                                   style="background-color: #141416; border: 1px solid #1A1A1D; border-radius: 4px;">
                                <tr>
                                    <td style="padding: 13px 9px;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                            <tr>
                                                <td style="padding-bottom: 8px;">
                                                    <p style="color: #3D7092; font-size: 14px; font-weight: 400; margin: 0;">对我意味什么</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <p style="color: #B0B0B0; font-size: 14px; font-weight: 400; margin: 0; line-height: 1.5;">{event.get('so_what', '')}</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    """


def render_six_dimensions(briefs: Dict[str, str]) -> str:
    """渲染六维简报模块"""
    dimension_labels = [
        ("Models", "model_and_capability"),
        ("AI Products", "ai_product_and_interaction"),
        ("Design", "design_and_experience"),
        ("Platform", "technology_and_platform"),
        ("Business", "business_and_monetization"),
        ("Policy", "policy_and_ethics"),
    ]

    html = """<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">"""

    for row_idx in range(3):
        row_items = dimension_labels[row_idx * 2 : row_idx * 2 + 2]
        labels_briefs = [(item[0], briefs.get(item[1], '')) for item in row_items]
        has_bottom = (row_idx == 2)
        html += _render_dimension_row(row_idx + 1, labels_briefs, has_bottom)

    html += """</table>"""
    return html


def _render_dimension_row(row_index: int, labels_briefs: List, has_bottom_border: bool) -> str:
    """渲染一行两个维度"""
    left_label, left_brief = labels_briefs[0]
    right_label, right_brief = labels_briefs[1]
    border_bottom = "border-bottom: 1px solid #1A1A1D;" if has_bottom_border else ""

    return f"""
    <tr>
        <td style="border-top: 1px solid #1A1A1D; {border_bottom}">
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                <tr>
                    {_render_dimension_cell(left_label, left_brief, has_right_border=True)}
                    {_render_dimension_cell(right_label, right_brief, has_right_border=False)}
                </tr>
            </table>
        </td>
    </tr>
    """


def _render_dimension_cell(label: str, brief: str, has_right_border: bool = False) -> str:
    """渲染单个维度单元格"""
    is_empty = brief == "今日无显著动态" or brief == "今天没有显著变化"
    text_color = "#787878" if is_empty else "#B0B0B0"
    border_right = "border-right: 1px solid #1A1A1D;" if has_right_border else ""

    return f"""
    <td width="50%" style="{border_right} padding: 72px 48px 72px 48px;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
            <tr>
                <td style="padding-bottom: 56px;">
                    <p style="color: #F5F5F5; font-size: 18px; font-weight: 500; margin: 0; width: 100px;">{label}</p>
                </td>
            </tr>
            <tr>
                <td>
                    <p style="color: {text_color}; font-size: 14px; font-weight: 400; margin: 0; line-height: 1.5;">{brief}</p>
                </td>
            </tr>
        </table>
    </td>
    """


# 图标 base64 (SVG)
ICON_EVIDENCE = "data:image/svg+xml;base64,PHN2ZyBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJub25lIiB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBvdmVyZmxvdz0idmlzaWJsZSIgc3R5bGU9ImRpc3BsYXk6IGJsb2NrOyIgdmlld0JveD0iMCAwIDE2IDE2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBpZD0iRnJhbWUiPgo8cGF0aCBpZD0iVmVjdG9yIiBkPSJNOCAxNC42NjY3TDUuMzMzMzMgMTJIMTAuNjY2N0w4IDE0LjY2NjdaTTggMS4zMzMzM0wxMC42NjY3IDRINS4zMzMzM0w4IDEuMzMzMzNaTTggOS4zMzMzM0M3LjI2MzYgOS4zMzMzMyA2LjY2NjY3IDguNzM2NCA2LjY2NjY3IDhDNi42NjY2NyA3LjI2MzYgNy4yNjM2IDYuNjY2NjcgOCA2LjY2NjY3QzguNzM2NCA2LjY2NjY3IDkuMzMzMzMgNy4yNjM2IDkuMzMzMzMgOEM5LjMzMzMzIDguNzM2NCA4LjczNjQgOS4zMzMzMyA4IDkuMzMzMzNaTTEuMzMzMzMgOEw0IDUuMzMzMzNWMTAuNjY2N0wxLjMzMzMzIDhaTTE0LjY2NjcgOEwxMiAxMC42NjY3VjUuMzMzMzNMMTQuNjY2NyA4WiIgZmlsbD0iI0Y1RjVGNSIvPgo8L2c+Cjwvc3ZnPg=="
ICON_REASONING = "data:image/svg+xml;base64,PHN2ZyBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJub25lIiB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBvdmVyZmxvdz0idmlzaWJsZSIgc3R5bGU9ImRpc3BsYXk6IGJsb2NrOyIgdmlld0JveD0iMCAwIDE2IDE2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBpZD0iRnJhbWUiPgo8cGF0aCBpZD0iVmVjdG9yIiBkPSJNMTAuNjY2NyAxMC42NjY3QzExLjc3MTMgMTAuNjY2NyAxMi42NjY3IDExLjU2MjEgMTIuNjY2NyAxMi42NjY3QzEyLjY2NjcgMTMuNzcxMyAxMS43NzEzIDE0LjY2NjcgMTAuNjY2NyAxNC42NjY3QzkuNTYyMDcgMTQuNjY2NyA4LjY2NjY3IDEzLjc3MTMgOC42NjY2NyAxMi42NjY3QzguNjY2NjcgMTEuNTYyMSA5LjU2MjA3IDEwLjY2NjcgMTAuNjY2NyAxMC42NjY3Wk00IDhDNS40NzI3NiA4IDYuNjY2NjcgOS4xOTM5MyA2LjY2NjY3IDEwLjY2NjdDNi42NjY2NyAxMi4xMzk0IDUuNDcyNzYgMTMuMzMzMyA0IDEzLjMzMzNDMi41MjcyNCAxMy4zMzMzIDEuMzMzMzMgMTIuMTM5NCAxLjMzMzMzIDEwLjY2NjdDMS4zMzMzMyA5LjE5MzkzIDIuNTI3MjQgOCA0IDhaTTkuNjY2NjcgMS4zMzMzM0MxMS42OTE3IDEuMzMzMzMgMTMuMzMzMyAyLjk3NDk1IDEzLjMzMzMgNUMxMy4zMzMzIDcuMDI1MDcgMTEuNjkxNyA4LjY2NjY3IDkuNjY2NjcgOC42NjY2N0M3LjY0MTYgOC42NjY2NyA2IDcuMDI1MDcgNiA1QzYgMi45NzQ5NSA3LjY0MTYgMS4zMzMzMyA5LjY2NjY3IDEuMzMzMzNaIiBmaWxsPSIjRjVGNUY1Ii8+CjwvZz4KPC9zdmc+"
ICON_IMPACT = "data:image/svg+xml;base64,PHN2ZyBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJub25lIiB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBvdmVyZmxvdz0idmlzaWJsZSIgc3R5bGU9ImRpc3BsYXk6IGJsb2NrOyIgdmlld0JveD0iMCAwIDE2IDE2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBpZD0iRnJhbWUiPgo8cGF0aCBpZD0iVmVjdG9yIiBkPSJNMi42MTkyNSAzLjI4NTk3TDMuNTYyMSA0LjIyODgyQzIuNTk2OTUgNS4xOTM5NiAyIDYuNTI3MjkgMiA4LjAwMDA2QzIgOS40NzI4IDIuNTk2OTUgMTAuODA2MSAzLjU2MjEgMTEuNzcxM0wyLjYxOTI1IDEyLjcxNDFDMS40MTI4MyAxMS41MDc3IDAuNjY2NjY3IDkuODQxMDYgMC42NjY2NjcgOC4wMDAwNkMwLjY2NjY2NyA2LjE1OTA1IDEuNDEyODMgNC40OTIzOCAyLjYxOTI1IDMuMjg1OTdaTTEzLjM4MDcgMy4yODU5N0MxNC41ODcyIDQuNDkyMzggMTUuMzMzMyA2LjE1OTA1IDE1LjMzMzMgOC4wMDAwNkMxNS4zMzMzIDkuODQxMDYgMTQuNTg3MiAxMS41MDc3IDEzLjM4MDcgMTIuNzE0MUwxMi40Mzc5IDExLjc3MTNDMTMuNDAzMSAxMC44MDYxIDE0IDkuNDcyOCAxNCA4LjAwMDA2QzE0IDYuNTI3NjMgMTMuNDAzMyA1LjE5NDU3IDEyLjQzODYgNC4yMjk0OEwxMy4zODA3IDMuMjg1OTdaTTguNjY2NjcgMy4zMzMzOFY3LjMzMzRIMTAuNjY2N0w3LjMzMzMzIDEyLjY2NjdWOC42NjY3M0g1LjMzMzMzTDguNjY2NjcgMy4zMzMzOFpNNC41MDQ5MSA1LjE3MTYyTDUuNDQ3NzEgNi4xMTQ0M0M0Ljk2NTE0IDYuNTk3IDQuNjY2NjcgNy4yNjM2NiA0LjY2NjY3IDguMDAwMDZDNC42NjY2NyA4LjczNjQgNC45NjUxNCA5LjQwMzA2IDUuNDQ3NzEgOS44ODU2Nkw0LjUwNDkxIDEwLjgyODVDMy43ODEwNSAxMC4xMDQ2IDMuMzMzMzMgOS4xMDQ2IDMuMzMzMzMgOC4wMDAwNkMzLjMzMzMzIDYuODk1NDYgMy43ODEwNSA1Ljg5NTQ4IDQuNTA0OTEgNS4xNzE2MlpNMTEuNDk1NyA1LjE3MjI4QzEyLjIxOTIgNS44OTYwOCAxMi42NjY3IDYuODk1OCAxMi42NjY3IDguMDAwMDZDMTIuNjY2NyA5LjEwNDYgMTIuMjE4OSAxMC4xMDQ2IDExLjQ5NTEgMTAuODI4NUwxMC41NTIzIDkuODg1NjZDMTEuMDM0OSA5LjQwMzA2IDExLjMzMzMgOC43MzY0IDExLjMzMzMgOC4wMDAwNkMxMS4zMzMzIDcuMjY0IDExLjAzNTEgNi41OTc2MiAxMC41NTI5IDYuMTE1MUwxMS40OTU3IDUuMTcyMjhaIiBmaWxsPSIjRjVGNUY1Ii8+CjwvZz4KPC9zdmc+"


def render_trend_watch(trends: List[Dict], news_map: Dict[str, Dict]) -> str:
    """渲染趋势观察模块"""
    html = """<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">"""
    for i, trend in enumerate(trends, 1):
        html += _render_trend_item(i, trend, news_map)
    html += """</table>"""
    return html


def _render_trend_item(index: int, trend: Dict, news_map: Dict[str, Dict]) -> str:
    """渲染单个趋势观察项"""
    number = str(index).zfill(2)

    # 渲染引用新闻
    news_ids = trend.get('news_ids', [])
    refs_html = ""
    if news_ids:
        refs_html = "<p style='color: #787878; font-size: 12px; font-weight: 400; margin: 0 0 12px 0;'>引用文章</p>"
        for news_id in news_ids[:5]:
            news = news_map.get(news_id, {})
            title = news.get('title', '未命名')
            url = news.get('url', '#')
            refs_html += f"""
            <p style="color: #3D7092; font-size: 12px; font-weight: 400; margin: 0 0 8px 0;">
                <a href="{url}" style="color: #3D7092; text-decoration: none;">{title}</a>
            </p>
            """
    else:
        refs_html = "<p style='color: #787878; font-size: 12px; font-weight: 400; margin: 0;'>暂无引用</p>"

    # 分隔线
    divider_html = """
    <tr>
        <td style="padding-left: 48px; padding-right: 48px; padding-top: 37px; padding-bottom: 37px;">
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                <tr>
                    <td style="border-top: 1px solid #1A1A1D; height: 1px; line-height: 1px;">&nbsp;</td>
                </tr>
            </table>
        </td>
    </tr>
    """ if index > 1 else ""

    return f"""
    {divider_html}
    <tr>
        <td style="padding-left: 48px; padding-right: 48px;">
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                <tr>
                    <td width="40" valign="top" style="padding-right: 24px;">
                        <p style="color: #787878; font-size: 24px; font-weight: 500; margin: 0;"><nobr>{number}</nobr></p>
                    </td>
                    <td valign="top">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                            <tr>
                                <td style="padding-bottom: 48px;">
                                    <p style="color: #F5F5F5; font-size: 24px; font-weight: 500; margin: 0;">{trend.get('title', '未命名趋势')}</p>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <!-- Evidence -->
                                        <tr>
                                            <td style="padding-bottom: 32px;">
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                                    <tr>
                                                        <td style="padding-bottom: 8px;">
                                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0"
                                                                   style="background-color: #1A1A1D; border-radius: 3px;">
                                                                <tr>
                                                                    <td style="padding: 4px 8px;">
                                                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                                            <tr>
                                                                                <td width="16" style="padding-right: 10px;">
                                                                                    <img src="{ICON_EVIDENCE}" width="16" height="16" alt="" style="display: block; width: 16px; height: 16px;">
                                                                                </td>
                                                                                <td>
                                                                                    <p style="color: #F5F5F5; font-size: 14px; font-weight: 500; margin: 0;">证据</p>
                                                                                </td>
                                                                            </tr>
                                                                        </table>
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>
                                                            <p style="color: #B0B0B0; font-size: 16px; font-weight: 400; margin: 0; line-height: 1.5;">{trend.get('evidence', '')}</p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <!-- Reasoning -->
                                        <tr>
                                            <td style="padding-bottom: 32px;">
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                                    <tr>
                                                        <td style="padding-bottom: 8px;">
                                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0"
                                                                   style="background-color: #1A1A1D; border-radius: 3px;">
                                                                <tr>
                                                                    <td style="padding: 4px 8px;">
                                                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                                            <tr>
                                                                                <td width="16" style="padding-right: 10px;">
                                                                                    <img src="{ICON_REASONING}" width="16" height="16" alt="" style="display: block; width: 16px; height: 16px;">
                                                                                </td>
                                                                                <td>
                                                                                    <p style="color: #F5F5F5; font-size: 14px; font-weight: 500; margin: 0;">推理</p>
                                                                                </td>
                                                                            </tr>
                                                                        </table>
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>
                                                            <p style="color: #B0B0B0; font-size: 16px; font-weight: 400; margin: 0; line-height: 1.5;">{trend.get('reasoning', '')}</p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <!-- Impact -->
                                        <tr>
                                            <td style="padding-bottom: 32px;">
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                                    <tr>
                                                        <td style="padding-bottom: 8px;">
                                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0"
                                                                   style="background-color: #1A1A1D; border-radius: 3px;">
                                                                <tr>
                                                                    <td style="padding: 4px 8px;">
                                                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                                            <tr>
                                                                                <td width="16" style="padding-right: 10px;">
                                                                                    <img src="{ICON_IMPACT}" width="16" height="16" alt="" style="display: block; width: 16px; height: 16px;">
                                                                                </td>
                                                                                <td>
                                                                                    <p style="color: #F5F5F5; font-size: 14px; font-weight: 500; margin: 0;">影响</p>
                                                                                </td>
                                                                            </tr>
                                                                        </table>
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>
                                                            <p style="color: #B0B0B0; font-size: 16px; font-weight: 400; margin: 0; line-height: 1.5;">{trend.get('so_what_for_me', '')}</p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <!-- References -->
                                        <tr>
                                            <td>{refs_html}</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    """


def render_actions(suggestions: Dict) -> tuple:
    """渲染行动建议模块"""
    today_html = _render_action_card("今天", suggestions.get('today', []))
    this_week_html = _render_action_card("本周", suggestions.get('this_week', []))
    this_month_html = _render_action_card("本月", suggestions.get('this_month', []))
    return today_html, this_week_html, this_month_html


def _render_action_card(title: str, items: List[Dict]) -> str:
    """渲染单个行动建议卡片"""
    items_html = ""
    for item in items[:3]:
        action_text = item.get('action', '')
        items_html += f"""
        <tr>
            <td style="padding: 8px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                    <tr>
                        <td valign="top" style="padding-right: 8px; line-height: 0; font-size: 0;">
                            <div style="border: 1px solid #2A2A2E; border-radius: 3px; width: 14px; height: 14px; display: inline-block; line-height: 0; font-size: 0;"></div>
                        </td>
                        <td valign="top">
                            <p style="color: #B0B0B0; font-size: 14px; font-weight: 400; margin: 0; line-height: 1.5;">{action_text}</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        """

    if not items:
        items_html = """
        <tr>
            <td style="padding: 8px;">
                <p style="color: #787878; font-size: 14px; font-weight: 400; margin: 0;">暂无建议</p>
            </td>
        </tr>
        """

    return f"""
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%"
           style="background-color: #141416; border: 1px solid #1A1A1D; border-radius: 6px; height: 360px;">
        <tr>
            <td style="padding: 12px 17px; border-bottom: 1px solid #1A1A1D;">
                <p style="color: #F5F5F5; font-size: 14px; font-weight: 500; margin: 0;">{title}</p>
            </td>
        </tr>
        {items_html}
    </table>
    """


def render_email(report_data: Dict[str, Any], news_map: Dict[str, Dict] = None) -> str:
    """
    完整渲染 V3 邮件 HTML

    Args:
        report_data: V3 JSON report 数据
        news_map: 新闻 ID -> 新闻详情的映射（用于引用文章）

    Returns:
        渲染后的 HTML 字符串
    """
    if news_map is None:
        news_map = {}

    template = load_template()

    meta = report_data.get('meta', {})
    signals = report_data.get('signal_interpretation', {})
    briefs = signals.get('six_dimension_briefs', {})
    trends = report_data.get('deep_analysis', [])
    actions = report_data.get('action_suggestions', {})

    # Header 背景
    template = template.replace('{{header_bg}}', get_header_bg_base64())

    # Meta
    template = template.replace('{{meta.date}}', meta.get('date', ''))
    template = template.replace('{{meta.day_of_week}}', get_day_of_week(meta.get('date', '')))
    template = template.replace('{{meta.filtered_count}}', str(meta.get('filtered_count', 0)))

    # Key Insight
    template = template.replace('{{signal_interpretation.main_conclusion}}', signals.get('main_conclusion', ''))
    template = template.replace('{{signal_interpretation.why_it_matters}}', signals.get('why_it_matters', ''))

    # Top Events
    top_events_html = render_top_events(signals.get('top_events', []))
    template = template.replace('{{top_events_html}}', top_events_html)

    # Six Dimensions
    six_dimensions_html = render_six_dimensions(briefs)
    template = template.replace('{{six_dimensions_html}}', six_dimensions_html)

    # Trend Watch
    trend_watch_html = render_trend_watch(trends, news_map)
    template = template.replace('{{trend_watch_html}}', trend_watch_html)

    # Actions
    today_html, this_week_html, this_month_html = render_actions(actions)
    template = template.replace('{{actions_today_html}}', today_html)
    template = template.replace('{{actions_this_week_html}}', this_week_html)
    template = template.replace('{{actions_this_month_html}}', this_month_html)

    return template