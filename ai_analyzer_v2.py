"""
V2.0.0 AI 分析模块
实现四层分析流程：
- 阶段 1：概要生成
- 阶段 2：观点生成
- 阶段 3：深度分析
- 阶段 4：建议生成
"""
import os
import json
import time
import httpx
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import settings


# ============================================================================
# V2 Schema 定义（合并自 v2_schema.py）
# ============================================================================

# 预设标签库
TAGS_LIBRARY = [
    "政治",      # 政府、国际关系
    "经济",      # 宏观经济、GDP、通胀
    "科技",      # 技术突破、前沿科技
    "商业",      # 公司动态、商业合作
    "金融",      # 银行、证券、保险
    "国际",      # 国际时事
    "政策",      # 行业政策、监管
    "创新",      # 新产品、新技术
    "行业",      # 行业动态、供需变化
    "市场"       # 市场波动、股价变化
]


def get_empty_structure() -> Dict[str, Any]:
    """返回空的 V2 输出结构，用于降级处理"""
    return {
        "summary": {
            "one_liner": "今日暂无新闻摘要",
            "digest": "今日暂无新闻内容",
            "keywords": ["暂无", "暂无", "暂无"]
        },
        "key_news_brief": [],
        "briefing": {
            "politics": "暂无政治新闻",
            "economy": "暂无经济新闻",
            "industry": "暂无行业新闻",
            "tech": "暂无科技新闻"
        },
        "perspectives": [],
        "deep_analysis": [],
        "suggestions": {
            "thinking": {"title": "暂无", "content": "暂无相关思维启发"},
            "investment": {"title": "暂无", "content": "暂无相关投资建议"},
            "self_improvement": {"title": "暂无", "content": "暂无相关个人提升建议"},
            "opportunities_risks": {"title": "暂无", "content": "暂无相关机遇风险提示"}
        }
    }


# ============================================================================
# V2 Parser 解析工具（合并自 v2_parser.py）
# ============================================================================

def parse_ai_json_response(text: str) -> Dict[str, Any]:
    """
    解析 AI 输出的 JSON，带四层降级策略

    降级流程：
    1. 直接 JSON 解析
    2. 提取 Markdown 代码块中的 JSON
    3. 正则提取 JSON 片段
    4. 返回空结构 + 记录错误日志
    """
    # 第 1 层：直接解析
    result = _try_direct_parse(text)
    if result:
        print("JSON 解析成功：直接解析")
        return result

    # 第 2 层：提取 Markdown 代码块
    result = _try_markdown_extract(text)
    if result:
        print("JSON 解析成功：Markdown 代码块提取")
        return result

    # 第 3 层：正则提取 JSON 片段
    result = _try_regex_extract(text)
    if result:
        print("JSON 解析成功：正则提取")
        return result

    # 第 4 层：返回空结构
    print(f"JSON 解析全部失败，返回空结构。原始输出前 500 字符：{text[:500]}...")
    return get_empty_structure()


def _try_direct_parse(text: str) -> Optional[Dict[str, Any]]:
    """尝试直接 JSON 解析"""
    try:
        data = json.loads(text)
        # 验证基本结构 - 只要有 V2 schema 中的任意字段即可
        if isinstance(data, dict):
            required_any = ["summary", "key_news_brief", "briefing", "perspectives", "deep_analysis", "suggestions"]
            if any(field in data for field in required_any):
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
                # 只要有 V2 schema 中的任意字段即可
                if isinstance(data, dict):
                    required_any = ["summary", "key_news_brief", "briefing", "perspectives", "deep_analysis", "suggestions"]
                    if any(field in data for field in required_any):
                        return data
            except json.JSONDecodeError:
                continue
    return None


def _try_regex_extract(text: str) -> Optional[Dict[str, Any]]:
    """尝试用正则提取 JSON 对象"""
    # 从文本中提取所有可能的 JSON 对象
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


