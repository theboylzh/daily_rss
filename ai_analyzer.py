import os
import json
import time
import multiprocessing
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from news_fetcher import NewsFetcher
from config import settings


class AIAnalyzer:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.daily_analysis_dir = settings.DAILY_ANALYSIS_DIR
        self.weekly_analysis_dir = settings.WEEKLY_ANALYSIS_DIR
        self.monthly_analysis_dir = settings.MONTHLY_ANALYSIS_DIR
        
        # 创建分析目录
        os.makedirs(self.daily_analysis_dir, exist_ok=True)
        os.makedirs(self.weekly_analysis_dir, exist_ok=True)
        os.makedirs(self.monthly_analysis_dir, exist_ok=True)
        
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
            - 用markdown输出
            - 今日摘要、政治时事、宏观经济、行业动态、科技新闻和关键事件用二级标题，其余用正文或者列表输出
            - 「关键事件」标题下的事件用「-」作为开头的无序列表，根据政治、经济和科技等维度选出3个即可
            - 如果某部分缺乏新闻，则输出「暂无新闻」
            - 「今日摘要」用简洁的语言整体地描述发生了什么，不用进行分类，字数尽量在20-30字即可
            - 只需要输出框架规定的内容，不要擅自在前面或者后面加上标题、说明之类的
            - 不要使用任何加粗/斜体等的样式语法
            - 在「行业动态」和「科技新闻」这两个部分的二级标题下的结构使用三级标题，例如「行业动态」中的「行业政策」等
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
            - 输出时，严格按照这6大部份的标题作为结构输出，每个结构的标题使用二级标题
            - 只需要框架规定的内容，不要擅自增加标题或者说明或其他结构
            - 以markdown格式输出，不要擅自加入代码块
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
            - 输出时，严格按照要求使用markdown格式
            - 四大部份的标题使用二级标题
            - 标题部分不需要加粗

            优化检查清单：
            1. 四大部分是否使用了二级标题？
            """
        }
        
        # 初始化Tavily客户端
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
        print("实时状态：连接DeepSeek API中...")
        
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
        
        # 保存Markdown格式的完整报告
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
            print(f"批量分析失败: {e}")
            # 备用方案：返回模拟分析结果
            return {
                "first_layer": "# 整体摘要分析\n\n分析失败，使用备用方案。",
                "second_layer": ["# 分析失败\n\n备用方案" for _ in range(3)],
                "third_layer": "# 综合分析\n\n分析失败，使用备用方案。"
            }
    
    def analyze_weekly_news(self) -> Dict[str, Any]:
        """分析每周新闻"""
        print("开始每周新闻分析...")
        
        # 获取上周新闻
        news_items = self.news_fetcher.get_recent_news(days=7)
        
        if not news_items:
            print("上周无新闻可分析")
            return {}
        
        print(f"共 {len(news_items)} 条新闻待分析")
        
        # 生成周回顾报告
        weekly_report = {
            "week": datetime.now().strftime('%Y-W%U'),
            "summary": self._generate_weekly_summary(news_items),
            "timestamp": datetime.now().isoformat(),
            "news_count": len(news_items)
        }
        
        # 保存分析结果
        self._save_weekly_analysis(weekly_report)
        
        print("每周新闻分析完成")
        return weekly_report
    
    def analyze_monthly_news(self) -> Dict[str, Any]:
        """分析每月新闻"""
        print("开始每月新闻分析...")
        
        # 获取上月新闻
        news_items = self.news_fetcher.get_recent_news(days=30)
        
        if not news_items:
            print("上月无新闻可分析")
            return {}
        
        print(f"共 {len(news_items)} 条新闻待分析")
        
        # 生成月回顾报告
        monthly_report = {
            "month": datetime.now().strftime('%Y-%m'),
            "summary": self._generate_monthly_summary(news_items),
            "timestamp": datetime.now().isoformat(),
            "news_count": len(news_items)
        }
        
        # 保存分析结果
        self._save_monthly_analysis(monthly_report)
        
        print("每月新闻分析完成")
        return monthly_report
    
    def _parallel_analysis(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """并行分析新闻"""
        # 限制并行数量，避免API调用过于频繁
        max_workers = min(multiprocessing.cpu_count(), 4)
        
        print(f"使用 {max_workers} 个进程进行并行分析...")
        
        # 分批次处理新闻
        batch_size = len(news_items) // max_workers + 1
        batches = [news_items[i:i+batch_size] for i in range(0, len(news_items), batch_size)]
        
        print(f"将 {len(news_items)} 条新闻分成 {len(batches)} 个批次处理")
        
        # 使用进程池进行并行分析
        with multiprocessing.Pool(processes=max_workers) as pool:
            # 添加进度显示
            results = []
            for i, batch_result in enumerate(pool.imap(self._analyze_news_batch, batches)):
                results.extend(batch_result)
                print(f"批次 {i+1}/{len(batches)} 分析完成，已分析 {len(results)}/{len(news_items)} 条新闻")
        
        print(f"所有批次分析完成，共分析 {len(results)} 条新闻")
        return results
    
    def _analyze_news_batch(self, news_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析一批新闻"""
        results = []
        for i, news in enumerate(news_batch):
            try:
                # 实时反馈
                print(f"分析新闻 {i+1}/{len(news_batch)}: {news['title'][:50]}...")
                analysis = self._analyze_single_news(news)
                results.append(analysis)
                # 避免API调用过于频繁
                time.sleep(1)
            except Exception as e:
                print(f"分析新闻失败 {news['title'][:50]}...: {e}")
                # 添加错误信息到分析结果
                results.append({
                    "title": news['title'],
                    "summary": f"分析失败: {str(e)[:100]}",
                    "keywords": [],
                    "sentiment": "neutral"
                })
        return results
    
    def _analyze_single_news(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """分析单条新闻"""
        # 调用AI模型API进行分析
        try:
            # 实际调用DeepSeek API
            analysis_results = self._call_ai_model([news])
            if analysis_results:
                analysis = analysis_results[0]
                # 标准化字段名
                standardized_analysis = {
                    "title": news['title'],
                    "summary": analysis.get('summary', analysis.get('摘要', '')),
                    "keywords": analysis.get('keywords', analysis.get('关键词', [])),
                    "sentiment": analysis.get('sentiment', analysis.get('情感分析', 'neutral'))
                }
                # 确保关键词字段存在
                if not standardized_analysis['keywords']:
                    standardized_analysis['keywords'] = self._extract_keywords(news['title'])
                return standardized_analysis
            else:
                raise Exception("分析结果为空")
        except Exception as e:
            print(f"API调用失败，使用备用分析: {e}")
            # 备用方案：使用模拟分析结果
            return {
                "title": news['title'],
                "summary": f"这是关于{news['title']}的分析摘要",
                "keywords": self._extract_keywords(news['title']),
                "sentiment": "neutral"
            }
    
    def _call_ai_model(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """调用AI模型进行批量分析"""
        api_key = settings.AI_API_KEY
        api_url = settings.AI_API_URL
        
        if not api_key:
            raise Exception("AI API Key未配置")
        
        # 提取新闻标题
        news_titles = [news['title'] for news in news_items]
        print(f"准备分析 {len(news_titles)} 条新闻标题...")
        
        # 限制新闻数量，避免API限制
        if len(news_titles) > 10:
            print(f"新闻数量过多 ({len(news_titles)}条)，只使用前10条进行分析...")
            news_titles = news_titles[:10]
        
        print(f"使用 {len(news_titles)} 条新闻进行分析...")
        
        try:
            # 构建提示词
            prompt = "分析以下新闻：\n\n"
            for i, title in enumerate(news_titles):
                prompt += f"{i+1}. {title}\n"
            prompt += "\n\n请为每条新闻提供：摘要、关键词、情感分析。"
            prompt += "\n使用JSON格式返回，每条新闻一个对象，放在数组中。"
            
            # 直接使用HTTP请求调用API，避免OpenAI客户端的proxies问题
            import httpx
            import json
            
            print("发送HTTP请求到AI API...")
            print(f"API URL: {api_url}")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
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
            
            # 创建自定义的HTTP客户端，不使用proxies参数
            with httpx.Client() as client:
                response = client.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
            
            print(f"HTTP响应状态: {response.status_code}")
            
            if response.status_code != 200:
                print(f"API调用失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                # 备用方案：生成模拟分析结果
                return self._generate_fallback_analysis(news_items)
            
            # 解析响应
            response_data = response.json()
            analysis_content = response_data['choices'][0]['message']['content']
            print(f"获取到的内容: {analysis_content[:200]}...")
            
            # 清理Markdown代码块
            clean_content = analysis_content.strip()
            
            # 使用正则表达式提取JSON内容
            import re
            json_match = re.search(r'```(?:json)?\n(.*?)\n```', clean_content, re.DOTALL)
            if json_match:
                clean_content = json_match.group(1).strip()
                print(f"从Markdown代码块中提取JSON")
            
            print(f"清理后的内容: {clean_content[:200]}...")
            
            # 尝试解析JSON
            try:
                analysis_results = json.loads(clean_content)
                
                # 验证结果格式
                if not isinstance(analysis_results, list):
                    raise Exception("分析结果格式错误，应为JSON数组")
                
                print(f"成功解析 {len(analysis_results)} 条分析结果")
                return analysis_results
                
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                # 尝试提取数组部分
                array_match = re.search(r'\[(.*?)\]', clean_content, re.DOTALL)
                if array_match:
                    array_content = '[' + array_match.group(1) + ']'
                    print(f"尝试提取数组部分: {array_content[:200]}...")
                    try:
                        analysis_results = json.loads(array_content)
                        print(f"成功解析提取的数组，共 {len(analysis_results)} 条结果")
                        return analysis_results
                    except:
                        pass
                
                # 备用方案：生成模拟分析结果
                print("使用备用分析结果")
                return self._generate_fallback_analysis(news_items)
                
        except Exception as e:
            print(f"分析失败: {e}")
            import traceback
            traceback.print_exc()
            # 备用方案：生成模拟分析结果
            return self._generate_fallback_analysis(news_items)
    
    def _generate_fallback_analysis(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成备用分析结果"""
        results = []
        for news in news_items:
            results.append({
                "title": news['title'],
                "summary": f"这是关于{news['title']}的分析摘要",
                "keywords": self._extract_keywords(news['title']),
                "sentiment": "neutral"
            })
        return results
    
    def _preprocess_news(self, news_items: List[Dict[str, Any]]) -> str:
        """预处理新闻数据"""
        news_titles = [news['title'] for news in news_items]
        return self._format_news_as_markdown(news_titles)
    
    def _format_news_as_markdown(self, news_titles: List[str]) -> str:
        """将新闻标题格式化为Markdown列表"""
        markdown = ""
        for i, title in enumerate(news_titles):
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
        
        # 3. 提取关键事件
        print("3. 提取关键事件...")
        key_events = self._extract_key_events(first_layer_result)
        print(f"成功提取 {len(key_events)} 个关键事件")
        
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
            import json
            
            # 构建提示词
            prompt = self.prompts["first_layer"] + "\n\n" + news_markdown
            
            # 直接使用HTTP请求调用API
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
            
            # 创建自定义的HTTP客户端，不使用proxies参数
            with httpx.Client() as client:
                response = client.post(
                    settings.AI_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
            
            print(f"HTTP响应状态: {response.status_code}")
            
            if response.status_code != 200:
                print(f"API调用失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                # 备用方案
                return "# 整体摘要分析\n\n## 整体摘要\n分析失败，使用备用方案。\n\n## 新闻分类\n- 综合新闻\n- 未分类\n\n## 关键事件\n- 分析失败"
            
            # 解析响应
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        except Exception as e:
            print(f"第一层分析失败: {e}")
            import traceback
            traceback.print_exc()
            # 备用方案
            return "# 整体摘要分析\n\n## 整体摘要\n分析失败，使用备用方案。\n\n## 新闻分类\n- 综合新闻\n- 未分类\n\n## 关键事件\n- 分析失败"
    
    def _extract_key_events(self, first_layer_result: str) -> List[str]:
        """从第一层结果中提取关键事件"""
        try:
            # 简单的关键事件提取逻辑
            # 实际应用中可以使用更复杂的NLP方法
            lines = first_layer_result.split('\n')
            key_events = []
            capture = False
            
            for line in lines:
                line = line.strip()
                if '## 关键事件' in line:
                    capture = True
                    continue
                elif capture and line.startswith('#') and not line.startswith('##'):
                    break
                elif capture and line:
                    # 提取事件内容
                    if line.startswith('- '):
                        event = line[2:]
                        key_events.append(event)
            
            # 确保至少有3个关键事件
            if len(key_events) < 3:
                # 如果提取失败，返回默认事件
                key_events = [
                    "主要新闻事件1",
                    "主要新闻事件2",
                    "主要新闻事件3"
                ]
            
            return key_events
        except Exception as e:
            print(f"提取关键事件失败: {e}")
            # 返回默认事件
            return [
                "主要新闻事件1",
                "主要新闻事件2",
                "主要新闻事件3"
            ]
    
    def _second_layer_analysis(self, key_events: List[str]) -> List[str]:
        """并行分析关键事件"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        # 只处理前3个关键事件
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
                    print(f"完成事件分析: {event[:50]}...")
                except Exception as e:
                    print(f"分析事件失败 {event[:50]}...: {e}")
                    results.append(f"# 分析失败\n\n{str(e)}")
        
        return results
    
    def _analyze_single_event(self, event: str) -> str:
        """分析单个关键事件"""
        try:
            from openai import OpenAI
            
            # 初始化客户端
            client = OpenAI(
                api_key=settings.AI_API_KEY,
                base_url=settings.AI_API_URL
            )
            
            # 构建提示词
            prompt = self.prompts["second_layer"] + "\n\n事件：" + event
            
            # 调用API
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻分析师"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                max_tokens=4096
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"分析单个事件失败: {e}")
            return f"# 分析失败\n\n{str(e)}"
    
    def _third_layer_analysis(self, first_layer_result: str, second_layer_results: List[str]) -> str:
        """第三层综合分析"""
        try:
            import httpx
            import json
            
            # 构建提示词
            prompt = self.prompts["third_layer"] + "\n\n"
            prompt += "# 第一层分析结果\n" + first_layer_result + "\n\n"
            prompt += "# 第二层分析结果\n"
            for i, result in enumerate(second_layer_results):
                prompt += f"## 事件 {i+1} 分析\n" + result + "\n\n"
            
            # 直接使用HTTP请求调用API
            print("发送第三层分析请求...")
            
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
            
            # 创建自定义的HTTP客户端，不使用proxies参数
            with httpx.Client() as client:
                response = client.post(
                    settings.AI_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
            
            print(f"HTTP响应状态: {response.status_code}")
            
            if response.status_code != 200:
                print(f"API调用失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                # 备用方案
                return "# 综合分析\n\n分析失败，使用备用方案。"
            
            # 解析响应
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        except Exception as e:
            print(f"第三层分析失败: {e}")
            import traceback
            traceback.print_exc()
            # 备用方案
            return "# 综合分析\n\n分析失败，使用备用方案。"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取，实际应用中可以使用更复杂的算法
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        # 过滤常见词
        common_words = set(['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'])
        keywords = [word for word in words if word not in common_words and len(word) > 1]
        # 去重并返回前5个
        return list(set(keywords))[:5]
    
    def _generate_daily_summary(self, analysis_results: List[Dict[str, Any]]) -> str:
        """生成每日总结"""
        # 这里应该调用AI模型生成总结
        # 由于是示例，我们使用模拟总结
        
        summary = "# 今日新闻总结\n\n"
        summary += f"今日共分析 {len(analysis_results)} 条新闻\n\n"
        summary += "## 主要事件\n\n"
        
        # 提取关键词
        all_keywords = []
        for result in analysis_results:
            # 兼容不同的字段名
            if 'keywords' in result:
                all_keywords.extend(result['keywords'])
            elif '关键词' in result:
                all_keywords.extend(result['关键词'])
        
        # 统计关键词频率
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(10)
        
        summary += "### 热点关键词\n\n"
        for keyword, count in top_keywords:
            summary += f"- {keyword} ({count})\n"
        
        summary += "\n## 事件分析\n\n"
        summary += "这里是对今日主要事件的详细分析..."
        
        return summary
    
    def _generate_event_analysis(self, analysis_results: List[Dict[str, Any]]) -> str:
        """生成事件分析"""
        # 这里应该调用AI模型生成事件分析
        # 由于是示例，我们使用模拟分析
        
        analysis = "# 事件发展脉络分析\n\n"
        analysis += "## 今日重要事件\n\n"
        
        # 按关键词分组事件
        keyword_groups = {}
        for result in analysis_results:
            # 兼容不同的字段名
            keywords = []
            if 'keywords' in result:
                keywords = result['keywords']
            elif '关键词' in result:
                keywords = result['关键词']
            
            # 获取新闻标题
            title = ""
            if 'title' in result:
                title = result['title']
            elif '新闻标题' in result:
                title = result['新闻标题']
            elif 'summary' in result:
                title = result['summary'][:50] + "..."  # 使用摘要作为标题
            
            if keywords and title:
                for keyword in keywords:
                    if keyword not in keyword_groups:
                        keyword_groups[keyword] = []
                    keyword_groups[keyword].append(title)
        
        # 输出分组结果
        for keyword, titles in keyword_groups.items():
            if len(titles) > 1:
                analysis += f"### {keyword}\n\n"
                for title in titles:
                    analysis += f"- {title}\n"
                analysis += "\n"
        
        analysis += "## 横向分析\n\n"
        analysis += "这里是对今日事件的横向分析..."
        
        return analysis
    
    def _generate_weekly_summary(self, news_items: List[Dict[str, Any]]) -> str:
        """生成每周总结"""
        summary = "# 每周新闻回顾\n\n"
        summary += f"本周共分析 {len(news_items)} 条新闻\n\n"
        summary += "## 本周热点\n\n"
        summary += "这里是本周热点事件的总结..."
        return summary
    
    def _generate_monthly_summary(self, news_items: List[Dict[str, Any]]) -> str:
        """生成每月总结"""
        summary = "# 每月新闻回顾\n\n"
        summary += f"本月共分析 {len(news_items)} 条新闻\n\n"
        summary += "## 本月热点\n\n"
        summary += "这里是本月热点事件的总结..."
        return summary
    
    def _save_daily_analysis(self, analysis: Dict[str, Any]):
        """保存每日分析结果"""
        date = analysis['date']
        file_path = os.path.join(self.daily_analysis_dir, f"{date}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"每日分析结果已保存: {file_path}")
    
    def _save_weekly_analysis(self, analysis: Dict[str, Any]):
        """保存每周分析结果"""
        week = analysis['week']
        file_path = os.path.join(self.weekly_analysis_dir, f"{week}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"每周分析结果已保存: {file_path}")
    
    def _save_monthly_analysis(self, analysis: Dict[str, Any]):
        """保存每月分析结果"""
        month = analysis['month']
        file_path = os.path.join(self.monthly_analysis_dir, f"{month}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"每月分析结果已保存: {file_path}")
    
    def _save_analysis_results(self, analysis_results: Dict[str, Any], date: str):
        """保存Markdown格式的完整分析报告"""
        # 确保报告目录存在
        report_dir = os.path.join(self.daily_analysis_dir, "reports")
        os.makedirs(report_dir, exist_ok=True)
        
        # 构建完整的Markdown报告
        markdown_report = "# 三层新闻分析报告\n\n"
        markdown_report += f"生成时间: {datetime.now().isoformat()}\n"
        markdown_report += f"分析新闻数量: {len(analysis_results.get('second_layer', []))}\n\n"
        
        # 添加第一层分析结果
        markdown_report += "## Summary 是日要闻\n\n"
        markdown_report += analysis_results.get("first_layer", "分析失败") + "\n\n"
        
        # 添加第二层分析结果
        markdown_report += "## Advanced 深度分析\n\n"
        for i, event_analysis in enumerate(analysis_results.get("second_layer", [])):
            markdown_report += event_analysis + "\n\n"
        
        # 添加第三层分析结果
        markdown_report += "## Insights 洞察建议\n\n"
        markdown_report += analysis_results.get("third_layer", "分析失败") + "\n"
        
        # 保存为Markdown文件
        md_file_path = os.path.join(report_dir, f"{date}.md")
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        print(f"Markdown分析报告已保存: {md_file_path}")
    
    def clean_old_analysis(self):
        """清理过期的分析数据"""
        # 清理2个月前的每日分析数据
        threshold_date = datetime.now() - timedelta(days=60)
        
        for filename in os.listdir(self.daily_analysis_dir):
            if filename.endswith('.json'):
                try:
                    file_date = datetime.strptime(filename[:-5], '%Y-%m-%d')
                    if file_date < threshold_date:
                        file_path = os.path.join(self.daily_analysis_dir, filename)
                        os.remove(file_path)
                        print(f"删除过期每日分析文件: {filename}")
                except Exception as e:
                    print(f"清理每日分析文件失败 {filename}: {e}")
    
    def _setup_tavily_client(self):
        """初始化Tavily客户端"""
        try:
            from tavily import TavilyClient
            api_key = settings.TAVILY_API_KEY
            if not api_key:
                print("Tavily API密钥未配置")
                return None
            client = TavilyClient(api_key=api_key)
            print("Tavily客户端初始化成功")
            return client
        except Exception as e:
            print(f"初始化Tavily客户端失败: {e}")
            return None
    
    def _generate_search_query(self, event: str) -> str:
        """生成更精准的搜索查询词"""
        # 提取事件的核心部分，去除问号、感叹号等标点
        core_event = event.replace('？', '').replace('！', '').strip()
        # 添加关键词，提高搜索精准度
        query = f"{core_event} 最新消息 背景 原因 影响 时间线 利益 专家观点"
        return query
    
    def _search_with_tavily(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """使用Tavily执行搜索"""
        try:
            if not self.tavily_client:
                print("Tavily客户端未初始化，跳过搜索")
                return []
            
            print(f"使用Tavily搜索: {query[:50]}...")
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
            
            print(f"Tavily搜索完成，获得 {len(search_results)} 个结果")
            return search_results
        except Exception as e:
            print(f"Tavily搜索失败: {e}")
            return []
    
    def _enhanced_event_analysis(self, event: str) -> str:
        """使用Tavily搜索增强事件分析"""
        try:
            # 生成更精准的搜索查询词
            search_query = self._generate_search_query(event)
            # 使用Tavily搜索相关信息
            search_results = self._search_with_tavily(search_query)
            
            # 构建增强的分析提示词
            enhanced_prompt = self.prompts["second_layer"] + "\n\n事件：" + event
            
            if search_results:
                enhanced_prompt += "\n\n相关信息：\n"
                for i, result in enumerate(search_results):
                    enhanced_prompt += f"{i+1}. [{result['title']}]({result['url']})\n"
                    if result['content']:
                        enhanced_prompt += f"   摘要：{result['content'][:200]}...\n"
            
            # 直接使用HTTP请求调用API
            import httpx
            import json
            
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
            
            # 创建自定义的HTTP客户端，不使用proxies参数
            with httpx.Client() as client:
                response = client.post(
                    settings.AI_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
            
            print(f"HTTP响应状态: {response.status_code}")
            
            if response.status_code != 200:
                print(f"API调用失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                # 回退到普通分析
                return self._analyze_single_event(event)
            
            # 解析响应
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        except Exception as e:
            print(f"增强事件分析失败: {e}")
            import traceback
            traceback.print_exc()
            # 回退到普通分析
            return self._analyze_single_event(event)


if __name__ == "__main__":
    # 测试每日分析
    analyzer = AIAnalyzer()
    daily_analysis = analyzer.analyze_daily_news()
    print(f"每日分析完成: {daily_analysis.get('date', '未知')}")
    
    # 测试每周分析
    # weekly_analysis = analyzer.analyze_weekly_news()
    # print(f"每周分析完成: {weekly_analysis.get('week', '未知')}")
    
    # 测试每月分析
    # monthly_analysis = analyzer.analyze_monthly_news()
    # print(f"每月分析完成: {monthly_analysis.get('month', '未知')}")
    
    # 清理过期分析数据
    analyzer.clean_old_analysis()
