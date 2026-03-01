import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from news_fetcher import NewsFetcher
from config import settings


class AIAnalyzer:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.daily_analysis_dir = settings.DAILY_ANALYSIS_DIR

        # 创建分析目录
        os.makedirs(self.daily_analysis_dir, exist_ok=True)

        # 初始化提示词
        self.prompts = {
            "system": "你是一个专业的新闻分析师，请分析以下新闻，提供摘要、关键词和情感分析。",
            "user": "请分析以下新闻，提供摘要、关键词和情感分析：\n\n标题：{title}\n\n内容：{content}...",
            "first_layer": """
任务=请根据给定的分析框架，分析以下新闻标题，生成一份专业的新闻摘要报告。

分析框架=需要按照这个框架来分析：
- 今日摘要
- 政治时事
- 宏观经济
- 行业动态：
    - 行业政策
    - 技术突破
    - 供需变化
    - 行业龙头动态
- 科技新闻：
    - 前沿科技
    - 消费电子
    - 互联网与软件
- 关键事件

优化检查清单：
- 用 markdown 输出
- 今日摘要、政治时事、宏观经济、行业动态、科技新闻和关键事件用二级标题，其余用正文或者列表输出
- 「关键事件」标题下的事件用「-」作为开头的无序列表，根据政治、经济、科技、商业等维度选出 3 个即可
- 如果某部分缺乏新闻，则输出「暂无新闻」
- 「今日摘要」用简洁的语言整体地描述发生了什么，不用进行分类，字数尽量在 20-30 字即可
- 只需要输出框架规定的内容，不要擅自在前面或者后面加上标题、说明之类的
- 不要使用任何加粗/斜体等的样式语法
- 在「行业动态」和「科技新闻」这两个部分的二级标题下的结构使用三级标题，例如「行业动态」中的「行业政策」等

关键事件输出要求（必须严格遵守）：
- 从政治、经济、科技、商业等维度中，筛选出最重要的 3 个事件
- 每个事件必须是新闻中真实提到的，不要杜撰任何原文未提及的内容
- 每个事件可以用 25-35 字概括，格式统一
- 严格按以下格式输出：
## 关键事件
- 事件描述
- 事件描述
- 事件描述
""",
            "second_layer": """
任务=请结合以下新闻事件和搜索结果，使用给定的分析框架对事件进行分析。

分析框架：

[填入新闻事件标题]（这里需要用一级标题）

一、客观事实
1. 讲述清楚谁在什么场合/时间，做了/发生了什么。
2. 这件事情的背景是什么

二、整体观点
1. 新闻重点或者亮点是什么？
2. 新闻的影响级别是什么？
3. 新闻的好坏程度如何？（好、坏、中性、有无风险、不值得关注等等）
4. 发生新闻最主要的原因是什么？（最直接的驱动因素）
5. 读者看到新闻以后最应该做什么？

三、事情发生原因
1. 有明确主体的新闻：人、公司、行业组织、政府监管等；对分析这类新闻来说，最重要的就是——寻找动机。
2. 没有明确主体的新闻：数据指标、客观事件等；

四、事情后续发展预测
1. 根据过去、现在的信息，预测事情的走向，不要追求四平八稳，而是要观点鲜明

五、个体能做什么
可以从多角度出发，如投资、消费、就业、生活

要求：
- 输出时，严格按照这 6 大部份的标题作为结构输出，每个结构的标题使用二级标题
- 只需要框架规定的内容，不要擅自增加标题或者说明或其他结构
- 以 markdown 格式输出，不要擅自加入代码块
- 检查输出的结构是否完整
- 输出的第一行必须是新闻事件的扼要标题，用一级标题的格式输出；但不要显示「填入新闻事件标题」这几个字，而是用真实的标题去填充
""",
            "third_layer": """
任务=请结合以下新闻摘要和重点新闻分析，从指定角度思考综合而全面的洞察和建议。

需要从以下四个结构进行思考：
- 思维启发
- 投资建议
- 个人提升
- 机遇与风险

要求：
- 输出时，严格按照要求使用 markdown 格式
- 四大部份的标题使用二级标题
- 标题部分不需要加粗

优化检查清单：
1. 四大部分是否使用了二级标题？
            """
        }

        # 初始化 Tavily 客户端
        self.tavily_client = self._setup_tavily_client()

    def analyze_daily_news(self, news_items=None) -> Dict[str, Any]:
        """分析每日新闻"""
        print("开始每日新闻分析...")

        # 获取今日新闻（如果未提供）
        if news_items is None:
            news_items = self.news_fetcher.get_recent_news(days=1)

        if not news_items:
            print("今日无新闻可分析")
            return {}

        # 保持完整分析，不限制新闻数量
        print(f"共 {len(news_items)} 条新闻待分析")

        # 批量分析
        print("开始批量分析...")
        start_time = time.time()

        # 添加进度显示
        print(f"正在进行三层分析 {len(news_items)} 条新闻，这可能需要一些时间...")
        print("实时状态：连接 DeepSeek API 中...")

        analysis_results = self._batch_analyze_news(news_items)

        end_time = time.time()
        print(f"三层分析完成，耗时 {end_time - start_time:.2f} 秒")

        # 生成分析报告
        print("生成分析报告...")
        analysis_report = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "first_layer": analysis_results.get("first_layer", "# 整体分析\n\n分析失败"),
            "second_layer": analysis_results.get("second_layer", []),
            "third_layer": analysis_results.get("third_layer", "# 综合分析\n\n分析失败"),
            "daily_summary": analysis_results.get("third_layer", "# 综合分析\n\n分析失败"),
            "event_analysis": analysis_results.get("first_layer", "# 整体分析\n\n分析失败"),
            "detailed_analysis": analysis_results.get("second_layer", []),
            "timestamp": datetime.now().isoformat(),
            "news_count": len(news_items)
        }

        # 保存分析结果
        self._save_daily_analysis(analysis_report)

        # 保存 Markdown 格式的完整报告
        self._save_analysis_results(analysis_results, analysis_report["date"])

        print("每日新闻分析完成")
        return analysis_report

    def _batch_analyze_news(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量分析新闻"""
        try:
            total_news = len(news_items)
            print(f"准备分析 {total_news} 条新闻...")

            # 使用三层分析流程
            analysis_results = self._three_layer_analysis(news_items)

            print(f"三层分析完成，获得完整分析结果")
            return analysis_results

        except Exception as e:
            print(f"批量分析失败：{e}")
            # 备用方案：返回模拟分析结果
            return {
                "first_layer": "# 整体摘要分析\n\n分析失败，使用备用方案。",
                "second_layer": ["# 分析失败\n\n备用方案" for _ in range(3)],
                "third_layer": "# 综合分析\n\n分析失败，使用备用方案。"
            }

    def _preprocess_news(self, news_items: List[Dict[str, Any]]) -> str:
        """预处理新闻数据"""
        news_titles = [news['title'] for news in news_items]
        return self._format_news_as_markdown(news_titles)

    def _format_news_as_markdown(self, news_titles: List[str]) -> str:
        """将新闻标题格式化为 Markdown 列表"""
        markdown = ""
        for title in news_titles:
            markdown += f"- {title}\n"
        return markdown

    def _three_layer_analysis(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """三层分析主方法"""
        print("开始三层分析...")

        # 1. 预处理
        print("1. 预处理新闻数据...")
        news_markdown = self._preprocess_news(news_items)
        print(f"预处理完成，共 {len(news_items)} 条新闻")

        # 2. 第一层分析
        print("2. 第一层分析：整体摘要分析...")
        first_layer_result = self._first_layer_analysis(news_markdown)
        print("第一层分析完成")

        # 3. 提取关键事件（带降级策略）
        print("3. 提取关键事件...")

        # 第一步：规则提取
        key_events = self._extract_key_events(first_layer_result)

        # 第二步：如果规则提取失败，使用 AI 提取
        if not key_events:
            print("规则提取未获得有效事件，尝试 AI 提取...")
            key_events = self._ai_extract_key_events(first_layer_result)

        # 第三步：如果 AI 提取也失败，则无关键事件
        if not key_events:
            print("警告：所有提取方式均失败，将跳过第二层分析")
        else:
            print(f"成功提取 {len(key_events)} 个关键事件")

        print(f"最终关键事件数量：{len(key_events)}")

        # 4. 第二层分析（并行）
        print("4. 第二层分析：关键事件深度分析（并行）...")
        second_layer_results = self._second_layer_analysis(key_events)
        print(f"第二层分析完成，共分析 {len(second_layer_results)} 个关键事件")

        # 5. 第三层分析
        print("5. 第三层分析：综合分析...")
        third_layer_result = self._third_layer_analysis(first_layer_result, second_layer_results)
        print("第三层分析完成")

        return {
            "first_layer": first_layer_result,
            "second_layer": second_layer_results,
            "third_layer": third_layer_result
        }

    def _first_layer_analysis(self, news_markdown: str) -> str:
        """第一层整体摘要分析"""
        try:
            import httpx

            # 构建提示词
            prompt = self.prompts["first_layer"] + "\n\n" + news_markdown
            print(f"构建第一层分析提示词，长度：{len(prompt)}")

            # 直接使用 HTTP 请求调用 API
            print("发送第一层分析请求...")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.AI_API_KEY}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个专业的新闻分析师"},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "max_tokens": 4096
            }

            # 创建自定义的 HTTP 客户端，不使用 proxies 参数
            with httpx.Client() as client:
                response = client.post(
                    settings.AI_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=90.0
                )

            print(f"HTTP 响应状态：{response.status_code}")

            if response.status_code != 200:
                print(f"API 调用失败，状态码：{response.status_code}")
                print(f"响应内容：{response.text}")
                # 备用方案
                return "# 整体摘要分析\n\n## 整体摘要\n分析失败，使用备用方案。\n\n## 新闻分类\n- 综合新闻\n- 未分类\n\n## 关键事件\n- 分析失败"

            # 解析响应
            response_data = response.json()
            result = response_data['choices'][0]['message']['content']
            print(f"第一层分析完成，结果长度：{len(result)}")
            print(f"第一层分析结果前 200 字符：{result[:200]}...")

            return result
        except Exception as e:
            print(f"第一层分析失败：{e}")
            import traceback
            traceback.print_exc()
            # 备用方案
            return "# 整体摘要分析\n\n## 整体摘要\n分析失败，使用备用方案。\n\n## 新闻分类\n- 综合新闻\n- 未分类\n\n## 关键事件\n- 分析失败"

    def _extract_key_events(self, first_layer_result: str) -> List[str]:
        """从第一层结果中提取关键事件 - 支持多种格式"""
        try:
            print("开始提取关键事件...")
            print(f"第一层分析结果长度：{len(first_layer_result)}")

            lines = first_layer_result.split('\n')
            key_events = []
            capture = False

            # 支持的列表前缀
            list_prefixes = ['- ', '• ', '· ', '* ']

            for line in lines:
                line_stripped = line.strip()

                if not capture:
                    # 检测关键事件标题（支持多种写法）
                    if '关键事件' in line_stripped and line_stripped.startswith('#'):
                        capture = True
                        print(f"找到关键事件标题：{line_stripped}")
                        continue
                else:
                    # 遇到新的大标题则停止（但不是关键事件标题）
                    if line_stripped.startswith('#') and '关键事件' not in line_stripped:
                        print(f"遇到下一个标题，停止捕获：{line_stripped}")
                        break

                    # 尝试多种列表前缀
                    for prefix in list_prefixes:
                        if line_stripped.startswith(prefix):
                            event = line_stripped[len(prefix):].strip()
                            # 过滤空内容和过短内容
                            if event and len(event) > 10:
                                key_events.append(event)
                                print(f"提取到事件：{event}")
                            break

            # 去重（保留顺序）
            seen = set()
            unique_events = []
            for event in key_events:
                event_lower = event.lower()
                if event_lower not in seen:
                    seen.add(event_lower)
                    unique_events.append(event)

            print(f"提取完成，共获得 {len(unique_events)} 个唯一事件")
            return unique_events

        except Exception as e:
            print(f"提取关键事件失败：{e}")
            import traceback
            traceback.print_exc()
            return []

    def _ai_extract_key_events(self, first_layer_result: str) -> List[str]:
        """使用 AI 提取关键事件 - 降级方案（仅在规则提取失败时调用）"""
        try:
            print("规则提取失败，使用 AI 降级提取...")
            import httpx

            # 构建提示词：强调从多维度筛选，严格限制 3 个事件
            prompt = f"""你是一个专业的新闻编辑，请从以下新闻分析结果中提取最关键的事件。

提取要求：
1. 从政治、经济、科技、商业、金融等维度综合评估，选出最重要的 3 个事件
2. 只输出 3 个事件，不多不少
3. 事件必须是原文中真实提到的，绝对不要杜撰任何原文未提及的内容
4. 每个事件用 25-35 字概括，保持信息完整

输出格式（必须严格遵守）：
- 事件描述
- 事件描述
- 事件描述

例如：
- 某国总统宣布某项重大经济政策
- 央行宣布降息 25 个基点
- 某公司发布新一代人工智能芯片

以下是新闻分析结果：
=====================================
{first_layer_result[:4000]}
=====================================

请提取 3 个关键事件（严格按格式输出，不要其他说明）："""

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.AI_API_KEY}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "max_tokens": 300
            }

            print("发送 AI 提取请求...")

            with httpx.Client() as client:
                response = client.post(
                    settings.AI_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )

            print(f"AI 提取响应状态：{response.status_code}")

            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
                print(f"AI 提取结果：{result[:300]}...")

                # 解析结果
                events = []
                for line in result.split('\n'):
                    line = line.strip()
                    if line.startswith('- '):
                        event = line[2:].strip()
                        if event and len(event) > 10:
                            events.append(event)

                print(f"AI 提取解析后获得 {len(events)} 个事件")
                return events[:3]  # 确保最多 3 个
            else:
                print(f"AI 提取失败，状态码：{response.status_code}")
                return []

        except Exception as e:
            print(f"AI 提取失败：{e}")
            import traceback
            traceback.print_exc()
            return []

    def _second_layer_analysis(self, key_events: List[str]) -> List[str]:
        """并行分析关键事件 - 支持动态数量"""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        # 处理无事件情况
        if not key_events:
            print("无关键事件可分析，跳过第二层分析")
            return []

        print(f"收到关键事件：{key_events}")

        # 最多处理 3 个事件
        events_to_analyze = key_events[:3]

        print(f"并行分析 {len(events_to_analyze)} 个关键事件...")

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_event = {
                executor.submit(self._enhanced_event_analysis, event): event
                for event in events_to_analyze
            }

            for future in as_completed(future_to_event):
                event = future_to_event[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"完成事件分析：{event[:50]}...")
                except Exception as e:
                    print(f"分析事件失败 {event[:50]}...: {e}")
                    results.append(f"# 分析失败\n\n{str(e)}")

        print(f"第二层分析完成，共获得 {len(results)} 个分析结果")
        return results

    def _analyze_single_event(self, event: str) -> str:
        """分析单个关键事件"""
        try:
            import httpx

            # 构建提示词
            prompt = self.prompts["second_layer"] + "\n\n事件：" + event

            # 直接使用 HTTP 请求调用 API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.AI_API_KEY}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个专业的新闻分析师"},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "max_tokens": 4096
            }

            # 创建自定义的 HTTP 客户端，不使用 proxies 参数
            with httpx.Client() as client:
                response = client.post(
                    settings.AI_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=90.0
                )

            print(f"HTTP 响应状态：{response.status_code}")

            if response.status_code != 200:
                print(f"API 调用失败，状态码：{response.status_code}")
                print(f"响应内容：{response.text}")
                return f"# 分析失败\n\nAPI 调用失败，状态码：{response.status_code}"

            # 解析响应
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        except Exception as e:
            print(f"分析单个事件失败：{e}")
            return f"# 分析失败\n\n{str(e)}"

    def _third_layer_analysis(self, first_layer_result: str, second_layer_results: List[str]) -> str:
        """第三层综合分析"""
        try:
            import httpx
            import time

            # 获取配置参数
            max_retries = settings.THIRD_LAYER_RETRIES
            timeout = settings.THIRD_LAYER_TIMEOUT
            initial_delay = settings.THIRD_LAYER_RETRY_DELAY

            # 构建完整提示词（包含第二层分析）
            def build_full_prompt():
                prompt = self.prompts["third_layer"] + "\n\n"
                prompt += "# 第一层分析结果\n" + first_layer_result + "\n\n"
                prompt += "# 第二层分析结果\n"
                for i, result in enumerate(second_layer_results):
                    prompt += f"## 事件 {i+1} 分析\n" + result + "\n\n"
                return prompt

            # 构建简化提示词（只包含第一层分析）
            def build_simple_prompt():
                prompt = self.prompts["third_layer"] + "\n\n"
                prompt += "# 第一层分析结果\n" + first_layer_result + "\n\n"
                prompt += "# 第二层分析结果\n"
                prompt += "## 事件分析\n分析失败，使用第一层分析结果进行综合分析。\n\n"
                return prompt

            # 发送请求的函数
            def send_request(prompt_content):
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.AI_API_KEY}"
                }

                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一个专业的新闻分析师"},
                        {"role": "user", "content": prompt_content}
                    ],
                    "stream": False,
                    "max_tokens": 4096
                }

                # 创建自定义的 HTTP 客户端，不使用 proxies 参数
                with httpx.Client() as client:
                    response = client.post(
                        settings.AI_API_URL,
                        headers=headers,
                        json=payload,
                        timeout=timeout
                    )

                print(f"HTTP 响应状态：{response.status_code}")

                if response.status_code != 200:
                    print(f"API 调用失败，状态码：{response.status_code}")
                    print(f"响应内容：{response.text}")
                    raise Exception(f"API 调用失败，状态码：{response.status_code}")

                # 解析响应
                response_data = response.json()
                return response_data['choices'][0]['message']['content']

            # 第一次尝试：使用完整提示词
            prompt = build_full_prompt()
            print(f"发送第三层分析请求（完整提示词）...")
            print(f"超时时间：{timeout}秒，最多重试 {max_retries} 次")

            # 实现重试逻辑
            for attempt in range(max_retries):
                try:
                    print(f"尝试 {attempt+1}/{max_retries}...")
                    result = send_request(prompt)
                    print(f"第三层分析成功（尝试 {attempt+1}/{max_retries}）")
                    return result
                except Exception as e:
                    print(f"尝试 {attempt+1} 失败：{e}")
                    if attempt < max_retries - 1:
                        # 指数退避策略
                        delay = initial_delay * (2 ** attempt)
                        print(f"{delay}秒后进行下一次尝试...")
                        time.sleep(delay)
                    else:
                        print(f"所有 {max_retries} 次尝试都失败")

            # 所有尝试都失败，降级为使用简化提示词（只包含第一层分析）
            print("降级策略：使用简化提示词（只包含第一层分析）...")
            simple_prompt = build_simple_prompt()

            # 对简化提示词进行最后一次尝试
            try:
                result = send_request(simple_prompt)
                print("简化提示词分析成功")
                return result
            except Exception as e:
                print(f"简化提示词分析也失败：{e}")
                # 最终备用方案
                return "# 综合分析\n\n分析失败，使用备用方案。"

        except Exception as e:
            print(f"第三层分析失败：{e}")
            import traceback
            traceback.print_exc()
            # 备用方案
            return "# 综合分析\n\n分析失败，使用备用方案。"

    def _save_daily_analysis(self, analysis: Dict[str, Any]):
        """保存每日分析结果"""
        date = analysis['date']
        file_path = os.path.join(self.daily_analysis_dir, f"{date}.json")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        print(f"每日分析结果已保存：{file_path}")

    def _save_analysis_results(self, analysis_results: Dict[str, Any], date: str):
        """保存 Markdown 格式的完整分析报告"""
        # 确保报告目录存在
        report_dir = os.path.join(self.daily_analysis_dir, "reports")
        os.makedirs(report_dir, exist_ok=True)

        # 构建完整的 Markdown 报告
        markdown_report = "# 三层新闻分析报告\n\n"
        markdown_report += f"生成时间：{datetime.now().isoformat()}\n"
        markdown_report += f"分析新闻数量：{len(analysis_results.get('second_layer', []))}\n\n"

        # 添加第一层分析结果
        markdown_report += "## Summary 是日要闻\n\n"
        markdown_report += analysis_results.get("first_layer", "分析失败") + "\n\n"

        # 添加第二层分析结果
        markdown_report += "## Advanced 深度分析\n\n"
        for event_analysis in analysis_results.get("second_layer", []):
            markdown_report += event_analysis + "\n\n"

        # 添加第三层分析结果
        markdown_report += "## Insights 洞察建议\n\n"
        markdown_report += analysis_results.get("third_layer", "分析失败") + "\n"

        # 保存为 Markdown 文件
        md_file_path = os.path.join(report_dir, f"{date}.md")
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)

        print(f"Markdown 分析报告已保存：{md_file_path}")

    def clean_old_analysis(self):
        """清理过期的分析数据"""
        # 清理 2 个月前的每日分析数据
        threshold_date = datetime.now() - timedelta(days=60)

        for filename in os.listdir(self.daily_analysis_dir):
            if filename.endswith('.json'):
                try:
                    file_date = datetime.strptime(filename[:-5], '%Y-%m-%d')
                    if file_date < threshold_date:
                        file_path = os.path.join(self.daily_analysis_dir, filename)
                        os.remove(file_path)
                        print(f"删除过期每日分析文件：{filename}")
                except Exception as e:
                    print(f"清理每日分析文件失败 {filename}: {e}")

    def _setup_tavily_client(self):
        """初始化 Tavily 客户端"""
        try:
            from tavily import TavilyClient
            api_key = settings.TAVILY_API_KEY
            if not api_key:
                print("Tavily API 密钥未配置")
                return None
            client = TavilyClient(api_key=api_key)
            print("Tavily 客户端初始化成功")
            return client
        except Exception as e:
            print(f"初始化 Tavily 客户端失败：{e}")
            return None

    def _generate_search_query(self, event: str) -> str:
        """生成更精准的搜索查询词"""
        # 提取事件的核心部分，去除问号、感叹号等标点
        core_event = event.replace('？', '').replace('！', '').strip()
        # 添加关键词，提高搜索精准度
        query = f"{core_event} 最新消息 背景 原因 影响 时间线 利益 专家观点"
        return query

    def _search_with_tavily(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """使用 Tavily 执行搜索"""
        try:
            if not self.tavily_client:
                print("Tavily 客户端未初始化，跳过搜索")
                return []

            print(f"使用 Tavily 搜索：{query[:50]}...")
            results = self.tavily_client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced"
            )

            # 提取有用的信息
            search_results = []
            for result in results.get("results", []):
                search_results.append({
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "content": result.get("content")
                })

            print(f"Tavily 搜索完成，获得 {len(search_results)} 个结果")
            return search_results
        except Exception as e:
            print(f"Tavily 搜索失败：{e}")
            return []

    def _enhanced_event_analysis(self, event: str) -> str:
        """使用 Tavily 搜索增强事件分析"""
        try:
            print(f"开始增强事件分析：{event}")

            # 生成更精准的搜索查询词
            search_query = self._generate_search_query(event)
            print(f"生成搜索查询：{search_query}")

            # 使用 Tavily 搜索相关信息
            search_results = self._search_with_tavily(search_query)
            print(f"搜索结果数量：{len(search_results)}")

            # 构建增强的分析提示词
            enhanced_prompt = self.prompts["second_layer"] + "\n\n事件：" + event
            print(f"构建增强提示词，长度：{len(enhanced_prompt)}")

            if search_results:
                enhanced_prompt += "\n\n相关信息：\n"
                for i, result in enumerate(search_results):
                    enhanced_prompt += f"{i+1}. [{result['title']}]({result['url']})\n"
                    if result['content']:
                        enhanced_prompt += f"   摘要：{result['content'][:200]}...\n"

            # 直接使用 HTTP 请求调用 API
            import httpx

            print("发送增强事件分析请求...")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.AI_API_KEY}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个专业的新闻分析师"},
                    {"role": "user", "content": enhanced_prompt}
                ],
                "stream": False,
                "max_tokens": 4096
            }

            # 创建自定义的 HTTP 客户端，不使用 proxies 参数
            with httpx.Client() as client:
                response = client.post(
                    settings.AI_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=90.0
                )

            print(f"HTTP 响应状态：{response.status_code}")

            if response.status_code != 200:
                print(f"API 调用失败，状态码：{response.status_code}")
                print(f"响应内容：{response.text}")
                # 回退到普通分析
                print("回退到普通分析")
                return self._analyze_single_event(event)

            # 解析响应
            response_data = response.json()
            result = response_data['choices'][0]['message']['content']
            print(f"增强事件分析完成，结果长度：{len(result)}")
            return result
        except Exception as e:
            print(f"增强事件分析失败：{e}")
            import traceback
            traceback.print_exc()
            # 回退到普通分析
            print("回退到普通分析")
            return self._analyze_single_event(event)


if __name__ == "__main__":
    # 测试每日分析
    analyzer = AIAnalyzer()
    daily_analysis = analyzer.analyze_daily_news()
    print(f"每日分析完成：{daily_analysis.get('date', '未知')}")

    # 清理过期分析数据
    analyzer.clean_old_analysis()
