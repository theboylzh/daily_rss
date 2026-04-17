"""
V2.0.0 分阶段调试工具
支持单独测试每个阶段，无需等待完整流程
"""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from ai_analyzer_v2 import AIAnalyzerV2, parse_ai_json_response, validate_v2_structure, get_empty_structure


class StageDebugger:
    """V2 分阶段调试器"""

    def __init__(self):
        self.analyzer = AIAnalyzerV2()
        self.news_items = self._load_news()
        self.stage1_result = None
        self.stage2_result = None
        self.stage3_result = None
        self.stage4_result = None

    def _load_news(self, news_file: str = None) -> list:
        """加载新闻数据"""
        if news_file is None:
            # 自动查找最新的新闻文件
            news_dir = 'data/news'
            files = sorted([f for f in os.listdir(news_dir) if f.endswith('.json')])
            if files:
                news_file = os.path.join(news_dir, files[-1])
            else:
                print("❌ 未找到新闻文件")
                return []

        try:
            with open(news_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载新闻失败：{e}")
            return []

    def test_stage1(self, sample_size: int = 20):
        """单独测试阶段 1：概要生成"""
        print("\n" + "=" * 60)
        print("阶段 1：概要生成 - 单独测试")
        print("=" * 60)

        # 使用部分新闻测试（节省时间）
        test_news = self.news_items[:sample_size]
        print(f"\n使用 {len(test_news)} 条新闻进行测试...")

        # 准备 prompt
        news_text = self.analyzer._format_news_for_prompt(test_news)
        prompt = self.analyzer.prompts["stage1_summary"] + "\n\n新闻列表:\n" + news_text

        print(f"Prompt 长度：{len(prompt)} 字符")
        print("\n发送 AI 请求...")

        import httpx
        from config import settings

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.analyzer.api_key}"
        }

        payload = {
            "model": self.analyzer.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的新闻分析师"},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "max_tokens": 4096
        }

        try:
            with httpx.Client(trust_env=False) as client:
                response = client.post(
                    self.analyzer.api_url,
                    headers=headers,
                    json=payload,
                    timeout=settings.THIRD_LAYER_TIMEOUT
                )

            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                print(f"AI 响应长度：{len(content)}")

                # 解析结果
                result = parse_ai_json_response(content)
                self.stage1_result = result

                # 验证结构 - 阶段 1 只检查它负责的字段
                stage1_fields = ["summary", "key_news_brief", "briefing", "key_news_list"]
                has_stage1_fields = any(f in result for f in stage1_fields)

                if has_stage1_fields:
                    print("\n✅ 阶段 1 测试成功 - 生成了阶段 1 的字段")
                else:
                    print(f"\n⚠️ 阶段 1 测试完成 - 缺少阶段 1 字段")

                # 打印摘要
                print("\n--- 结果摘要 ---")
                print(f"one_liner: {result.get('summary', {}).get('one_liner', '缺失')}")
                print(f"digest: {result.get('summary', {}).get('digest', '缺失')[:50]}...")
                print(f"keywords: {result.get('summary', {}).get('keywords', [])}")
                print(f"key_news_brief: {len(result.get('key_news_brief', []))} 条")

                # 保存结果
                self._save_result(result, 'stage1_result.json')

                return result
            else:
                print(f"❌ API 请求失败：{response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 测试失败：{e}")
            return None

    def test_stage2(self, use_cache: bool = True):
        """单独测试阶段 2：观点生成（使用优化后的批量摘要）"""
        print("\n" + "=" * 60)
        print("阶段 2：观点生成 - 单独测试（批量摘要优化版）")
        print("=" * 60)

        # 检查是否有阶段 1 的结果
        if self.stage1_result is None:
            if use_cache and os.path.exists('stage1_result.json'):
                print("从缓存加载阶段 1 结果...")
                with open('stage1_result.json', 'r', encoding='utf-8') as f:
                    self.stage1_result = json.load(f)
            else:
                print("请先运行阶段 1 测试")
                return None

        key_news_list = self.stage1_result.get('key_news_list', [])
        if not key_news_list:
            print("❌ 阶段 1 结果中没有 key_news_list")
            return None

        print(f"\n使用 {len(key_news_list)} 条重点新闻生成观点...")

        # 直接调用 analyzer 的优化方法
        result = self.analyzer._stage2_perspectives(key_news_list)

        if result:
            self.stage2_result = result
            perspectives = result.get('perspectives', [])
            print(f"\n✅ 阶段 2 测试完成 - 生成 {len(perspectives)} 个观点")

            for i, p in enumerate(perspectives[:3], 1):
                print(f"  {i}. {p.get('title', '无标题')}")

            self._save_result(result, 'stage2_result.json')

        return result

    def test_stage3(self):
        """单独测试阶段 3：深度分析"""
        print("\n" + "=" * 60)
        print("阶段 3：深度分析 - 单独测试")
        print("=" * 60)

        # 检查是否有阶段 1 的结果
        if self.stage1_result is None:
            if os.path.exists('stage1_result.json'):
                print("从缓存加载阶段 1 结果...")
                with open('stage1_result.json', 'r', encoding='utf-8') as f:
                    self.stage1_result = json.load(f)
            else:
                print("请先运行阶段 1 测试")
                return None

        key_news_brief = self.stage1_result.get('key_news_brief', [])
        if not key_news_brief:
            print("❌ 阶段 1 结果中没有 key_news_brief")
            return None

        print(f"\n分析 {len(key_news_brief[:3])} 个关键事件...")

        deep_analyses = []
        for event in key_news_brief[:3]:
            analysis = self._analyze_single_event(event)
            if analysis:
                deep_analyses.append(analysis)

        result = {"deep_analysis": deep_analyses}
        self.stage3_result = result

        print(f"\n✅ 阶段 3 测试完成 - 生成 {len(deep_analyses)} 个分析")
        for i, a in enumerate(deep_analyses, 1):
            print(f"  {i}. [{a.get('tags', [])}] {a.get('title', '无标题')[:40]}...")

        self._save_result(result, 'stage3_result.json')
        return result

    def _analyze_single_event(self, event: dict):
        """分析单个事件"""
        prompt = self.analyzer.prompts["stage3_deep_analysis"] + "\n\n关键事件:\n"
        prompt += f"标题：{event.get('title', '未知')}\n"
        prompt += f"标签：{event.get('tags', [])}\n"

        result = self._call_ai_api(prompt)
        if result and "deep_analysis" in result:
            analyses = result.get("deep_analysis", [])
            if analyses:
                return analyses[0]
        return None

    def test_stage4(self):
        """单独测试阶段 4：建议生成"""
        print("\n" + "=" * 60)
        print("阶段 4：建议生成 - 单独测试")
        print("=" * 60)

        # 构建上下文
        context = self._build_context()
        if not context:
            print("❌ 缺少必要的上下文，请先运行前面阶段")
            return None

        prompt = self.analyzer.prompts["stage4_suggestions"] + "\n\n分析上下文:\n" + context
        print(f"Prompt 长度：{len(prompt)}")

        print("\n发送 AI 请求...")
        result = self._call_ai_api(prompt)

        if result:
            self.stage4_result = result
            suggestions = result.get('suggestions', {})
            print(f"\n✅ 阶段 4 测试完成")
            for key, value in suggestions.items():
                if isinstance(value, dict):
                    print(f"  {key}: {value.get('title', '无标题')}")

            self._save_result(result, 'stage4_result.json')

        return result

    def _build_context(self) -> str:
        """构建阶段 4 的上下文"""
        context = ""

        if self.stage1_result:
            context += "今日摘要:\n"
            s = self.stage1_result.get('summary', {})
            context += f"一句话：{s.get('one_liner', '')}\n"
            context += f"关键词：{s.get('keywords', [])}\n\n"

        if self.stage2_result:
            context += "观点:\n"
            for p in self.stage2_result.get('perspectives', [])[:2]:
                context += f"- {p.get('title', '')}\n"
            context += "\n"

        if self.stage3_result:
            context += "深度分析:\n"
            for a in self.stage3_result.get('deep_analysis', [])[:2]:
                context += f"- {a.get('title', '')}: {a.get('viewpoint', '')[:50]}...\n"

        return context

    def _call_ai_api(self, prompt: str, max_tokens: int = 4096) -> dict:
        """调用 AI API"""
        import httpx
        from config import settings

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.analyzer.api_key}"
        }

        payload = {
            "model": self.analyzer.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "max_tokens": max_tokens
        }

        try:
            with httpx.Client(trust_env=False) as client:
                response = client.post(
                    self.analyzer.api_url,
                    headers=headers,
                    json=payload,
                    timeout=settings.THIRD_LAYER_TIMEOUT
                )

            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                return parse_ai_json_response(content)
            else:
                print(f"API 请求失败：{response.status_code}")
                return None
        except Exception as e:
            print(f"API 调用失败：{e}")
            return None

    def _save_result(self, data: dict, filename: str):
        """保存结果到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到：{filename}")

    def run_all_stages(self):
        """按顺序运行所有阶段"""
        print("\n" + "=" * 60)
        print("按顺序运行所有阶段")
        print("=" * 60)

        self.test_stage1()
        if self.stage1_result:
            self.test_stage2()
        if self.stage2_result:
            self.test_stage3()

        # 阶段 4 可以在任何时候运行
        self.test_stage4()

        print("\n" + "=" * 60)
        print("所有阶段测试完成")
        print("=" * 60)


def main():
    """主函数"""
    debugger = StageDebugger()

    print("=" * 60)
    print("V2.0.0 分阶段调试工具")
    print("=" * 60)
    print("\n命令:")
    print("  1 - 测试阶段 1：概要生成")
    print("  2 - 测试阶段 2：观点生成")
    print("  3 - 测试阶段 3：深度分析")
    print("  4 - 测试阶段 4：建议生成")
    print("  all - 运行所有阶段")
    print("  q - 退出")

    while True:
        choice = input("\n请输入命令 [1/2/3/4/all/q]: ").strip()

        if choice == '1':
            debugger.test_stage1()
        elif choice == '2':
            debugger.test_stage2()
        elif choice == '3':
            debugger.test_stage3()
        elif choice == '4':
            debugger.test_stage4()
        elif choice == 'all':
            debugger.run_all_stages()
        elif choice == 'q':
            print("再见!")
            break
        else:
            print("无效命令，请重新输入")


if __name__ == "__main__":
    main()
