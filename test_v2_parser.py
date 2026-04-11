"""
V2.0.0 JSON 解析模块的单元测试
"""
import unittest
import json
from v2_parser import parse_ai_json_response, validate_v2_structure
from v2_schema import get_empty_structure


class TestV2Parser(unittest.TestCase):
    """测试 V2 JSON 解析器"""

    def test_direct_parse_success(self):
        """测试直接 JSON 解析成功"""
        valid_json = json.dumps({
            "summary": {
                "one_liner": "测试摘要",
                "digest": "测试内容",
                "keywords": ["科技", "创新", "发展"]
            },
            "key_news_brief": [],
            "briefing": {
                "politics": "",
                "economy": "",
                "industry": "",
                "tech": ""
            },
            "perspectives": [],
            "deep_analysis": [],
            "suggestions": {
                "thinking": {"title": "", "content": ""},
                "investment": {"title": "", "content": ""},
                "self_improvement": {"title": "", "content": ""},
                "opportunities_risks": {"title": "", "content": ""}
            }
        })

        result = parse_ai_json_response(valid_json)
        self.assertEqual(result["summary"]["one_liner"], "测试摘要")

    def test_markdown_json_block(self):
        """测试从 Markdown 代码块中提取 JSON"""
        markdown_text = """
好的，这是你要的 JSON 格式输出：

```json
{
  "summary": {
    "one_liner": "Markdown 测试",
    "digest": "从代码块中提取",
    "keywords": ["测试"]
  },
  "key_news_brief": [],
  "briefing": {"politics": "", "economy": "", "industry": "", "tech": ""},
  "perspectives": [],
  "deep_analysis": [],
  "suggestions": {
    "thinking": {"title": "", "content": ""},
    "investment": {"title": "", "content": ""},
    "self_improvement": {"title": "", "content": ""},
    "opportunities_risks": {"title": "", "content": ""}
  }
}
```

希望这个格式对你有帮助！
"""
        result = parse_ai_json_response(markdown_text)
        self.assertEqual(result["summary"]["one_liner"], "Markdown 测试")

    def test_plain_code_block(self):
        """测试从普通代码块（```）中提取 JSON"""
        text = """
```
{
  "summary": {"one_liner": "测试", "digest": "测试", "keywords": ["1"]},
  "key_news_brief": [],
  "briefing": {"politics": "", "economy": "", "industry": "", "tech": ""},
  "perspectives": [],
  "deep_analysis": [],
  "suggestions": {
    "thinking": {"title": "", "content": ""},
    "investment": {"title": "", "content": ""},
    "self_improvement": {"title": "", "content": ""},
    "opportunities_risks": {"title": "", "content": ""}
  }
}
```
"""
        result = parse_ai_json_response(text)
        self.assertEqual(result["summary"]["one_liner"], "测试")

    def test_json_with_chinese_text(self):
        """测试 JSON 前后有中文的情况"""
        text = """
好的，根据您的要求，我生成了以下的 JSON 格式输出：

{
  "summary": {
    "one_liner": "中文测试摘要，约二十字左右",
    "digest": "这是今日摘要，描述今天发生的重要事件。",
    "keywords": ["关键词一", "关键词二", "关键词三"]
  },
  "key_news_brief": [],
  "briefing": {"politics": "", "economy": "", "industry": "", "tech": ""},
  "perspectives": [],
  "deep_analysis": [],
  "suggestions": {
    "thinking": {"title": "", "content": ""},
    "investment": {"title": "", "content": ""},
    "self_improvement": {"title": "", "content": ""},
    "opportunities_risks": {"title": "", "content": ""}
  }
}

请您查阅，如有问题请随时告知。
"""
        result = parse_ai_json_response(text)
        self.assertEqual(result["summary"]["one_liner"], "中文测试摘要，约二十字左右")

    def test_fallback_to_empty_structure(self):
        """测试解析失败时返回空结构"""
        invalid_text = "这是一段完全无效的文本，没有任何 JSON 内容"
        result = parse_ai_json_response(invalid_text)
        self.assertEqual(result, get_empty_structure())

    def test_partial_json_extraction(self):
        """测试从混合文本中提取部分 JSON"""
        text = """
第一阶段分析完成：
{"summary": {"one_liner": "提取测试", "digest": "test", "keywords": ["1"]}}

然后还有一些其他文本内容
"""
        result = parse_ai_json_response(text)
        # 应该能提取到 JSON
        self.assertEqual(result["summary"]["one_liner"], "提取测试")

    def test_validate_structure_complete(self):
        """测试验证完整结构"""
        valid_data = {
            "summary": {"one_liner": "test", "digest": "test", "keywords": ["1"]},
            "key_news_brief": [],
            "briefing": {"politics": "", "economy": "", "industry": "", "tech": ""},
            "perspectives": [],
            "deep_analysis": [],
            "suggestions": {
                "thinking": {"title": "", "content": ""},
                "investment": {"title": "", "content": ""},
                "self_improvement": {"title": "", "content": ""},
                "opportunities_risks": {"title": "", "content": ""}
            }
        }

        is_valid, errors = validate_v2_structure(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_structure_missing_fields(self):
        """测试验证缺少字段的情况"""
        invalid_data = {
            "summary": {"one_liner": "test"},  # 缺少 digest 和 keywords
            "key_news_brief": [],
            # 缺少 briefing
            "perspectives": [],
            "deep_analysis": [],
            "suggestions": {}  # 缺少所有子字段
        }

        is_valid, errors = validate_v2_structure(invalid_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
