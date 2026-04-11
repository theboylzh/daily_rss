"""
V2.0.0 JSON 解析模块
提供四层降级解析策略
"""
import json
import re
import logging
from typing import Dict, Any, Optional
from v2_schema import get_empty_structure

logger = logging.getLogger(__name__)


def parse_ai_json_response(text: str) -> Dict[str, Any]:
    """
    解析 AI 输出的 JSON，带四层降级策略

    降级流程：
    1. 直接 JSON 解析
    2. 提取 Markdown 代码块中的 JSON
    3. 正则提取 JSON 片段
    4. 返回空结构 + 记录错误日志

    Args:
        text: AI 输出的原始文本

    Returns:
        解析后的字典，如果全部失败则返回空结构
    """
    # 第 1 层：直接解析
    result = _try_direct_parse(text)
    if result:
        logger.info("JSON 解析成功：直接解析")
        return result

    # 第 2 层：提取 Markdown 代码块
    result = _try_markdown_extract(text)
    if result:
        logger.info("JSON 解析成功：Markdown 代码块提取")
        return result

    # 第 3 层：正则提取 JSON 片段
    result = _try_regex_extract(text)
    if result:
        logger.info("JSON 解析成功：正则提取")
        return result

    # 第 4 层：返回空结构
    logger.error(f"JSON 解析全部失败，返回空结构。原始输出前 500 字符：{text[:500]}...")
    return get_empty_structure()


def _try_direct_parse(text: str) -> Optional[Dict[str, Any]]:
    """尝试直接 JSON 解析"""
    try:
        data = json.loads(text)
        # 验证基本结构
        if isinstance(data, dict) and "summary" in data:
            return data
    except json.JSONDecodeError:
        pass
    return None


def _try_markdown_extract(text: str) -> Optional[Dict[str, Any]]:
    """尝试从 Markdown 代码块中提取 JSON"""
    # 支持 ```json 和 ``` 两种格式
    patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            json_text = match.group(1).strip()
            try:
                data = json.loads(json_text)
                if isinstance(data, dict) and "summary" in data:
                    return data
            except json.JSONDecodeError:
                continue
    return None


def _try_regex_extract(text: str) -> Optional[Dict[str, Any]]:
    """尝试用正则提取 JSON 对象"""
    # 从最外层开始匹配，支持嵌套
    json_objects = _extract_json_objects(text)

    for json_text in json_objects:
        try:
            data = json.loads(json_text)
            if isinstance(data, dict) and "summary" in data:
                return data
        except json.JSONDecodeError:
            continue

    return None


def _extract_json_objects(text: str) -> list:
    """
    从文本中提取所有可能的 JSON 对象
    使用括号匹配来找到完整的 JSON 对象
    """
    results = []
    i = 0

    while i < len(text):
        # 寻找第一个 {
        if text[i] == '{':
            start = i
            bracket_count = 1
            i += 1

            # 匹配对应的 }
            while i < len(text) and bracket_count > 0:
                if text[i] == '{':
                    bracket_count += 1
                elif text[i] == '}':
                    bracket_count -= 1
                i += 1

            if bracket_count == 0:
                results.append(text[start:i])
        else:
            i += 1

    # 按长度从大到小排序，优先尝试完整的 JSON
    results.sort(key=len, reverse=True)
    return results


def validate_v2_structure(data: Dict[str, Any]) -> tuple[bool, list]:
    """
    验证数据结构是否符合 V2 Schema

    Args:
        data: 待验证的数据字典

    Returns:
        (是否有效，错误信息列表)
    """
    errors = []

    # 检查 summary
    if "summary" not in data:
        errors.append("缺少 summary 字段")
    else:
        summary = data["summary"]
        if "one_liner" not in summary:
            errors.append("缺少 summary.one_liner")
        if "digest" not in summary:
            errors.append("缺少 summary.digest")
        if "keywords" not in summary:
            errors.append("缺少 summary.keywords")

    # 检查 key_news_brief
    if "key_news_brief" not in data:
        errors.append("缺少 key_news_brief 字段")

    # 检查 briefing
    if "briefing" not in data:
        errors.append("缺少 briefing 字段")
    else:
        briefing = data["briefing"]
        required_fields = ["politics", "economy", "industry", "tech"]
        for field in required_fields:
            if field not in briefing:
                errors.append(f"缺少 briefing.{field}")

    # 检查 perspectives
    if "perspectives" not in data:
        errors.append("缺少 perspectives 字段")

    # 检查 deep_analysis
    if "deep_analysis" not in data:
        errors.append("缺少 deep_analysis 字段")

    # 检查 suggestions
    if "suggestions" not in data:
        errors.append("缺少 suggestions 字段")
    else:
        suggestions = data["suggestions"]
        required_fields = ["thinking", "investment", "self_improvement", "opportunities_risks"]
        for field in required_fields:
            if field not in suggestions:
                errors.append(f"缺少 suggestions.{field}")

    return len(errors) == 0, errors