class AIAnalyzerV2:
    """V2.0.0 AI 分析器"""

    def __init__(self):
        self.api_url = settings.AI_API_URL
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL
        self.daily_analysis_dir = settings.DAILY_ANALYSIS_DIR

        # 创建分析目录
        os.makedirs(self.daily_analysis_dir, exist_ok=True)

        # 初始化 Prompt 模板
        self.prompts = self._init_prompts()

    def _init_prompts(self) -> Dict[str, str]:
        """初始化所有阶段的 Prompt 模板"""
        return {
            # 阶段 1：概要生成
            "stage1_summary": self._get_stage1_prompt(),
            # 阶段 2：观点生成
            "stage2_perspectives": self._get_stage2_prompt(),
            # 阶段 2 子任务：新闻摘要生成（单条）
            "stage2_news_summary": self._get_news_summary_prompt(),
            # 阶段 2 子任务：批量新闻摘要生成
            "stage2_batch_news_summary": self._get_batch_news_summary_prompt(),
            # 阶段 3：深度分析
            "stage3_deep_analysis": self._get_stage3_prompt(),
            # 阶段 4：建议生成
            "stage4_suggestions": self._get_stage4_prompt(),
        }

    def _get_stage1_prompt(self) -> str:
        """阶段 1：概要生成 Prompt"""
        return """
任务=分析以下新闻列表，生成结构化的 JSON 输出。

输出要求=必须严格输出纯 JSON，不要任何 Markdown 格式，不要任何额外说明。

输出结构={
  "summary": {
    "one_liner": "一句话总结（20-30 字，抽象理性简单）",
    "digest": "今日摘要（2-3 句话概括今天发生的事情）",
    "keywords": ["关键词 1", "关键词 2", "关键词 3"]
  },
  "key_news_brief": [
    {"title": "新闻标题", "tags": ["标签 1"]}
  ],
  "briefing": {
    "politics": "政治时事简报内容",
    "economy": "宏观经济简报内容",
    "industry": "行业动态简报内容",
    "tech": "科技新闻简报内容"
  },
  "key_news_list": [
    {"title": "标题", "content": "正文内容", "url": "链接", "source": "来源"}
  ]
}

字段说明:
- one_liner: 高度抽象的一句话总结，理性简洁，20-30 字
- digest: 描述今天发生的事件，2-3 句话
- keywords: 三个关键词，概括今日新闻主题
- key_news_brief: 3 个关键新闻，带标签，用于展示和阶段 3 分析
  - title 必须使用原始新闻标题，不能改写或缩写
- briefing: 四类新闻简报，每类 50-100 字（这是摘要文本，用于 AI 分类参考）
- key_news_list: 5-10 条重点新闻，包含完整标题 + 正文，用于阶段 2 观点生成
  - title 必须使用原始新闻标题，不能改写或缩写

标签选择=从以下预设标签库中选择 1-2 个标签：
""" + ", ".join(TAGS_LIBRARY) + """

注意事项:
- key_news_brief 固定 3 条，key_news_list 5-10 条，两者可以内容有重叠但用途不同
- key_news_brief 和 key_news_list 的 title 必须直接使用原始新闻标题，不能 AI 改写
- 所有字段必须存在，不能缺失
- JSON 格式必须正确，能被直接解析
"""

    def _get_news_summary_prompt(self) -> str:
        """阶段 2 子任务：为每条重点新闻生成摘要"""
        return """
任务=为以下新闻生成结构化摘要。

要求:
- 摘要长度控制在 100 字以内
- 保留新闻的核心信息（谁、做了什么、结果/影响）
- 语言简洁、客观
- 输出纯文本，不要任何格式

新闻标题：{title}
新闻正文：{content}

摘要:
"""

    def _get_batch_news_summary_prompt(self) -> str:
        """阶段 2 子任务：批量新闻摘要生成 Prompt"""
        return """
任务=批量为以下新闻列表生成摘要。

输入格式=新闻列表，每条新闻包含 title 和 content。

输出要求=必须严格输出纯 JSON 数组格式，不要任何 Markdown 格式。

输出结构=[
  {
    "title": "新闻标题",
    "summary": "新闻摘要（100 字以内）"
  },
  {
    "title": "新闻标题 2",
    "summary": "新闻摘要 2"
  }
]

摘要要求:
- 每条摘要长度控制在 100 字以内
- 保留新闻的核心信息（谁、做了什么、结果/影响）
- 语言简洁、客观
- JSON 数组长度必须与输入新闻数量一致

注意事项:
- JSON 格式必须正确，能被直接解析
- 不要遗漏任何一条新闻

新闻列表:
"""

    def _get_stage2_prompt(self) -> str:
        """阶段 2：观点生成 Prompt"""
        return """
任务=基于以下新闻摘要素材包，生成 3 个观点。

输出要求=必须严格输出纯 JSON，不要任何 Markdown 格式。

输出结构={
  "perspectives": [
    {
      "title": "观点标题",
      "description": "观点描述（200-300 字）",
      "references": [
        {"title": "引用文章标题 1", "url": "链接 1"},
        {"title": "引用文章标题 2", "url": "链接 2"}
      ]
    }
  ]
}

观点生成要求:
- 生成恰好 3 个观点
- 每个观点必须有独特的视角
- 观点要鲜明，不要模棱两可
- description 要论述清楚观点的核心内容
- references 从原始新闻中选择与观点最相关的 2 篇文章

注意事项:
- 所有字段必须存在
- JSON 格式必须正确
"""

    def _get_stage3_prompt(self) -> str:
        """阶段 3：深度分析 Prompt"""
        return """
任务=对以下关键事件进行深度分析。

输出要求=必须严格输出纯 JSON，不要任何 Markdown 格式。

输出结构={
  "deep_analysis": [
    {
      "tags": ["标签"],
      "title": "事件标题",
      "facts": "客观事实",
      "viewpoint": "整体观点",
      "causes": "发生原因",
      "prediction": "后续预测",
      "advice": "个体建议"
    }
  ]
}

分析框架:
- tags: 从预设标签库中选择 1-2 个
- title: 事件标题（一级标题格式）
- facts: 谁在什么场合/时间做了什么，背景是什么
- viewpoint: 重点/亮点/影响级别/好坏程度
- causes: 发生原因（主体 + 动机）
- prediction: 后续预测（观点鲜明）
- advice: 个体建议（投资/消费/就业/生活角度）

注意事项:
- 所有字段必须存在
- JSON 格式必须正确
"""

    def _get_stage4_prompt(self) -> str:
        """阶段 4：建议生成 Prompt"""
        return """
任务=基于以下分析结果，生成四类建议。

输出要求=必须严格输出纯 JSON，不要任何 Markdown 格式。

输出结构={
  "suggestions": {
    "thinking": {"title": "标题", "content": "内容"},
    "investment": {"title": "标题", "content": "内容"},
    "self_improvement": {"title": "标题", "content": "内容"},
    "opportunities_risks": {"title": "标题", "content": "内容"}
  }
}

建议生成要求:
- thinking: 思维启发，从新闻中获得的认知升级或思维角度
- investment: 投资建议，与新闻相关的投资机会或风险
- self_improvement: 个人提升，个人可以学习或提升的方向
- opportunities_risks: 机遇与风险，未来的机会和需要注意的风险

注意事项:
- 所有字段必须存在
- JSON 格式必须正确
"""

    def analyze_daily_news_v2(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        V2.0.0 四层分析主入口

        Args:
            news_items: 新闻列表

        Returns:
            完整的分析结果（符合 V2 Schema）
        """
        print("=" * 50)
        print("V2.0.0 四层分析开始")
        print("=" * 50)

        if not news_items:
            print("无新闻可分析，返回空结构")
            return get_empty_structure()

        start_time = time.time()
        result = get_empty_structure()

        try:
            # 阶段 1：概要生成
            stage1_result = self._stage1_summary(news_items)
            if stage1_result:
                result["summary"] = stage1_result.get("summary", {})
                result["key_news_brief"] = stage1_result.get("key_news_brief", [])
                result["briefing"] = stage1_result.get("briefing", {})
                key_news_list = stage1_result.get("key_news_list", [])
            else:
                key_news_list = []

            # 阶段 2：观点生成
            stage2_result = self._stage2_perspectives(key_news_list)
            if stage2_result:
                result["perspectives"] = stage2_result.get("perspectives", [])

            # 阶段 3：深度分析
            stage3_result = self._stage3_deep_analysis(result["key_news_brief"])
            if stage3_result:
                result["deep_analysis"] = stage3_result.get("deep_analysis", [])

            # 阶段 4：建议生成
            stage4_result = self._stage4_suggestions(result)
            if stage4_result:
                result["suggestions"] = stage4_result.get("suggestions", {})

            # 保存分析结果
            self._save_analysis(result)

            elapsed = time.time() - start_time
            print(f"\nV2.0.0 四层分析完成，耗时：{elapsed:.2f}秒")

            return result

        except Exception as e:
            print(f"分析失败：{e}")
            import traceback
            traceback.print_exc()
            return get_empty_structure()

    def _call_ai_api(self, prompt: str, system_prompt: str = "你是一个专业的新闻分析师") -> Optional[str]:
        """调用 AI API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "max_tokens": 4096
            }

            print(f"发送 AI 请求...")

            # 禁用代理自动检测，使用直连
            with httpx.Client(trust_env=False) as client:
                response = client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=settings.THIRD_LAYER_TIMEOUT
                )

            print(f"HTTP 响应状态：{response.status_code}")

            if response.status_code != 200:
                print(f"API 调用失败，状态码：{response.status_code}")
                print(f"响应内容：{response.text[:500]}...")
                return None

            response_data = response.json()
            content = response_data['choices'][0]['message']['content']
            print(f"AI 响应长度：{len(content)}")
            return content

        except Exception as e:
            print(f"调用 AI API 失败：{e}")
            return None

    def _stage1_summary(self, news_items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """阶段 1：概要生成"""
        print("\n--- 阶段 1：概要生成 ---")

        # 准备新闻数据
        news_text = self._format_news_for_prompt(news_items)
        prompt = self.prompts["stage1_summary"] + "\n\n新闻列表:\n" + news_text

        print(f"阶段 1 提示词长度：{len(prompt)}")

        # 调用 AI
        response = self._call_ai_api(prompt)
        if not response:
            print("阶段 1 失败")
            return None

        # 解析 JSON
        result = parse_ai_json_response(response)

        # 验证结构
        is_valid, errors = validate_v2_structure(result)
        if not is_valid:
            print(f"阶段 1 验证失败：{errors}")

        print(f"阶段 1 完成")
        return result

    def _stage2_perspectives(self, key_news_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """阶段 2：观点生成"""
        print("\n--- 阶段 2：观点生成 ---")

        if not key_news_list:
            print("无重点新闻，跳过阶段 2")
            return None

        # 步骤 1：批量生成新闻摘要（优化：1 次 API 调用替代多次）
        test_news = key_news_list[:10]  # 最多 10 条
        print(f"批量为 {len(test_news)} 条新闻生成摘要...")

        batch_result = self._generate_batch_news_summary(test_news)

        # 解析批量结果
        summaries = []
        references = []
        if batch_result:
            for item in batch_result:
                title = item.get("title", "未知标题")
                summary = item.get("summary", "")
                if summary:
                    summaries.append(summary)
                    references.append({"title": title, "url": test_news[0].get("url", "")})

        # 如果批量摘要失败，降级为单条生成
        if not summaries:
            print("批量摘要失败，降级为单条生成...")
            for news in test_news:
                summary = self._generate_news_summary(news)
                if summary:
                    summaries.append(summary)
                    references.append({
                        "title": news.get("title", "未知标题"),
                        "url": news.get("url", "")
                    })

        # 步骤 2：汇总摘要形成素材包
        summary_package = "\n---\n".join(summaries)
        print(f"观点素材包长度：{len(summary_package)}")

        # 步骤 3：生成观点
        prompt = self.prompts["stage2_perspectives"] + "\n\n新闻摘要素材包:\n" + summary_package
        prompt += "\n\n引用文章列表:\n" + json.dumps(references, ensure_ascii=False, indent=2)

        response = self._call_ai_api(prompt)
        if not response:
            print("阶段 2 失败")
            return None

        result = parse_ai_json_response(response)

        # 补充引用（如果 AI 输出的 references 为空）
        if "perspectives" in result:
            for perspective in result["perspectives"]:
                if not perspective.get("references"):
                    perspective["references"] = references[:2]

        print(f"阶段 2 完成")
        return result

    def _generate_news_summary(self, news: Dict[str, Any]) -> Optional[str]:
        """为单条新闻生成摘要"""
        try:
            title = news.get("title", "")
            content = news.get("content", "")

            if not content:
                return title

            prompt = self.prompts["stage2_news_summary"].format(
                title=title,
                content=content[:1000]  # 限制长度
            )

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "max_tokens": 200
            }

            with httpx.Client(trust_env=False) as client:
                response = client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

            if response.status_code == 200:
                data = response.json()
                summary = data['choices'][0]['message']['content']
                return summary.strip()

        except Exception as e:
            print(f"生成新闻摘要失败：{e}")

        return None

    def _generate_batch_news_summary(self, news_list: List[Dict[str, Any]]) -> Optional[List[Dict[str, str]]]:
        """批量生成新闻摘要（优化：1 次 API 调用处理多条新闻）"""
        try:
            # 构建输入文本
            input_text = ""
            for i, news in enumerate(news_list, 1):
                title = news.get("title", "未知标题")
                content = news.get("content", "")[:500]  # 限制长度
                input_text += f"{i}. 标题：{title}\n   内容：{content}\n\n"

            prompt = self.prompts["stage2_batch_news_summary"] + "\n" + input_text

            # 直接调用 API（不经过 parse_ai_json_response，因为它会尝试匹配 V2 schema）
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "max_tokens": 2000
            }

            print("发送批量摘要请求...")
            with httpx.Client(trust_env=False) as client:
                response = client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )

            if response.status_code != 200:
                print(f"批量摘要 API 失败：{response.status_code}")
                return None

            response_text = response.json()['choices'][0]['message']['content']

            # 尝试直接解析 JSON 数组
            try:
                result = json.loads(response_text)
                if isinstance(result, list):
                    print(f"批量摘要成功：获得 {len(result)} 条摘要")
                    return result
                elif isinstance(result, dict) and "summaries" in result:
                    # 处理包装格式
                    print(f"批量摘要成功：获得 {len(result['summaries'])} 条摘要")
                    return result["summaries"]
            except json.JSONDecodeError:
                pass

            # 尝试从 Markdown 代码块提取
            import re
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
            if match:
                json_text = match.group(1).strip()
                try:
                    result = json.loads(json_text)
                    if isinstance(result, list):
                        print(f"批量摘要成功（Markdown 提取）：获得 {len(result)} 条摘要")
                        return result
                except json.JSONDecodeError:
                    pass

            print("批量摘要解析失败：无法提取 JSON 数组")
            return None

        except Exception as e:
            print(f"批量生成摘要失败：{e}")

        return None

    def _stage3_deep_analysis(self, key_news_brief: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """阶段 3：深度分析"""
        print("\n--- 阶段 3：深度分析 ---")

        if not key_news_brief:
            print("无关键新闻，跳过阶段 3")
            return None

        # 取前 3 条关键新闻
        events_to_analyze = key_news_brief[:3]
        print(f"分析 {len(events_to_analyze)} 个关键事件...")

        deep_analyses = []

        for event in events_to_analyze:
            analysis = self._analyze_single_event(event)
            if analysis:
                deep_analyses.append(analysis)

        print(f"阶段 3 完成，获得 {len(deep_analyses)} 个分析结果")
        return {"deep_analysis": deep_analyses}

    def _analyze_single_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """分析单个事件"""
        try:
            prompt = self.prompts["stage3_deep_analysis"] + "\n\n关键事件:\n"
            prompt += f"标题：{event.get('title', '未知')}\n"
            prompt += f"标签：{event.get('tags', [])}\n"

            response = self._call_ai_api(prompt)
            if not response:
                return None

            result = parse_ai_json_response(response)

            if "deep_analysis" in result and len(result["deep_analysis"]) > 0:
                return result["deep_analysis"][0]

        except Exception as e:
            print(f"分析单个事件失败：{e}")

        return None

    def _stage4_suggestions(self, partial_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """阶段 4：建议生成"""
        print("\n--- 阶段 4：建议生成 ---")

        # 汇总已有信息
        context = self._build_stage4_context(partial_result)

        prompt = self.prompts["stage4_suggestions"] + "\n\n分析上下文:\n" + context

        response = self._call_ai_api(prompt)
        if not response:
            print("阶段 4 失败")
            return None

        result = parse_ai_json_response(response)
        print(f"阶段 4 完成")
        return result

    def _build_stage4_context(self, partial_result: Dict[str, Any]) -> str:
        """构建阶段 4 的上下文"""
        context = ""

        if "summary" in partial_result:
            context += "今日摘要:\n"
            context += f"一句话：{partial_result['summary'].get('one_liner', '')}\n"
            context += f"关键词：{partial_result['summary'].get('keywords', [])}\n\n"

        if "perspectives" in partial_result:
            context += "观点:\n"
            for p in partial_result["perspectives"]:
                context += f"- {p.get('title', '')}: {p.get('description', '')}\n"
            context += "\n"

        if "deep_analysis" in partial_result:
            context += "深度分析:\n"
            for a in partial_result["deep_analysis"]:
                context += f"- {a.get('title', '')}: {a.get('viewpoint', '')}\n"

        return context

    def _format_news_for_prompt(self, news_items: List[Dict[str, Any]]) -> str:
        """格式化新闻为 Prompt 文本"""
        text = ""
        for i, news in enumerate(news_items[:50]):  # 最多 50 条
            text += f"{i+1}. 标题：{news.get('title', '未知')}\n"
            text += f"   来源：{news.get('source', '未知')}\n"
            text += f"   内容：{news.get('content', '')[:300]}...\n\n"
        return text

    def _save_analysis(self, result: Dict[str, Any]):
        """保存分析结果"""
        date = datetime.now().strftime('%Y-%m-%d')

        # 保存 JSON
        json_path = os.path.join(self.daily_analysis_dir, f"{date}_v2.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存：{json_path}")


if __name__ == "__main__":
    # 测试
    print("V2.0.0 AI 分析模块测试")
    analyzer = AIAnalyzerV2()
    print("V2 分析器初始化完成")
